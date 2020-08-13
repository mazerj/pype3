# -*- Mode: Python; tab-width:4 py-indent-offset:4 -*-

"""Classes for reading pype data files

Author -- James A. Mazer (mazerj@gmail.com)

"""

import sys
import types
import string
import os
import posix
import math
import time
import cPickle

from vectorops import *
from pype import *
import re

import numpy as np

try:
	import Numeric							# for legacy loads...
except ImportError:
	Numeric = None

def labeled_dump(label, obj, f, bin=0):
	"""Wrapper for cPickle.dump.

	Prepends ascii tag line and then dumps a pickled
	version of the object.
	"""
	f.write('<<<%s>>>\n' % label)
	cPickle.dump(obj, f, bin)

if Numeric is None:
	def labeled_load(f):
		"""Wrapper for cPickle.load.

		Inverse of labeled_dump().

		"""

		while 1:
			l = f.readline()
			if not l:
				return None, None
			if l.startswith('<<<') and l.endswith('>>>\n'):
				return l[3:-4], cPickle.load(f)
else:
	def labeled_load(f):
		"""Wrapper for cPickle.load.

		Inverse of labeled_dump(). This one works with old 32bit
		Numeric-based pypefiles, but requires Numeric be installed!

		"""

		def local_array_constructor(shape, typecode, thestr,
									Endian=Numeric.LittleEndian):

			# try to guess the word size on the machine that
			# pickled the data -- 'l' and 'f' are NATIVE types
			# and native word length is not available, so we have
			# to infer the native word length based on the actually
			# data block size and the indicated data block size.
			#
			# this is FRAGILE -- could break and only handles the
			# two cases I'm aware of -- in general, the better
			# solution is to never create Numeric arrays without
			# a complete type specification -- ie, use Float32
			# instead of Float -- and always pass in a typecode.

			if typecode == 'l':
				if Numeric.cumproduct(shape) * 4 == len(thestr):
					typecode = Numeric.Int32
				else:
					typecode = Numeric.Int64
			elif typecode == 'f':
				if Numeric.cumproduct(shape) * 4 == len(thestr):
					typecode = Numeric.Float32
				else:
					typecode = Numeric.Float64
			return ac(shape, typecode, thestr, Endian=Endian)

		try:
			ac = Numeric.array_constructor
			Numeric.array_constructor = local_array_constructor
			while 1:
				l = f.readline()
				if not l:
					return None, None
				if l.startswith('<<<') and l.endswith('>>>\n'):
					return l[3:-4], cPickle.load(f)
		finally:
			Numeric.array_constructor = ac



class PypedataTimeError(Exception):
	"""Serious bad voodoo in the datafile!

	This error gets raised when time seems to run
	backwards.	This represents a SERIOUS problem
	with the datafile...
	"""
	pass


def idfile(f):
	try:
		fp = open(f, 'r')
	except IOError:
		return None
	m1 = fp.read(1)
	m2 = fp.read(1)
	m3 = fp.read(1)
	fp.close()
	if len(m1) == 0:
		return 'empty'
	elif m1 == '<' and m2 == '<' and m3 == '<':
		return 'pype'
	elif m1 == 'n' and m2 == 'p' and m3 == 'f':
		return 'newpype'
	elif ord(m1) == 0xbe and ord(m2) == 0xef and ord(m3) == 0x08:
		return 'gz'
	elif ord(m1) == 0x42 and ord(m2) == 0x5a:
		return 'bz2'
	else:
		return ''

class Note(object):
	def __init__(self, rec):
		self.id = rec[1]
		self.data = rec[2:]

