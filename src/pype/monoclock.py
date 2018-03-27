# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""
Monotonic clock using ctypes

"""

import ctypes, os
CLOCK_MONOTONIC = 1 # see <linux/time.h>

class timespec(ctypes.Structure):
	_fields_ = [
		('tv_sec', ctypes.c_long),
		('tv_nsec', ctypes.c_long)
	]

_librt = ctypes.CDLL('librt.so.1', use_errno=True)
_clock_gettime = _librt.clock_gettime
_clock_gettime.argtypes = [ctypes.c_int, ctypes.POINTER(timespec)]

def monotonic_time():
	"""Get monotonic clock time -- in seconds
	
	"""
	t = timespec()
	if _clock_gettime(CLOCK_MONOTONIC, ctypes.pointer(t)) != 0:
		errno_ = ctypes.get_errno()
		raise OSError(errno_, os.strerror(errno_))
	return t.tv_sec + (t.tv_nsec * 1e-9)
