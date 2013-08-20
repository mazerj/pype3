#!/usr/bin/env pypenv
# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""
Sun Feb 16 15:07:54 2003 mazer
  pype file expander -- takes a data file and *E X P L O D E S* it into
  something that matlab might be able to read..

  This is intented to be a generic tool that works with ANY pype task

Thu Nov	 3 16:59:59 2005 mazer
  added dumping of PlexNet timestamp data

Sun May 21 08:22:08 2006 mazer
  Made matlabify a little more strict: varnames can ONLY contain
  [a-zA-Z0-9_]. Somehow some spaces snuck into some var names which
  broke p2m. Now anything illegal is replaced by a '_' and p2m.m
  should report the error more usefully!

Sun May 21 13:44:57 2006 mazer
  Added 'startat' support so you can convert from the middle of a
  file to the end. This is for appending new data...

Mon Jan 26 11:00:53 2009 mazer
  Optimizing writeVector() to use matlab's load function seems to
  roughly cut conversion times in half -- but all the improvement
  is really on the matlab side..

Thu Jan 29 14:05:22 2009 mazer
  more optimizing to use fread() in matlab and numeric.array.tostring()
  for fast python-side i/o

Fri Jan 30 10:59:42 2009 mazer
  updated to use single monster output file.. even fast, I think..

Tue May 10 10:23:19 2011 mazer
  removed PROFILE options -- matlab's the limiting factor, not python..

Wed May 11 13:14:31 2011 mazer
  got rid of Numeric dependency (numpy now)