class PypeRecord(object):
	_reportcorrection = 1
	_reportchannel = 1
	def __init__(self, file, recnum, rec, taskname=None,
				 trialtime=None, parsed_trialtime=None,
				 userparams={},
				 tracker_guess=('iscan', 120, 24)):
		#
		# Wed Sep 11 14:36:42 2002 mazer
		#
		# this just cache's the record until it's really needed..
		#
		#  rec[0]		record type STRING: ('ENCODE' usually)
		#  rec[1]		info TUPLE: (trialresult, rt, paramdict, taskinfo)
		#						taskinfo can be ANYTHING user wants to
		#						save in the datafile
		#  rec[2]		event LIST: [(time, event), (time, event) ...]
		#  rec[3]		time VECTOR (list)
		#  rec[4]		eye x-pos VECTOR (list)
		#  rec[5]		eye y-pos VECTOR (list)
		#  rec[6]		LIST of photodiode time stamps
		#  rec[7]		LIST of spike time stamps
		#  rec[8]		record_id (SCALAR; auto incremented after each write)
		#  rec[9]		raw photodiode response VECTOR
		#  rec[10]		raw spike response VECTOR
		#  rec[11]		TUPLE of raw analog channel data
		#				(chns: 0,1,2,3,4,5,6), but 2 & 3 are same as
		#				rec[9] and rec[10], so they're just None's in
		#				this vector to save space. c5 and c6 aren't
		#				currently implemented
		#  rec[12]		pupil area data (if available) in same format
		#				as the eye [xy]-position data above. This is new
		#				as of 08-feb-2003 (JAM)
		#  rec[13]		on-line plexon data via PlexNet. This should be
		#				a list of (timestamp, unit) pairs, with timestamps
		#				in ms and unit's following the standard plexon
		#				naming scheme (01a, 02a, 02b etc..)
		#				(added: rec[13] 31-oct-2005 JAM)
		#  rec[14]		eyenew data (added: Fri Apr	 8 15:27:34 2011 mazer )

		self.file = file
		self.recnum = recnum
		self.rec = rec
		self.taskname = taskname
		self.trialtime = trialtime
		self.parsed_trialtime = parsed_trialtime
		self.userparams = userparams
		self.computed = None

		# these things are fast, the rest of the recording will
		# be filled in by the compute() method..
		# task specific data

		self.info = self.rec[1]

		# these should be standard..
		self.result = self.info[0]
		self.rt = self.info[1]
		self.params = self.info[2]
		if not 'eyetracker' in self.params.keys():
			self.params['eyetracker'] = tracker_guess[0]
			self.params['eyefreq'] = tracker_guess[1]
			self.params['eyelag'] = tracker_guess[2]

		# the rest of self.info is totally task dependent, see the
		# compute() method below
		self.rest = self.info[3:]

	def __repr__(self):
		return "<PypeRecord: r='%s'>" % self.result

	def printevents(self, fp=sys.stdout):
		lastt = None
		for (t, e) in self.events:
			if not lastt is None:
				dt = t - lastt
			else:
				dt = 0
			fp.write("	 %6dms\t(%6dms)\t%s\n" % (t, dt, e))
			lastt = t

	def pp(self, file=sys.stdout):
		self.debugprint(file=file)

	def debugprint(self, params=1, events=1, rest=1, spikes=1, syncs=1,
				   file=sys.stderr):
		file.write("================================\n")
		file.write("taskname='%s'\n	 %s\n" % (self.taskname,
											  type(self.taskname)))
		file.write("trialtime='%s'\n  %s\n" % (self.trialtime,
											   type(self.trialtime)))
		file.write("result='%s'\n  %s\n" % (self.result, type(self.result)))
		file.write("rt='%s'\n  %s\n" % (self.rt, type(self.rt)))

		if params:
			file.write("--------------------------------\n")
			klist = self.userparams.keys()
			klist.sort()
			for k in klist:
				file.write("userparams['%s']=<%s>\n	 %s\n" %
						   (k, self.userparams[k], type(self.userparams[k])))
			file.write("--------------------------------\n")
			klist = self.params.keys()
			klist.sort()
			for k in klist:
				file.write("params['%s']=<%s>\n	 %s\n" %
						   (k, self.params[k], type(self.params[k])))
		if rest:
			file.write("--------------------------------\n")
			file.write("rest=<%s>\n" % (self.rest,))
		if events:
			file.write("--------------------------------\n")
			file.write("events:\n")
			try:
				e = self.events
			except AttributeError:
				e = None
				file.write('  No events.\n');
			if e:
				self.printevents()
		if spikes:
			file.write("--------------------------------\n")
			file.write("spike_times:\n")
			try:
				st = self.spike_times
			except AttributeError:
				st = None
			if st:
				for t in st:
					file.write("   %8dms\n" % t)
			else:
				file.write("  No spikes.\n")

		if syncs:
			file.write("--------------------------------\n")
			file.write("photo_times:\n")
			try:
				pt = self.photo_times
			except AttributeError:
				pt = None
			if pt:
				for t in pt:
					file.write("   %8dms\n" % t)
			else:
				file.write("  No photo events.\n")

		file.write("================================\n")


	def compute(self, velocity=None, gaps=None, raw=None, nooffset=None):
		"""
		Note: All eye info is maintained here in PIXELS.
			  Use pix2deg() and deg2pix() below to convert.
		"""
		if not self.computed:
			# this is new 13-apr-2001:
			if 'eyelag' in self.params:
				lag = float(self.params['eyelag'])
			else:
				lag = 0

			# all pype files should have these (may be [] if not collected)

			#Tue Aug 20 16:08:29 2013 mazer
			# if an event 'name' is not a string, then assume it's a list
			# or tuple and expand on the fly into multiple events with
			# a shared timestamp -- this was originally done in by
			# p2m/pype_expander.py when generating matlab files, but this
			# is actually the correct place to do it..
			times = []
			events = []
			for (t, e) in self.rec[2]:
				if type(e) is types.StringType:
					times.append(t)
					events.append(e)
				else:
					for ee in e:
						times.append(t)
						events.append(ee)
			self.events = zip(times, events)


			self.eyet = np.array(self.rec[3], np.float) # ms
			self.realt = np.array(self.rec[3], np.float) # ms
			dt = diff(self.eyet)
			if sum(np.where(np.less(dt, 0), 1, 0)) > 0:
				raise PypedataTimeError
			self.eyex = np.array(self.rec[4], np.float) # dva
			self.eyey = np.array(self.rec[5], np.float) # dva

			if self.params['eyetracker'] == 'ISCAN':
				# Tue Jun  7 15:39:09 2011 mazer : NEW
				#  estimate eye tracker rate directly from data:
				#	one frame for sample&hold camera, one frame for
				#	framegrabber and one more frame because it seems
				#	correct (check with Rikki Razdan again??)

				# find points where x or y has changed
				dxy= (np.diff(self.eyex)!=0) & (np.diff(self.eyey)!=0)
				# compute sampling interval (si)
				si = np.median(diff(np.array(self.realt)[np.where(dxy)]))
				si = 1000.0 / (60.0 * np.round((1000.0 / si) / 60.0))
				lag = 3.0 * round(si)
				self.params['eyelag_user'] = lag
				self.params['eyelag'] = lag

			if lag > 0:
				# correct for eye tracker delay, if any..
				self.eyet = self.eyet - lag
				if PypeRecord._reportcorrection:
					# report this correction only ONCE!!
					sys.stderr.write('NOTE: fixing %.1f ms eye lag\n' % lag)
					PypeRecord._reportcorrection = None
			self.params['lagcorrected'] = 1
			self.eyevalid = None
			self.photo_times = np.array(self.rec[6], np.int)
			self.spike_times = np.array(self.rec[7], np.int)

			#Tue Jun  2 12:19:23 2009 mazer
			# Strip out false spikes generated by inaccurate TTL event
			# detection algorithm; this is also now done by p2mLoad to avoid
			# having to regenerate existing p2m files. Same thing for
			# photo_times...
			t = find_events(self.events, EYE_START)
			if len(t) > 0:
				if len(self.spike_times) and abs(self.spike_times[0] - t[0]) < 5:
					self.spike_times = self.spike_times[1::]
				if len(self.photo_times) and abs(self.photo_times[0] - t[0]) < 5:
					self.photo_times = self.photo_times[1::]

			if len(self.rec) > 13 and self.rec[13] is not None:
				plist = self.rec[13]
				times, channels, units, ids = [], [], [], []
				for (t, c, u) in plist:
					times.append(t)
					channels.append(c)
					units.append(u)
					ids.append("%03d%c" % (c, chr(ord('a')+u-1)))
				self.plex_times = np.array(times, np.int)
				self.plex_channels = np.array(channels, np.int)
				self.plex_units = np.array(units, np.int)
				self.plex_ids = ids[::]
			else:
				self.plex_times = None


			t = find_events(self.events, START)
			if len(t) == 0:
				sys.stderr.write('warning: no START event, guessing..\n')
				# just use the first event as a reference point...
				self.t0 = self.events[0][0]
			else:
				self.t0 = t[0]
			self.eyet = self.eyet - self.t0
			self.realt = self.realt - self.t0
			self.photo_times = self.photo_times - self.t0
			self.spike_times = self.spike_times - self.t0

			# Sun Dec  4 10:08:01 2005 mazer -- NOTE:
			# not necessary to align -- it's already been
			# done by the PlexNet.py module (START code is
			# same time as the TTL trigger/gate linegoing high and
			# all timestamps are stored in the data file relative to
			# that trigger event)
			#
			# self.plex_times = self.plex_times - self.t0

			self.events = align_events(self.events, self.t0)

			if gaps:
				gaps = np.nonzero(np.where(np.greater(dt, 1),
													 1,0))
				self.gaps_t = np.take(self.eyet, gaps)
				self.gaps_y = self.gaps_t * 0
				self.gapdurs = np.take(self.eyet, gaps+1) - self.gaps_t
			else:
				self.gaps_t = None
				self.gaps_y = None

			if raw and ('@eye_rot' in self.params):
				if self.params['@eye_rot'] != 0:
					self.israw = None
				else:
					if nooffset:
						self.eyex = self.eyex / self.params['@eye_xgain']
						self.eyey = self.eyey / self.params['@eye_ygain']
						self.israw = 1
					else:
						self.eyex = ((self.eyex + self.params['@eye_xoff']) /
									 self.params['@eye_xgain'])
						self.eyey = ((self.eyey + self.params['@eye_yoff']) /
									 self.params['@eye_ygain'])
						self.israw = 1
			else:
				self.israw = None

			if velocity:
				dt = dt / 1000.
				dx = diff(self.eyex) / dt
				dy = diff(self.eyey) / dt
				dxy = ((dx**2) + (dy**2))**0.5

				self.eyedxdt = dx
				self.eyedydt = dy
				self.eyedxydt = dxy
			else:
				self.eyedxdt = None
				self.eyedydt = None
				self.eyedxydt = None

			self.computed = 1

		return self

	def spikes(self, pattern=None):
		# select spikes from specified channel; channel is specified
		# in ~/.pyperc/spikechannel (users should use the 'pypespike'
		# sh script to select a channel)
		#	None --> TTL input (old style)
		#	regexp --> PlexNet datastream (001a, 001b, 002b etc..)
		import pype

		if pattern is None:
			try:
				pattern = string.strip(open(pype.pyperc('spikepattern'),
											'r').readline())
			except IOError:
				pattern = None

		if pattern is None or self.plex_times is None:
			ts = self.spike_times[::]
			pattern = 'TTL'
		else:
			p = re.compile(pattern)
			ts = []
			for n in range(len(self.plex_times)):
				if p.match(self.plex_ids[n]) is not None:
					ts.append(self.plex_times[n])

		if PypeRecord._reportchannel:
			sys.stderr.write('spikepattern=%s\n' % pattern)
			PypeRecord._reportchannel = None

		return pattern, ts

