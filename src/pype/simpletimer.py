# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""Timer based on librt monotonic clock function.

This is a comedi_server-free clone of the pype.Timer class,
really for debugging when comedi's not available. See docs
for pype.Time().

This timer's actually has slightly more overhead than the
comedi version..
for sthis

"""

import os
import ctypes

class timespec(ctypes.Structure):
	_fields_ = [
		('tv_sec', ctypes.c_long),
		('tv_nsec', ctypes.c_long)
	]

librt = ctypes.CDLL('librt.so.1', use_errno=True)
clock_gettime = librt.clock_gettime
clock_gettime.argtypes = [ctypes.c_int, ctypes.POINTER(timespec)]
CLOCK_MONOTONIC = 1 # see <linux/time.h>

class Timer(object):
	"""Like Timer class, but uses built in clock"""
	def __init__(self, on=True):
		self._t = timespec()
		if on:
			self.reset()
		else:
			self.disable()

	def disable(self):
        self._start_at = None

	def reset(self):
		"""Reset timer.

		:return: nothing

		"""
		self._start_at = self._monotonic_time_ms()

	def ms(self):
		"""Query timer.

		:return: (ms) elapsed time

		"""
        try:
            return self._monotonic_time_ms() - self._start_at
        except TypeError:
            return 0

	def _monotonic_time_ms(self):
		clock_gettime(CLOCK_MONOTONIC, ctypes.pointer(self._t))
		return int(round((self._t.tv_sec + (self._t.tv_nsec * 1e-9)) * 1000.0))

		if clock_gettime(CLOCK_MONOTONIC, ctypes.pointer(self._t)) != 0:
			errno_ = ctypes.get_errno()
			raise OSError(errno_, os.strerror(errno_))
		return int(round((self._t.tv_sec + (self._t.tv_nsec * 1e-9)) * 1000.0))

def exact_time_sec():
    t = timespec()
    if clock_gettime(CLOCK_MONOTONIC, ctypes.pointer(t)) != 0:
        errno_ = ctypes.get_errno()
        raise OSError(errno_, os.strerror(errno_))
    return t.tv_sec + (t.tv_nsec * 1e-9)
