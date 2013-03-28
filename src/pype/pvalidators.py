# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""Parameter tables with type validation

PMW (Python MegaWidgets) based parameter tables (aka worksheets)
for use by the pype GUI. Most of these functions are **INTERNAL**
only and should never be called directly, except by "power users"!

The exceptions are the *is_????* functions to be used as validators
for task worksheets.

Author -- James A. Mazer (james.mazer@yale.edu)

"""

"""Revision History

Mon Aug 14 13:46:27 2006 mazer

- Added field locking buttons ('X' to left of entry fields) to let
  user lock individual entries to avoid accidental changes.. For
  Jon Touryan... should work ok with runlock'ing, but I haven't
  tested it. Is anybody using runlock??

Fri Feb 13 11:15:35 2009 mazer

- changed load/save format to a human-readable (non-pickled) version
  change should be transparent - old pickle versions will get read
  and new text versions written from now on..

Wed Mar 11 11:08:19 2009 mazer

- when parameter tables are evaluated, added storage of the raw
  unevaluated string version of the var for future reference..

Sun May 31 15:13:23 2009 mazer

- changed load/save of param tables to use standard pythong ConfigParser
  object -- this makes it easier to have external programs generate
  params files..

Tue Dec 14 16:54:50 2010 mazer

- purged old pickle-based config file code

Fri Apr 29 11:41:42 2011 mazer

- added dictionary type (like tuple) to allow {'yes':1, 'no':0} type stuff..