class PypeFile(object):
	def __init__(self, fname, filter=None, status=None, quiet=None):
		flist = fname.split('+')
		if len(flist) > 1:
			if flist[0][-3:] == '.gz':
				cmd = 'gunzip --quiet -c %s ' % string.join(flist,' ')
			else:
				cmd = 'cat %s ' % string.join(flist,' ')
			self.fp = posix.popen(cmd, 'r')
			if not quiet:
				sys.stderr.write('compositing: %s\n' % fname)
			self.fname = fname
		elif fname[-3:] == '.gz':
			# it appears MUCH faster to open a pipe to gunzip
			# than to use the zlib/gzip module..
			self.fp = posix.popen('gunzip --quiet <%s 2>/dev/null' % fname, 'r')
			if not quiet:
				sys.stderr.write('decompressing: %s\n' % fname)
			self.fname = fname[:-3]
			self.zfname = fname[::]
		elif not posixpath.exists(fname) and posixpath.exists(fname+'.gz'):
			# if .gz file exists and the named file does not,
			# try using the .gz file instead...
			self.fname = fname
			self.zfname = fname+'.gz'
			self.fp = posix.popen('gunzip --quiet <%s 2>/dev/null' %
								  self.zfname, 'r')
			if not quiet:
				sys.stderr.write('decompressing: %s\n' % self.zfname)
		else:
			self.fname = fname
			self.zfname = None
			self.fp = open(self.fname, 'r')
		self.cache = []
		self.status = status
		self.filter = filter
		self.userparams = None
		self.taskname = None
		self.extradata = []
		self.counter = 0

	def __repr__(self):
		return '<PypeFile:%s (%d recs)>' % (self.fname, len(self.cache))

	def _fatal_unpickle_error(self):
		exc_type, exc_value, exc_traceback = sys.exc_info()
		sys.stderr.write('Missing module <%s> during unpickling.\n' % exc_value)
		sys.stderr.write("""
	Find the original module and add it to your PYTHONPATH to access
	datafile. This usually means the missing module imported Numeric, so
	if you can't find the original, try making a dummmy file of the same
	name, on your path, containing the line:

	from Numeric import *

	""")

		sys.stderr.write('PYTHONPATH=%s\n' % os.environ['PYTHONPATH'])
		sys.stderr.write(get_traceback())
		sys.exit(1)



	def close(self):
		if not self.fp is None:
			try:
				self.fp.close()
			except IOError:
				# not sure why this happens, something sort of pipe
				# and thread interaction?
				pass
			self.fp = None

	def _next(self, cache=1, runinfo=None):
		if self.fp is None:
			return None

		trialtime = None
		while 1:
			try:
				label, rec = labeled_load(self.fp)
			except EOFError:
				label, rec = None, None
			except ImportError:
				# this is usually caused by pickling a data structure that
				# depends on Numeric
				self._fatal_unpickle_error()

			if label == None:
				self.close()
				return None
			if label == WARN:
				sys.stderr.write('WARNING: %s\n' % rec)
			if label == ANNOTATION:
				# for the moment, do nothing about this..
				pass
			elif rec[0] == ENCODE:
				try:
					xxx=trialtime2
				except UnboundLocalError:
					trialtime2 = 'nd'
				try:
					xxx=tracker_guess
				except UnboundLocalError:
					tracker_guess = ('unknown', -1, -1)
				p = PypeRecord(self, self.counter,
							   rec, trialtime=trialtime,
							   parsed_trialtime=trialtime2,
							   tracker_guess=tracker_guess,
							   userparams=self.userparams,
							   taskname=self.taskname)
				self.counter = self.counter + 1
				trialtime = None
				if (not self.filter) or (p.result == self.filter):
					if cache:
						self.cache.append(p)
				return p
			elif (rec[0] == 'NOTE' and rec[1] == 'task_is'):
				self.taskname = rec[2]
			elif (rec[0] == 'NOTE' and rec[1] == 'pype' and
				  rec[2] == 'run starts'):
				if runinfo:
					return 1
			elif (rec[0] == 'NOTE' and rec[1] == 'pype' and
				  rec[2] == 'run ends'):
				pass
			elif rec[0] == 'NOTE' and rec[1] == 'trialtime':
				(n, trialtime) = rec[2]
				# for some reason unclear to me, trialtime is an 'instance'
				# and not a string.. the % hack makes it into a string..
				trialtime = "%s" % trialtime
				# year, month, day, hour, min, sec, 1-7, 1-365, daylight sav?
				trialtime2 = time.strptime(trialtime, '%d-%b-%Y %H:%M:%S')
				# try to detect if this is an iscan file? Anything after
				# 01-jun-2000.	After 13-apr-2001, there should be an
				# eye tracker parameter stored in the datafile..
				# only do this on first record.
				year = trialtime2[0]
				month = trialtime2[1]
				if (year > 2000) or (year == 2000 and month >= 6):
					tracker_guess = ('iscan', 120, 24)
				else:
					tracker_guess = ('coil', 1000, 0)
			elif rec[0] == 'NOTE' and rec[1] == 'userparams':
				self.userparams = rec[2]
			else:
				#sys.stderr.write('stashed: <type=%s>\n' % label)
				self.extradata.append(Note(rec))

	def nth(self, n, free=1):
		"""Load or return (if cached) nth record."""
		while len(self.cache) <= n:
			if self._next() is None:
				return None
		rec = self.cache[n]
		if free:
			self.cache[n] = None
		return rec

	def freenth(self, n):
		if n < len(self.cache):
			self.cache[n] = None

	def last(self):
		"""Get last record."""
		while 1:
			d = self._next()
			if d is None: break
		return (self.cache[-1], len(self.cache)-1)

