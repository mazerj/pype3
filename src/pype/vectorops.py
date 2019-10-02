# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""Simple vector operations

Implements a bunch of common but useful vector operations using
Numeric (if possible). If Numeric's not available, tries to fall
back to (slower) raw-python.

Author -- James A. Mazer (mazerj@gmail.com)

"""

import numpy as np

# take these direction from numpy!
mean = np.mean
std = np.std
diff = np.diff

def find(boolvec):
	"""Find indices of all TRUE elements in boolvec.

	You can use like this::

	  take(x, find(greater(x, 0)))

	to select all elements of x greater than zero..

	"""
	return np.compress(boolvec, np.arange(len(boolvec)))

def sem(v, sig=None):
	"""Compute standard error of the mean of vector.

	"""
	if len(v) > 1:
		if sig is None:
			sig = std(v)
		return sig/(float(len(v))**0.5)
	else:
		return 0.0

def zeros(v):
	"""Count number of zero entries in vector.

	"""
	if not isinstance(v, np.ndarray):
		v = np.array(v, np.float)
	return len(v)-len(np.nonzero(v))

def smooth_boxcar(v, kn=1):
	"""Smooth vector using a boxcar (square) filter (ie, running
	average), where kn=1 is a 3pt average, kn=2 is a 5pt average etc..

	"""
	if not isinstance(v, np.ndarray):
		v = np.array(v, np.float)
	n = len(v)
	vout = np.zeros(v.shape)
	for ix in range(0, n):
		a = ix - kn
		if a < 0:
			a = 0
		b = ix + kn
		if b > n:
			b = n
		vout[ix] = mean(v[a:b])
	return vout

def decimate(v, n):
	"""Simple decimatation (ie, downsampling) vector by n. No effort
	to be smart about this -- integer decimation only!

	"""
	if not isinstance(v, np.ndarray):
		v = np.array(v, np.float)
	return np.take(v, list(range(0,len(v),n)))

def sparseness(v):
	"""Compute (Tove & Rolls) sparseness of vector.

	"""
	if not isinstance(v, np.ndarray):
		v = np.array(v, np.float)
	n = float(len(v));
	if np.sum(v) == 0:
		return 0
	else:
		a = ((np.sum(v) / n) ** 2.0) / (np.sum((v**2.0) / n))
		return ((1.0 - a) / (1.0 - (1.0 / n)))

def nanround(n, digits=0):
    if n is not None:
        n = round(n, digits)
    return n

if __name__=='__main__' :
	pass
