# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""Auxiliary functions

Supplemental frequently used function -- either in pype code directly
or in user-tasks.

Author -- James A. Mazer (james.mazer@yale.edu)

"""

"""Revision History

Wed Apr	 8 21:42:18 1998 mazer

- created

Mon Jan 24 23:15:29 2000 mazer

- added tic/toc functions

Sun Nov	 6 13:06:34 2005 mazer

- added stat:stop:step slice syntax to param_expand

Wed Jul	 5 16:16:19 2006 mazer

- added =start:stop:step for inclusive ranges

Thu Jan	 7 17:22:10 2010 mazer

- hacked labeled_load to override the Numeric array constructor
  function to allow loading 32bit data files on 64bit machines.

- moved labeled_* to pypedata
"""

import random
import sys
import time
import posixpath
import os
import re
import string
import numpy as np

_tic = None

def tic():
	"""Start timer.

	Benchmark function: start a simple timer (like matlab tic/toc)

	"""
	global _tic
	_tic = time.time()

def toc(label=None):
	"""Stop/lap timer (and perhaps print value).

	Benchmark function: stop & print simple timer (like matlab tic/toc)

	"""
	global _tic
	if label:
		sys.stderr.write(label)
	if _tic:
		t = time.time()-_tic
		sys.stderr.write("%f secs" % t)
		return t
	else:
		return None

def nextfile(s):
	"""Next available file in sequence.

	:return: next available file from pattern. For example,
		nextfile('foo.%04d.dat') will return 'foo.0000.dat', then
		'foo.0001.dat' etc..

	"""
	n = 0
	while 1:
		fname = s % n
		if not posixpath.exists(fname):
			return fname
		n = n + 1

def lastfile(s):
	"""Last existing file in sequence.

	:return: last opened file from pattern (like nextfile, but returns
		the last existing file in the sequence).

	"""
	n = 0
	f = None
	while 1:
		fname = s % n
		if not posixpath.exists(fname):
			return f
		f = fname
		n = n + 1

class Timestamp(object):
	def __init__(self, dateonly=None, sortable=None):
		months = ['Jan', 'Feb', 'Mar', 'Apr', 'May',
				  'Jun', 'Jul', 'Aug', 'Sep', 'Oct',
				  'Nov', 'Dec' ]
		(self.y, self.mon, self.d, self.h, self.min, self.s,
		 x1, x2, x3) = time.localtime(time.time())
		self.monstr = months[self.mon - 1]
		self.sortable = sortable
		self.dateonly = dateonly

	def __repr__(self):
		if self.sortable:
			s = "%04d-%02d-%02d" % (self.y, self.mon, self.d)
		else:
			s = "%02d-%s-%04d" % (self.d, self.monstr, self.y)
		if not self.dateonly:
			s = "%s %02d:%02d:%02d" % (s, self.h, self.min, self.s)
		return s

class Logfile(object):
	def __init__(self, filename, autodate=None, autonum=None):
		if filename:
			if autodate:
				filename = "%s.%s" % (filename,
									  Timestamp(dateonly=1, sortable=1))
			if autonum:
				n = 0
				while 1:
					f = "%s.%03d" % (filename, n)
					if not posixpath.exists(f):
						filename = f
						break
					n = n + 1
		self.filename = filename
		self.write("")

	def write(self, line):
		if self.filename:
			f = open(self.filename, "a")
			f.write(line)
			f.close()

def frange(start, stop, step, inclusive=None):
	"""Floating point version of range().

	"""
	r = []
	if inclusive:
		stop = stop + step
	while start < stop:
		r.append(start)
		start = start + step
	return r

def vrandint(center, pvar):
	"""Random variable generator.

	Generate a uniformly distributed random
	number in range [center-var, center+var].

	"""
	return random.randint(center - (pvar * center), center + (pvar * center))

def pickints(lo, hi, n):
	"""Pick n integers.

	Select n random integers in the range [lo,hi].

	"""
	if (n > (hi - lo + 1)):
		n = hi - lo + 1
	l = []
	for i in range(0, n):
		while 1:
			i = random.randint(lo, hi)
			if l.count(i) == 0:
				l.append(i)
				break
	return l

def urand(min=0, max=1.0, integer=None):
	"""Generate uniformly distributed random numbers (was uniform())

	:param min,max: (float) specifies bounds on range

	:param integer: (boolean) if true, only return integers

	:return: (int | float) random number in specified range

	"""
	v = min + (max - min) * random.random()
	if integer:
		return int(round(v))
	return v

def nrand(mean=0, sigma=1.0, integer=None):
	"""Generate normally (Gaussian) distributed random numbers.

	:param mean, sigma: (float) specifies normal/Gaussian dist params

	:param integer: (boolean) if true, only return integers

	:return: (int | float) random number in specified range

	"""
	v = random.normalvariate(mean, sigma)
	if integer:
		return int(round(v))
	return v

def from_discrete_dist(v):
	"""Generate random numbers from a discrete distribution.

	Assume v represents somethine like a probability density
	function, with each scalar in v representing the prob. of
	that index, choose an index from that distribution.	 Note,
	the sum(v) MUST equal 1!!!

	*NB* Returned values start from 0, i.e. for v=[0.5, 0.5] possible
	return values are 0 or 1, with 50/50 chance..

	:param v: (array) frequency distribution

	:return: (int) index into distribution

	"""

	# compute cummulative density function
	u = urand(0.0, 1.0)
	pcumm = 0.0
	ix = 0
	for i in range(0, len(v)):
		pcumm = pcumm + v[i]
		if u < pcumm:
			return i
	return None

def _fuzzynums(mean, plus, minus=None, integer=None):
	"""Generate random number between around mean +/- plus/minus.

	This means [mean-minus, mean+plus], distribution is
	flat/uniform.

	"""
	if integer:
		return int(round(_fuzzynums(mean, plus, minus, integer=None)))
	else:
		if minus is None:
			minus = plus
		return urand(mean - minus, mean + plus)

def permute(v):
	"""Return a random permutation of the input vector.

	:param v: (array) input vector

	:return: randomly permuted version of v

	"""
	l = range(0,len(v))
	out = []
	while len(l) > 0:
		ix = random.randint(0, len(l)-1)
		out.append(v[l[ix]])
		del l[ix]
	return out

def pick_one(v, available=None):
	"""Pick on element from a vector.

	Tue Jan 7 19:15:43 2003 mazer: This used to return a random
	element of vector, when available==None, but that was inconsistent
	with the other junk in this file.  Now it always returns an INDEX
	(small int).

	:param v: (array) vector of elements to select from

	:param available: (boolean vector) -- mask specifying which
		elements are actually available for selection. This can be
		used to mask out stimuli that have already been presented etc.

	:return: (int) index of selected element in v

	"""


	if available is None:
		return random.randint(0, len(v)-1)
	else:
		i = random.randint(0, len(v)-1)
		j = i;
		while not available[i]:
			i = (i + 1) % len(v)
			if j == i:
				return None
		return i

def navailable(available):
	"""Count number of available slots; see pick_one()

	:param available: (boolean vector) see pick_one()

	:return: (int) number of available (non-zero) elements in list

	"""
	n = 0;
	for i in range(0, len(available)):
		if available[i]:
			n = n + 1
	return n

def pick_n(v, n):
	"""Randomly pick n-elements from vector.

	Pick elements **without replacement** from vector.

	:param v: (array) input vector

	:param n: (int) number of elements to pick

	:return: (array) vector length N containing indices of all
		selected elements.

	"""
	if n > len(v):
		raise ValueError, 'pick_n from short v'
	v = permute(v)
	return v[0:n]

def pick_n_replace(v, n):
	"""Randomly pick n-elements from vector

	Pick elements **with replacement** from vector.

	*NB* 11-Jul-2005: changed this back to replace returning the
	selected elements, not the indicies; returning indicies is
	incompatible with pick_n() and broke zvs10.py ...

	:param v: (array) input vector

	:param n: (int) number elements to pick

	:return: (array) vector length N containing selected elements.

	"""

	v = []
	for i in range(0, n):
		v.append(vector[pick_one(vector)])
	return v

def param_expand(s, integer=None):
	"""Expand pype *parameter* string.

	Allowed formats for parameter string (see ptable.py):

	* X+-Y -- uniform dist'd number: [X-Y, X+Y]

	* X+-Y% -- uniform dist'd number: [X-(X*Y/100), X+(X*Y/100)]

	* U[min,max] -- uniform dist'd number between min and max

	* N[mu,sigma] -- normally dist'd number from N(mu, sigma)

	* G[mu,sigma] -- same as N (Gaussian)

	* E[mu] -- exponential of mean mu

	* TE[mu,{max | min,max}] -- exponential of mean mu; values are constrained
	  to be within min:max (by resampling). If only max is specified, min
	  is assumed to be zero

	* ITE[mu,{max | min,max}] -- integer exponential -- like TE[], but
	  discretized to integer values

	* EDC[mu,min,max,nbins] -- discrete exponential of mean mu, contrained
	  to min:max (by resampling). 'nbins' specifies number of discrete points
	  in distribution (edc = exponential dirac comb)

	* start:step[:stride] -- generate non-inclusive range (python
	  style) and pick one at random (default stride is 1)

	* =start:step[:stride] -- generate inclusive range (matlab
	  style) and pick one at random (default stride is 1)

	* [#,#,#,#] -- pick one of these numbers

	* X -- just X

	:param s: (string) parameter specification string

	:param integer: (boolean) if true, return nearest integer

	:return: (float or int) number from specified distirbution

	"""

	if integer:
		return int(round(param_expand(s, integer=None)))

	s = string.strip(s)
	if len(s) < 1:
		return None

	if s.lower().startswith('n'):
		try:
			(mu, sigma) = eval(s[1:])
			return np.random.normal(mu, sigma)
		except:
			# should be 'except NameError:' but that doesn't properly
			# handle unmatched brackets... same below
			pass

	if s.lower().startswith('u'):
		try:
			(lo, hi) = eval(s[1:])
			return np.random.uniform(lo, hi)
		except:
			pass

	if s.lower().startswith('e'):
		try:
			(mu,) = eval(s[1:])
			return np.random.exponential(mu)
		except:
			pass

	if s.lower().startswith('te') or s.lower().startswith('ite'):
		try:
			# ite/te[mu,max] or ite/te[mu,min,max]
			if s[0] in 'iI':
				arg = s[3:]
			else:
				arg = s[2:]
			v = eval(arg)
			if len(v) == 2:
				meanval, minval, maxval = v[0], 0.0, v[1]
			else:
				meanval, minval, maxval = v[0], v[1], v[2]

			print meanval, minval, maxval

			while 1:
				# keep drawing until we get a range-valid value
				# before 12/18/2012 draw was clipped with min/max
				x = np.random.exponential(meanval)
				if s.lower()[0] == 'i':
                    #  shift by +0.5 then -1 to to avoid problems with the
                    #  bin from -0.5-0.5 being only half full due to exp>0
                    x = int(round(x+0.5)-1)
				if x >= minval and x <= maxval:
					return x
		except:
			pass

	if s.lower().startswith('edc'):
		try:
			# edc[mu,min,max,nbins] (ACM's exponential dirac comb)
			v = eval(s[3:])
			meanval, minval, maxval, nbins = v[0], v[1], v[2], v[3]

			if meanval < minval or meanval > maxval:
				return None

			# search for a value until it falls within the specified range
			while 1:
				val = np.random.exponential(meanval)
				if val >= minval and val <= maxval:
					binedges = np.linspace(minval,maxval,nbins+1)
					bincenters = binedges[0:-1] + (binedges[1]-binedges[0])/2
					val = val-bincenters[0]-1
					divisor = (bincenters[-1]-(bincenters[0]-1))/nbins
					val = int((round(val/divisor))*divisor)+(bincenters[0]-1)
					return val
		except:
			pass




	if s[0] == '[' and s[-1] == ']':
		# list syntax: pick one from [#,#,#,#]
		l = map(float, s[1:-1].split(','))
		return l[pick_one(l)]

	# if 'slice' syntax is used, generate the slice using range
	# and pick one element randomly. e.g., '1:10:2' would pick
	# 1, 3, 5, 7 or 9 with equal prob.
	if s[0] == '=':
		inc = 1
		l = string.split(s[1:], ':')
	else:
		inc = 0
		l = string.split(s, ':')
	if len(l) > 1:
		if len(l) == 3:
			start, stop, step = map(float, l)
		elif len(l) == 2:
			start, stop = map(float, l)
			step = 1.0
		if inc:
			l = np.arange(start, stop+step, step)
		else:
			l = np.arange(start, stop, step)
		return l[pick_one(l)]

	l = re.split('\+\-', s)
	if len(l) == 2:
		a = float(l[0])
		if len(l[1]) > 0 and l[1][-1] == '%':
			b = float(l[1][0:-1]) / 100.0
			b = a * b
		else:
			b = float(l[1])
		return _fuzzynums(a, b)

	return float(s)

def showparams(app, P, clearfirst=1):
	"""Pretty-print a parameter table into the info window.

	See info() function.

	:param app: (PypeApp) appliation handle

	:param P: parameter dictionary

	:return: nothing

	"""
	if clearfirst:
		info(app)
	keys = P.keys()
	keys.sort()
	n = 0
	while n < len(keys):
		s = ''
		while n < len(keys) and len(s) < 25:
			s = s + "%12s: %-10s" % (keys[n], P[keys[n]])
			n = n + 1
		info(app, s)

def dir2ori(dir):
	"""Convert stimulus DIRECTION to an ORIENTATION.

	"""
	ori = (-dir + 90.0)
	if ori < 0:
		ori = ori + 360.
	return ori

if __name__ == '__main__':
	sys.stderr.write('%s should never be loaded as main.\n' % __file__)
	sys.exit(1)