def count_spikes(spike_times, start, stop):
	n = 0
	for t in spike_times:
		if (t >= start) and (t < stop):
			n = n + 1
	return n

def extract_spikes(spike_times, start, stop, fromzero=None, offset=0):
	"""Pull out a subset of spikes -- the ones in the specified time window"""
	v = []
	for t in spike_times:
		if (t >= start) and (t < stop):
			if fromzero:
				v.append(t - start + offset)
			else:
				v.append(t)
	return v

def fixvel(d, start=None, stop=None, kn=2):
	"""
	Extract velocity trace from eye record data.  By default, this
	smooths the result with a simple running average kernel using
	the vectorops.smooth().
	"""

	if start is None:
		start = 0
	if stop is None:
		stop = len(d.eyet)
	dt = d.eyet[(start+1):stop] - d.eyet[start:(stop-1)]
	dx = d.eyex[(start+1):stop] - d.eyex[start:(stop-1)]
	dy = d.eyey[(start+1):stop] - d.eyey[start:(stop-1)]
	dxy = (dx**2 + dy ** 2) ** .5
	if kn:
		return start, stop, smooth_boxcar(dxy / dt, kn=kn)
	else:
		return start, stop, dxy / dt

def pix2deg(d, pix):
	"""Try to convert from pixels to degrees visual angle."""
	try:
		return float(pix) / float(d.params['mon_ppd'])
	except:
		return float(pix) / float(d.params['pix_per_dva'])