"""
import sys, types, string, math, os
import numpy
from pype import *
from events import *
from pypedata import *
from tempfile import mkstemp
from pypedebug import keyboard

DEBUG=0
TMPVAR=0

def tmpvar():
	global TMPVAR
	TMPVAR = TMPVAR + 1
	return 'xpx%d' % TMPVAR


def printify(fp, vname, v):
	# convert a "value" into a matlab safe function
	if type(v) is types.IntType:
		# If it's an int, just use the integer
		fp.write("%s=%d;\n" % (vname, v))
	elif type(v) is types.FloatType:
		# If it's an float, just use the float
		fp.write("%s=%f;\n" % (vname, v))
	elif type(v) is types.ListType or type(v) is types.TupleType:
		if len(v) > 0:
			tv = tmpvar()
			for n in range(len(v)):
				printify(fp, '%s{%d}' % (tv, n+1), v[n])
			fp.write('%s=%s;\n' % (vname, tv))
			fp.write('clear %s;\n' % tv)
		else:
			fp.write('%s=[];\n' % vname)
	else:
		# Otherwise, treat like string (this works for strings and
		# lists.  Replaces single-quotes with double quotes to keep
		# strings intact, but this is NOT ROBUST -- ie, won't handle
		# escaped quotes!!
		s = '%s' % (v,)
		s = string.join(string.split(s, "'"), "''")
		# strip trailing \n's
		s = string.join(string.split(s, "\n"), "")
		s = "'%s'" % (s,)
		fp.write("%s=%s;\n" % (vname, s))

def matlabify(m):
	"""Convert pype/worksheet variable names to something matlab-safe"""
	# no leading underscores allowed
	if m[0] == '_':
		m = 'X' + m

	# replace '@' with INT (for internal)
	m = string.join(string.split(m, '@'), 'INT')

	# replace '*' with STAR(for internal)
	m = string.join(string.split(m, '*'), 'STAR')

	# This one's because Ben Hayden messed up.	Just delete
	# colons..
	m = string.join(string.split(m, ':'), '')

	# matlab wants [a-zA-Z0-9_] only in varnames -- so replace everything
	# else with '_'
	s = []
	for c in m:
		if c in string.letters+string.digits+'_':
			s.append(c)
		else:
			s.append('_')
	m = string.join(s, '')
	return m


def writeDict(fp, objname, name, dict):
	for k in dict.keys():
		# massage the pype dictionary name into a matlab safe
		# variable name -- replace leading underscores with 'X_'
		# and '@' with 'XX'
		m = matlabify(k)
		if type(dict[k]) is types.StringType:
			n = 0
		else:
			try:
				n = len(dict[k])
			except TypeError:
				n = 0
		if n == 0:
			# this is a string or other atomic type (int/float etc)
			printify(fp, '%s.%s.%s' % (objname, name, m), dict[k])
		else:
			# this is some sort of list..
			v = dict[k]
			for j in range(n):
				printify(fp, "%s.%s.%s{%d}" % \
						 (objname, name, m, j+1), v[j])

def writeVector(fp, objname, name, v, format):
	# Mon Jan 26 10:58:21 2009 mazer
	#  spent some time profile and trying to speed this up...  best was
	#  to use tempfile and matlab-load() instead of matlab-eval(). This
	#  fn is still the main cycle stealer for this module..
	#
	# Thu Jan 29 13:51:03 2009 mazer
	#  by writing vectors out as strings, the python code becomes
	#  significantly faster. more than factor of two I think..

	if v is None or len(v) == 0:
		fp.write("%s.%s=[];" % (objname, name))
	else:
		vs = numpy.array(v, numpy.float64)
		(fd, tmp) = mkstemp(prefix='px3')
		t = open(tmp,'w')
		t.write(vs.tostring())
		t.close()
		os.close(fd)

		fp.write("fid=fopen('%s','r');\n" % tmp)
		fp.write("%s.%s=fread(fid, 'float64');\n" % (objname, name))
		fp.write("fclose(fid);\n")
		if not DEBUG:
			fp.write("delete('%s');\n" % tmp)


def expandExtradata(fname, fp, extradata):
	for n in range(len(extradata)):
		printify(fp, "extradata{%d}.id" % (n+1),
				 extradata[n].id)
		for k in range(len(extradata[n].data)):
			printify(fp, "extradata{%d}.data{%d}" % (n+1, k+1), \
					 extradata[n].data[k])

def expandRecord(fname, fp, n, d, xd):
	objname = 'rec(%d)' % (n+1)
	d.compute()

	fp.write("%s.pype_recno=%d;\n" % (objname, n))
	fp.write("%s.taskname='%s';\n" % (objname, d.taskname))
	fp.write("%s.trialtime='%s';\n" % (objname, d.trialtime))
	fp.write("%s.result='%s';\n" % (objname, d.result))
	try:
		fp.write("%s.rt=%d;\n" % (objname, d.rt))
	except TypeError:
		fp.write("%s.rt='%s';\n" % (objname, d.rt))
	fp.write("%s.record_id=%d;\n" % (objname, d.rec[8]))

	if d.userparams:
		writeDict(fp, objname, 'userparams', d.userparams)
	writeDict(fp, objname, 'params', d.params)

	for n in range(len(d.rest)):
		vname = "%s.rest{%d}" % (objname, n+1)
		printify(fp, vname, d.rest[n])

    v = tmpvar()
    times = map(lambda e:e[0], d.events)
    events = map(lambda e:e[1], d.events)
    
    fp.write("%s.ev_t=%s;\n" % (objname, times, ))
    fp.write("%s=sprintf('%s');\n" % \
             (v, string.join(events, chr(1)),))
    fp.write("%s.ev_e=strread(%s,'%%s','delimiter',char(1));\n" % \
             (objname, v, ))
    fp.write("clear %s;\n" % (v,))

	try:
		v = d.spike_times
	except AttributeError:
		v = []
	writeVector(fp, objname, 'spike_times', v, '%d')

	try:
		v = d.photo_times
	except AttributeError:
		v = []
	writeVector(fp, objname, 'photo_times', v, '%d')

	try:
		v = d.realt
	except AttributeError:
		v = []
	writeVector(fp, objname, 'realt', v, '%d')

	try:
		v = d.eyet
	except AttributeError:
		v = []
	writeVector(fp, objname, 'eyet', v, '%d')

	try:
		v = d.rec[9]
	except IndexError:
		v = []
	writeVector(fp, objname, 'raw_photo', v, '%d')

	try:
		v = d.rec[10]
	except IndexError:
		v = []
	writeVector(fp, objname, 'raw_spike', v, '%d')


	# Thu Nov  3 16:59:55 2005 mazer
	# write PlexNet timestamps, if present.
	# note: 'times' is timestamp in ms re standard pype time
	#		'channels' is electrode #, starting with 0
	#		'units' is sorted unit # on this electrode, starting with 0
	#
	# Fri Jan 25 13:02:10 2008 mazer
	#	modified to work with both plexon and tdt data
	#
	# Wed Mar 21 17:34:25 2012 mazer
	#	next line was: if d.plex_times: which wasn't right..
	if (not d.plex_times is None) and len(d.plex_times) > 0:
		writeVector(fp, objname, 'plx_times', d.plex_times, '%d')
		writeVector(fp, objname, 'plx_channels', d.plex_channels, '%d')
		writeVector(fp, objname, 'plx_units', d.plex_units, '%d')
	elif len(d.rec) > 13:
		plist = d.rec[13]
		if plist is not None:
			times = []
			channels = []
			units = []
			for (t, c, u) in plist:
				times.append(t)
				channels.append(c)
				units.append(u)
			writeVector(fp, objname, 'plx_times', times, '%d')
			writeVector(fp, objname, 'plx_channels', channels, '%d')
			writeVector(fp, objname, 'plx_units', units, '%d')


	# handle analog data channels:
	for chn in range(0, 7):
		cname = 'c%d' % chn
		try:
			v = d.rec[11][chn]
		except IndexError:
			v = []
		writeVector(fp, objname, cname, v, '%d')

	try:
		v = d.eyex
	except AttributeError:
		v = []
	writeVector(fp, objname, 'eyex', v, '%d')

	try:
		v = d.eyey
	except AttributeError:
		v = []
	writeVector(fp, objname, 'eyey', v, '%d')

	# look for pupil data from eyelink, if any..
	try:
		v = d.rec[12]
	except IndexError:
		v = []
	writeVector(fp, objname, 'eyep', v, '%d')

	# new sample data (eyelink, iscan etc)
	try:
		v = d.rec[14]
	except IndexError:
		v = []
	writeVector(fp, objname, 'eyenew', v, '%d')

	fp.write("fprintf(2,'+');\n")


def expandFile(fname, outfile, startat=0, maxn=None):
	pf = PypeFile(fname, filter=None)

	recno = 0
	expanded = 0
	out = open(outfile, 'w')
	sys.stderr.write('expanding: ')
	sys.stderr.flush()
	n = 0
	while 1:
		d = pf.nth(recno)
		if d is None:
			break
		elif recno >= startat:
			expandRecord(fname, out, recno, d, pf.extradata)
			n = n + 1
			sys.stderr.write('.')
			sys.stderr.flush()
		else:
			sys.stderr.write('x')
			sys.stderr.flush()
		recno = recno + 1
		if maxn and (n > maxn):
			break	# n is max number of record to extract at a time..
	expandExtradata(fname, out, pf.extradata)
	out.close()
	pf.close()
	if recno > 0:
		sys.stderr.write('\n')

if __name__ == '__main__':
	n = 0								# starting trial number (0 for first)
	maxn = 0							# max number of trial to extract

	if len(sys.argv) < 3:
		sys.stderr.write("Usage: %s pypefile outfile [startat] [maxn]\n" %
						 sys.argv[0])
		sys.exit(1)

	if len(sys.argv) > 3:
		n = int(sys.argv[3])
	if len(sys.argv) > 4:
		maxn = int(sys.argv[4])

	expandFile(sys.argv[1], sys.argv[2], startat=n, maxn=maxn)
	sys.exit(0)
