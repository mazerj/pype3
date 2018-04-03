#!/usr/bin/env pypenv
# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""Interface to audio card via pygame

"""

import sys
import pygame
import numpy as np

try:
	from guitools import Logger
except ImportError:
	def Logger(s, *args):
		sys.stderr.write(s)

class _Beeper(object):
	_doinit = 1
	_disabled = None
	_dafreq = None
	_bits = None
	_chans = None

	def __init__(self):
		if _Beeper._disabled: return

		if _Beeper._doinit:
			if pygame.mixer.get_init() is None:
				try:
					pygame.mixer.init()
				except pygame.error:
					Logger('beep: no audio device available -- check perms\n')
					_Beeper._doinit = 0
					_Beeper._disabled = 1
					return
				pygame.sndarray.use_arraytype('numpy')
			(_Beeper._dafreq,
			 _Beeper._bits, _Beeper._chans) = pygame.mixer.get_init()
			#Logger('_Beeper: %d hz, %d bits, chans=%d\n' %
			#	   (_Beeper._dafreq, _Beeper._bits, _Beeper._chans))
			_Beeper.cache = {}
			_Beeper._doinit = 0

	def _beep(self, freq, msdur, vol, risefall, wait, play):
		if _Beeper._disabled: return

		try:
			s = _Beeper.cache[freq, msdur, vol, risefall]
		except KeyError:
			s = self._synth(freq, msdur, vol, risefall)
			_Beeper.cache[freq, msdur, vol, risefall] = s

		if play:
			# wait for free mixer...
			while pygame.mixer.get_busy():
				pass
			s.play()
			while wait and pygame.mixer.get_busy():
				pass

	def _synth(self, freq, msdur, vol, risefall):
		t = np.arange(0, msdur / 1000.0, 1.0 / _Beeper._dafreq)
		s = np.zeros((t.shape[0], 2))
		# use trapezoidal envelope with risefall (below) time
		if msdur < 40:
			risefall = msdur / 2.0
		env = -abs((t - (t[-1] / 2)) / (risefall/1000.0))
		env = env - min(env)
		env = np.where(np.less(env, 1.0), env, 1.0)

		bits = _Beeper._bits
		if bits < 0:
			bits = -bits
			signed = 1
		else:
			signed = 0

		fullrange = np.power(2, bits-1)

		if freq is None:
			y = env * vol * fullrange * np.random.random(t.shape)
		else:
			y = env * vol * fullrange * np.sin(2.0 * np.pi * t * freq)
		y = y.astype(np.int16)

		if _Beeper._chans == 2:
			y = np.transpose(np.array([y,y]))
		s = pygame.sndarray.make_sound(y)
		return s

def beep(freq=-1, msdur=-1, vol=0.5, risefall=20, wait=1, play=1, disable=None):
	"""Beep the speaker using sound card.

	:param freq: (Hz/None) tone frequency (None for noise)

	:param msdur: (ms) tone duration

	:param vol: (0-1) volume

	:param risefall: (ms) envelope rise and fall

	:param wait: (bool) block until sound has been played

	:param play: (bool) true: play now; false: synthesize and cache for later

    :return: nothing    
	"""

	if disable:
		# just disable sound subsystem
		_Beeper._disabled = 1
	elif freq and freq < 0:
		_Beeper()
	else:
		_Beeper()._beep(freq, msdur, vol=vol, risefall=risefall,
						wait=wait, play=play)



def warble(base, t, volume=1, fmper=25, driver=None):
	"""Make a nice warbling sound - cheapo FM

	:param base: (Hz) base frequency

	:param t: (ms) duration

	:param volume: (0-1) volume

	:param fmper: (ms) period of modulation frequency

    :return: nothing

	"""

	et = 0
	while et < t:
		beep(base, fmper, volume, wait=0)
		beep(1.10*base, fmper, volume, wait=0)
		et = et + (2 * fmper)


if	__name__ == '__main__':
	print "start"
	beep()
	#beep(1000, 100, 1, 1)
	warble(1000, 100)
	warble(500, 100)
	print "quitting"
	pygame.mixer.quit()
	print "done."