def deg2pix(d, deg):
	"""Try to convert from degrees visual angle to pixels."""
	try:
		return float(deg) * float(d.params['mon_ppd'])
	except:
		return float(deg) * float(d.params['pix_per_dva'])


def find_saccades(d, thresh=2, mindur=25, maxthresh=None):
	"""Find all saccades in a trial.

	This function is carefully hand tuned. The steps are as follows:

	- decimates eye signal back down to 120hz (iscan speed)

	- compute the velocity signal

	- smooth velocity with a running average (5pt)

	- find velocity spikes that exceed thresh

	- Two saccades within <mindur>ms are essentially considered to be
	  one noisy saccade and the second one is discarded::

		vel	 /\					  /\					 /\		  / ...
		 ___/  \_________________/	\___________________/  \_____/
			   <-------------------------------------->
			   |				|	|				  |
			   t0				t1	t2				  t3
									<-------------------------------
									|				  |	  |
									t0				  t1  t2

	- So, to compute a real fixation triggered PSTH, you allign allthe
	  rasters up on 't2' and only count spikes from t0-t3.

	- *Mon Oct 7 10:59:13 2002 mazer*

	- Added maxthresh -- if (vel > maxthresh), assume it's a blink and
	  don't put it in the list..

	- *Thu Apr 21 16:25:08 2011 mazer*

	- set things up so you can pass in (t, x, y, valid/None) instead
	  of pypedata object

	- cleaned up and added docs..

	:param d: (PypeData object OR (t, x, y, valid/None) tuple) Input
		data either in the form of a PypeData object or raw x,y,z,valid data
		stream. Valid is either none, or a boolean vector indicating the
		calibration validity of each datapoint in the time series.

	:param thresh: (pixs/120Hz-tick) Velocity threshold (applied after
		decimation to 120hz, therefore the /120Hz-tick units..).

	:param mindur: (ms; assumes input sampling rate is 1khz) Minimum
		allowable interval between saccades. Two"saccades" closer than mindur
		will be elided into a single saccade.

	:param maxthresh: (pix/120Hz-tick) Anything over this velocity is
		assumed to be a blink. If you don't specifiy a value, blinks are just
		ignored.

	:return: list of tuples (one for each saccade), where,

	   [ (t0,t1,t2,t3,t0i,t1i,t2i,t3i,fx,fy,fv,l_fx,l_fy,l_fv), ... ]

	   tN's are the times of the events shown in the diagram above,
	   while tNi's the indices of those events back into the d.eye[xyt]
	   arrays.

	   fx,fy are the mean x & y positions between t2-t3 and l_fx, l_fy
	   are the position of the last fixation.  fv and l_fv refer to the
	   calibration state of fx/fy and l_fx/l_fy respectively.  If fv is
	   TRUE, then this is a 'calibrated' fixation.	Which means inside
	   the calibration field, OR **NO** EYE CALIBRATION DATA WAS
	   SUPPLIED.

	"""

	if type(d) is types.TupleType:
		# set eyevalid to None if you're not using calibration info..
		(eyet, eyex, eyey, eyevalid) = d
	else:
		eyet = d.eyet
		eyex = d.eyex
		eyey = d.eyey
		eyevalid = d.eyevalid

	# decimate from actual FS down to 120hz (ie, 8ms sampling period)
	fs = mean(diff(eyet))				# estimate actual FS
	decimate_by = int(0.5 + (8.0 / fs))	# decimation factor

	if decimate > 1:
		t = decimate(eyet, decimate_by)
		x = decimate(eyex, decimate_by)
		y = decimate(eyey, decimate_by)
	else:
		t = eyet
		x = eyex
		y = eyey

	dx = x[1::] - x[0:-1:]
	dy = y[1::] - y[0:-1:]
	dt = t[1::] - t[0:-1:]

	dxy = ((dx**2 + dy ** 2) ** .5) / dt
	dxy = smooth_boxcar(dxy, 2)

	# t0[i] = start of last fixation
	# t1[i] = start of this saccade
	# t2[i] = start of this fixation (end this saccade)
	# t3[i] = start of next saccade
	#  tN is the time in ms, tNi is index into [txy]

	if maxthresh is None:
		# this will NEVER be exceeded..
		maxthresh = max(dxy) * 10

	# find a fixation to get started..
	realti = None
	for ix in range(0, len(dxy)):
		if dxy[ix] < thresh and dxy[ix] < maxthresh:
			realix = ix * decimate_by
			realti = t[ix]
			ix0 = ix
			break

	if realti is None:
		# no fixations found..
		return []

	IN_SACC = 1
	IN_FIX = 2

	SacList = [];
	t2 = realti
	t2i = realix
	state = IN_FIX
	fx, fy, fv, lfx, lfy, lfv, t0i = None, None, None, None, None, None, None

	for ix in range(ix0, len(dxy)):
		realix = ix * decimate_by
		realti = t[ix]
		if (state == IN_FIX) and (dxy[ix] > thresh) and (dxy[ix] < maxthresh):
			# we were in a fixation (or at start) and just entered a saccade
			t3 = realti
			t3i = realix
			if eyevalid:
				v = (sum(eyevalid[t2i:t3i]) == 0)
			else:
				v = 1
			(fx, fy, fv, lfx, lfy, lfv) = (mean(eyex[t2i:t3i]),
										   mean(eyey[t2i:t3i]), v, fx, fy, fv)
			if (not t0i is None) and t3-t2 > 0:
				SacList.append((t0,	 t1,  t2,  t3,
								t0i, t1i, t2i, t3i,
								fx, fy, fv, lfx, lfy, lfv))
			(t0, t1, t2, t3) = (t2, realti, None, None)
			(t0i, t1i, t2i, t3i) = (t2i, realix, None, None)
			state = IN_SACC
		elif (state == IN_SACC) and (dxy[ix] <= thresh):
			# make sure we're staying below thresh for a ~<mindur>ms
			skip = 0
			for i in range(1, int(0.5+float(mindur)/decimate_by)):
				j = ix + i
				if j < len(dxy) and dxy[j] > thresh and dxy[ix] < maxthresh:
					skip = 1
					break
			if not skip:
				# we were in a saccade and now in a stable fixation period
				t2 = realti
				t2i = realix
				state = IN_FIX

	# try to catch that last saccade that ran out..
	if (state == IN_FIX) and (dxy[ix] <= thresh):
		t3 = realti
		t3i = realix
		if (not t0i is None) and t3-t2 > 0:
			SacList.append((t0,	 t1,  t2,  t3,
							t0i, t1i, t2i, t3i,
							fx, fy, fv, lfx, lfy, lfv))

	return SacList


