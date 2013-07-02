# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""Timer based on librt monotonic clock function.

This is a comedi_server-free clone of the pype.Timer class,
really for debugging when comedi's not available. See docs
for pype.Time().

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
        if on:
            self.reset()
        else:
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
        if self._start_at is None:
            return 0
        else:
            return self._monotonic_time_ms() - self._start_at

	def _monotonic_time_ms(self):
		t = timespec()
		if clock_gettime(CLOCK_MONOTONIC, ctypes.pointer(t)) != 0:
			errno_ = ctypes.get_errno()
			raise OSError(errno_, os.strerror(errno_))
		return int(round((t.tv_sec + t.tv_nsec * 1e-9) * 1000.0))