"""


import types, string, re
import posixpath
import Pmw

import pype_aux


# these are made available for custom validation functions,
# so the user doesn't have to know how Pmw works (it's just
# too ugly/complicated for the average user & me).

VALID = Pmw.OK
INVALID = Pmw.PARTIAL

def is_dir(s, evaluate=None):
	"""Must be a directory.

	"""
	if posixpath.isdir(s):
		r = VALID
	else:
		r = INVALID
	if evaluate:
		return (r, s)
	return r

def is_file(s, evaluate=None):
	"""Must be name of an EXISTING file.

	"""
	if posixpath.exists(s):
		r = VALID
	else:
		r = INVALID
	if evaluate:
		return (r, s)
	return r

def is_newfile(s, evaluate=None):
	"""Must be name of NON-EXISTING file.

	"""
	if posixpath.exists(s):
		r = INVALID
	else:
		r = VALID
	if evaluate:
		return (r, s)
	return r

def is_any(s, evaluate=None):
	"""No type checking --> always returns true.

	"""
	r = VALID
	if evaluate:
		return (r, s)
	return r

def is_boolean(s, evaluate=None):
	"""Must be some sort of boolean flag.

	Try to do a bit of parsing:
		- 1,yes,on,true -> 1
		- 0,no,off,false -> 0

	Use pyesno() or something like that for drop down.

	"""
	try:
		x = string.lower(s)
		if (x == 'yes') or (x == 'on') or (x == 'true'):
			r = VALID
			i = 1
		elif (x == 'no') or (x == 'off') or (x == 'false'):
			r = VALID
			i = 1
		else:
			i = int(s)
			if (i == 0) or (i == 1):
				r = VALID
			else:
				i = 0
				r = INVALID
	except ValueError:
		i = 0
		r = INVALID
	if evaluate:
		return (r, i)
	return r

# alias for is_boolean:
is_bool = is_boolean

def is_int(s, evaluate=None):
	"""Must be simple integer (positive, negative or zero).

	"""

	try:
		i = int(s)
		r = VALID
	except ValueError:
		i = 0
		r = INVALID
	if evaluate:
		return (r, i)
	return r

def is_posint(s, evaluate=None):
	"""Must be positive (> 0) integer.

	"""
	try:
		i = int(s)
		if i > 0:
			r = VALID
		else:
			r = INVALID
	except ValueError:
		i = 0
		r = INVALID
	if evaluate:
		return (r, i)
	return r

def is_negint(s, evaluate=None):
	"""Must be negative (< 0) integer.

	"""
	try:
		i = int(s)
		if i > 0:
			r = VALID
		else:
			r = INVALID
	except ValueError:
		i = 0
		r = INVALID
	if evaluate:
		return (r, i)
	return r

def is_gteq_zero(s, evaluate=None):
	"""Must be greater than or equal to zero.

	"""

	try:
		i = int(s)
		if i >= 0:
			r = VALID
		else:
			r = INVALID
	except ValueError:
		i = 0
		r = INVALID
	if evaluate:
		return (r, i)
	return r

def is_lteq_zero(s, evaluate=None):
	"""Must be less than or equal to zero.

	"""

	try:
		i = int(s)
		if i <= 0:
			r = VALID
		else:
			r = INVALID
	except ValueError:
		i = 0
		r = INVALID
	if evaluate:
		return (r, i)
	return r

def is_rgb(s, evaluate=None):
	"""Must be a properly formed RGB color triple.

	Form should be (R,G,B) were R G and B are all
	in the range 0-255. Parens are required.

	Note: is_color is an alias for this fn

	"""
	l = None
	try:
		l = eval(s)
		if len(l) == 3 and \
			   (l[0] >= 0 and l[0] < 256) and \
			   (l[1] >= 0 and l[1] < 256) and \
			   (l[2] >= 0 and l[2] < 256):
			r = VALID
		elif len(l) == 1 and \
			 (l[0] >= 0 and l[0] < 256):
			r = VALID
			l = (l[0],l[0],l[0])
		else:
			r = INVALID
	except:
		r = INVALID
	if evaluate:
		return (r, l)
	return r

is_color = is_rgb

def is_rgba(s, evaluate=None):
	"""Must be proper RGBA tuple (RGB+alpha).

	Like is_color()/is_rgb(), but allows for alpha channel
	specification.
	"""
	l = None
	try:
		l = eval(s)
		if len(l) == 3 and \
		   (l[0] >= 0 and l[0] < 256) and (l[1] >= 0 and l[1] < 256) and \
		   (l[2] >= 0 and l[2] < 256):
			r = VALID
		elif len(l) == 4 and \
		   (l[0] >= 0 and l[0] < 256) and (l[1] >= 0 and l[1] < 256) and \
		   (l[2] >= 0 and l[2] < 256) and (l[3] >= 0 and l[3] < 256):
			r = VALID
		else:
			r = INVALID
	except:
		r = INVALID
	if evaluate:
		return (r, l)
	return r

def is_gray(s, evaluate=None):
	"""
	entry must be a valid 8-bit grayscale value (0-255)
	"""
	try:
		i = int(s)
		if (i >= 0) and (i <= 255):
			r = VALID
		else:
			i = 0
			r = INVALID
	except ValueError:
		i = 0
		r = INVALID
	if evaluate:
		return (r, i)
	return r

def is_float(s, evaluate=None):
	"""Must be a valid floating point number

	"""
	try:
		f = float(s)
		r = VALID
	except ValueError:
		f = 0.0
		r = INVALID
	if evaluate:
		return (r, f)
	return r

def is_percent(s, evaluate=None):
	"""Must be valid percentage (ie, float in range 0-1)
	(technically this is is_fraction!)

	"""
	try:
		f = float(s)
		if (f >= 0.0) and (f <= 1.0):
			r = VALID
		else:
			f = 0.0
			r = INVALID
	except ValueError:
		f = 0.0
		r = INVALID
	if evaluate:
		return (r, f)
	return r

def is_angle_degree(s, evaluate=None):
	"""Must be valid angle in degrees (ie, float in range 0-360)

	"""
	try:
		f = float(s)
		if (f >= 0.0) and (f <= 360.0):
			r = VALID
		else:
			f = 0.0
			r = INVALID
	except ValueError:
		f = 0.0
		r = INVALID
	if evaluate:
		return (r, f)
	return r

def is_param(s, evaluate=None):
	"""Is 'special parameter' string.

	See the param_expand function (pype_aux.py) for
	full documentation on the valid forms of special
	parameter strings.

	"""
	try:
		x = pype_aux.param_expand(s)
		if x is None:
			r = INVALID
		else:
			r = VALID
	except ValueError:
		x = 0.0
		r = INVALID
	if evaluate:
		return (r, x)
	return r

def is_iparam(s, evaluate=None):
	"""Like is_param, but integer values.

	"""
	try:
		x = pype_aux.param_expand(s)
		if x is None:
			r = INVALID
		else:
			r = VALID
	except ValueError:
		x = 0
		r = INVALID
	if evaluate:
		try:
			return (r, int(round(x)))
		except TypeError:
			return (INVALID, 0)
	return r

def is_cdf(s, evaluate=None):
	"""Must describe a cummulative distribution <-- NO REALLY, PDF...

	This ensures that the specified value is an integer or a vector
	describing a valid cummulative PDF.  If an integer, then return a
	n-length cdf of uniform prob (eg, [1/n, 1/n .. 1/n]) Otherwise,
	normalize the vector to have unity area.

	IMPROVED: 23-mar-2002 JM --> changed so you don't have
	to make stuff add to 1.0, evaluating divides by the
	sum to force it to add up to 1.0...

	"""
	try:
		i = int(s)
		if evaluate:
			val = []
			for n in range(i):
				val.append(1.0 / float(i))
		r = VALID
	except ValueError:
		try:
			i = eval(s)
			val = []
			if type(i) is types.ListType:
				sum = 0.0
				for f in i:
					sum = sum + float(f)
				for f in i:
					val.append(float(f) / sum)
			r = VALID
		except:
			val = 0
			r = INVALID
	if evaluate:
		return (r, val)
	return r

def toint(s):
	try:
		return int(s)
	except ValueError:
		return None

def is_pdf(s, evaluate=None):
	"""Probability density function.

	- If a list, then the list is normalized to sum=1.0 when retrieved.
	
	- If an integeer, then a uniform distribution of specified length
	  is used (ie, [1/n, 1/n .. 1/n]) is generated on retrieval

    - If of the form 'hazard(N)', where N is an integer

	"""
	import numpy as np
	
	try:
		i = int(s)
		if evaluate:
			val = []
			for n in range(i):
				val.append(1.0 / float(i))
		r = VALID
	except ValueError:
		# this re pulls out the argument for the hazard function
		hparse = re.compile('^hazard\(([0-9]+)\)$').split(s)
		if len(hparse) == 3 and not toint(hparse[1]) is None:
			val = np.exp(-np.arange(toint(hparse[1])))
			r = VALID
		else:
			try:
				i = eval(s)
				val = []
				if type(i) is types.ListType:
					sum = 0.0
					for f in i:
						sum = sum + float(f)
					for f in i:
						val.append(float(f) / sum)
				r = VALID
			except:
				val = 0
				r = INVALID
	if evaluate:
		return (r, val)
	return r

def is_list(s, evaluate=None):
	"""Must be a list/vector or range.

	Lists are specified in []'s. Ranges can be either:

		=start:stop:step (inclusive: both start and stop in list)

		start:stop:step  (stop is not included in the list)

	"""

	try:
		v = string.split(s, ':')
		if len(v) > 1:
			if s[0] == '=':
				inc = 1
				v = map(int, string.split(s[1:], ':'))
			else:
				v = map(int, string.split(s, ':'))
				inc = 0
			if len(v) < 3:
				stride = 1
			else:
				stride = v[2]
			r = VALID
			if inc:
				val = range(v[0], v[1]+1, stride);
			else:
				val = range(v[0], v[1], stride);
			if evaluate:
				return (r, val)
			return r
	except:
		pass

	try:
		val = eval(s)
		if type(val) == types.ListType:
			r = VALID
		else:
			r = INVALID
			val = []
	except:
		r = INVALID
		val = []

	if evaluate:
		return (r, val)

	return r