def findfix(d, thresh=2, dur=50, anneal=10, start=None, stop=None):
	"""
	Find fixation periods in trial. Threshold is velocity (pix/ms)
	below which will be called a fixation, if it's maintained for
	more than dur ms.  Fixations separated by gaps of less than
	anneal ms will be merged together to form single fixation
	events.

	NOTE: start and stop are index values, NOT TIMES!

	Returns list of tuples::

	  [
	   (start_ix, stop_ix, start_ms, stop_ms, mean_xpos, mean_ypos),
	   (start_ix, stop_ix, start_ms, stop_ms, mean_xpos, mean_ypos),
	   .......
	   (start_ix, stop_ix, start_ms, stop_ms, mean_xpos, mean_ypos)
	  ]

	Note: 100 deg/sec -> 1800pix/sec -> 1.8pix/ms

	"""

	# calculate v (velocity profile from XY position)
	start, stop, v = fixvel(d, start=start, stop=stop)

	fix_ix = []
	infix = 0
	for i in range(0, len(v)):
		if (not d.eyevalid is None) and (not d.eyevalid[i]):
			# outside valid calibration range -- discard completely
			infix = 0
		elif (not infix) and (v[i] <= thresh):
			infix = 1
			fstart = start + i
		elif infix and ((v[i] > thresh) or i == (len(v)-1)):
			infix = 0
			fstop = start + i - 1
			if (d.eyet[fstop]-d.eyet[fstart]) > dur:
				fix_ix.append(fstart)
				fix_ix.append(fstop)

	if len(fix_ix) > 2:
		merged = fix_ix[:1]
		for i in range(2, len(fix_ix), 2):
			if d.eyet[fix_ix[i]] - d.eyet[fix_ix[i-1]] > anneal:
				merged.append(fix_ix[i-1])
				merged.append(fix_ix[i])
		merged.append(fix_ix[-1])
		fix_ix = merged

	fixations = []
	for i in range(0, len(fix_ix), 2):
		a = fix_ix[i]
		b = fix_ix[i+1]
		xp = np.sum(d.eyex[a:b]) / float(len(d.eyex[a:b]))
		yp = np.sum(d.eyey[a:b]) / float(len(d.eyey[a:b]))
		fixations.append((a, b, d.eyet[a], d.eyet[b], xp, yp))

	return fixations

