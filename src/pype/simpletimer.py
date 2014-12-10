# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""Timer based on librt monotonic clock function.

This is a comedi_server-free clone of the pype.Timer class,
really for debugging when comedi's not available. See docs
for pype.Time().

This timer's actually has slightly more overhead than the
comedi version..
for sthis

"""

import os, sys

if sys.platform.startswith('darwin'):
    import ctypes
    
    # src:
    #   http://twistedmatrix.com/trac/attachment/ticket/2424/linux_and_osx.py
    libSystem = ctypes.CDLL('libSystem.dylib', use_errno=True)
    CoreServices = ctypes.CDLL(
        '/System/Library/Frameworks/CoreServices.framework/CoreServices',
        use_errno=True)
    mach_absolute_time = libSystem.mach_absolute_time
    mach_absolute_time.restype = ctypes.c_uint64
    AbsoluteToNanoseconds = CoreServices.AbsoluteToNanoseconds
    AbsoluteToNanoseconds.restype = ctypes.c_uint64
    AbsoluteToNanoseconds.argtypes = [ctypes.c_uint64]
    
    def _get_monotonic_ms():
        return AbsoluteToNanoseconds(mach_absolute_time()) * 1e-6
elif sys.platform.startswith('linux'):
    # linux/posix: 
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

    def get__monotonic_ms():
        ts = timespec()
        clock_gettime(CLOCK_MONOTONIC, ctypes.pointer(ts))
        return int(round((ts.tv_sec + (ts.tv_nsec * 1e-9)) * 1000.0))
else:
    # fallback to using plain old time.time() and converting from s to ms
    import time
    def get__monotonic_ms():
        return int(round(time.time() * 1000.0))
    

class Timer(object):
    """Like Timer class, but uses built in clock"""
    def __init__(self, on=True):
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
        self._start_at = _get_monotonic_ms()

    def ms(self):
        """Query timer.

        :return: (ms) elapsed time

        """
        try:
            return _get_monotonic_ms() - self._start_at
        except TypeError:
            return 0

