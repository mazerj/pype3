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

import monotonic
def get_monotonic_ms():
    return int(round(monotonic.monotonic() * 1000.0))


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
        self._start_at = get_monotonic_ms()

    def ms(self):
        """Query timer.

        :return: (ms) elapsed time

        """
        try:
            return get_monotonic_ms() - self._start_at
        except TypeError:
            return 0