def find_events(events, event):
	"""Returns a list of event times which match pattern.

	See find_events2() to get list of the actual (time, event) pairs.

	:param events: (list) list of encode pairs ((time, event),...)

	:param event: (string) event name to match

	:return: (list) list of matching event **times**

	"""
	try:
		# zip(*x) is 'unzip'; see python function docs..
		return list(zip(*find_events2(events, event))[0])
	except IndexError:
		return []						# no matching events

def find_events2(events, event):
	"""Returns a list of actual events (pairs) which match pattern.

	:param events: (list) list of encode pairs ((time, event),...)

	:param event: (string) event name to match

	:return: (list) list of matching event **pairs**

	"""
	if event[-1] == '*':
		event = event[0:-1]
		chop = len(event)
	else:
		chop = -1

	elist = []
	for (t, e) in events:
		e0 = e
		if chop > 0: e = e[:chop]
		if e == event:
			elist.append((t, e0))
	return elist

def align_events(events, t0):
	"""Align an event list to a new time.

	:param events: (list) list of encode pairs ((time, event),...)

	:return: (list) 're-aligned' event list

	"""

	new_events = []
	for (t, e) in events:
		new_events.append(((t - t0), e))
	return new_events

def pp_encode(e):
	"""Pretty-print an event list.

	:param e: (list) list of encoded events

	:return: (string) printable version of event list

	"""
	s = ''
	for t, c in e:
		if s is '':
			s = '%10d %10d %s\n' % (-1, t, c)
		else:
			s = s + '%10d %10d %s\n' % (t-lastt, t, c)
		lastt = t
	return s

if __name__ == '__main__':
	v = PypeFile(sys.argv[1])
	v.last()
