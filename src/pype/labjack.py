# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""
Sampler Class for LabJack U3.

This basically provides a simple common interface for both
oreground or background sampling of AIN lines from the U3
using streaming mode. Sample timestamps can be requested
based on U3 device time, or the posix monotonic clock on
the host system (same clock pype already uses internally).

Notes:
  - timestamps are in SECONDS
  - analog inputs are in VOLTS
	- AIN lines seem to float ~1.5V when left untied..
	- VS reads +5V
	- GND reads 0V
  - Digital outputs go between 0 and 3.5V
  - Digital inputs float high..

Problem:
  - there's a bizarre backwards time offset between the time at
	which the pulse is recorded and the timestamp when the pulse
	was generated, such that the pulse appears to be generated
	about 12ms AFTER it was recorded (at 2khz). It seems somewhat
	sampling rate dependent, but not in any obvious way. Nor is
	it consistent enough to correct for.

"""

import u3
import os, time, threading, signal
import numpy as np

from pypedebug import keyboard

U3CLOCK = 4000000.

import ctypes, os

CLOCK_MONOTONIC = 1 # see <linux/time.h>

class timespec(ctypes.Structure):
	_fields_ = [
		('tv_sec', ctypes.c_long),
		('tv_nsec', ctypes.c_long)
	]

librt = ctypes.CDLL('librt.so.1', use_errno=True)
clock_gettime = librt.clock_gettime
clock_gettime.argtypes = [ctypes.c_int, ctypes.POINTER(timespec)]

def monotonic_time():
	t = timespec()
	if clock_gettime(CLOCK_MONOTONIC, ctypes.pointer(t)) != 0:
		errno_ = ctypes.get_errno()
		raise OSError(errno_, os.strerror(errno_))
	return t.tv_sec + t.tv_nsec * 1e-9


class SamplerU3(object):
	def __init__(self, deviceHandle=None, samplingRate=2000.0):
		"""Setup a LabJack U3 for multithreaded sampling.

		Open the LabJack using standard LabJack library calls, then
		instantiate this specifying the deviceHandle (really object
		you get back from u3.U3()) and optional samplingRate in Hz.

		Since this is threaded and uses signals -- you
		must instantiate this ONLY in the main thread!!!!

		"""
		if deviceHandle is None:
			self.d = u3.U3()			# take first available U3
		else:
			self.d = deviceHandle
		self.samplingRate = samplingRate

		self.frags = []
		self.nsamps = 0
		self.running = 0
		self.nrunning = 0
		self.errorcount = 0
		self.fragstart_host = None

		# setup a timer on EIO0 (DB15) -- timers use an EIO or FIO line.
		# offset of 8 pushed it to the DB15 connector...
		self.d.configIO(TimerCounterPinOffset=8,
						NumberOfTimersEnabled=2)

		# timer0 as "system timer low" (mode 10; low 32bits of 4mhz clk)
		# timer1 as "system timer high" (mode 11; high 32bits of 4mhz clk)
		self.d.getFeedback(u3.TimerConfig(timer=0,
										  TimerMode=10,
										  Value=0),
						   u3.TimerConfig(timer=1,
										  TimerMode=11,
										  Value=0),
						   )

		# Set up streaming acquisition:
		#	Acquire 6 channels of two clocks + AIN (0-3) at max gain, at 2khz
		self.d.streamConfig(NumChannels=6,
							PChannels=[200, 224,  0,  1,  2,  3],
							NChannels=[	 0,	  0, 31, 31, 31, 31],
							SampleFrequency=self.samplingRate)

		# configure FIO4-6 for Digital I/O
		self.d.writeRegister(6104, 1)		# Dig OUT
		self.d.writeRegister(6105, 1)		# Dig OUT
		self.d.writeRegister(6106, 0)		# Dig IN
		self.d.writeRegister(6106, 0)		# Dig IN

		signal.signal(signal.SIGUSR1, self.interrupt_handler)


	def stop(self, wait=True):
		"""Setup a LabJack U3 for multithreaded sampling.

		Stop any background acquisitions. By default this will block
		until the acquisition halts. If you don't want this, use
		wait=False. You can call this multiple times and look at
		the return value to see if acquisition is stopped (return
		will be True when stopped).

		"""
		self.running = 0
		while wait and self.nrunning > 0:
			pass
		return self.nrunning == 0

	def go(self, bg=False):
		"""Start acquistion threads.

		This launches two threads:

		- One does continuous analog acquisition on FIO0-3/AIN0-3
		  locked to the host system clock.
		- The other monitors the two DigialInput lines (FIO6,7) and
		  sends a SIGUSR1 to the parent if they change state.
		  Information about the state change is stored in
		  self.ievent

		Method returns after starting the threads. To stop the
		threads, use the stop() method.

		"""
		tad = threading.Thread(target=self.adgo)
		tdi = threading.Thread(target=self.digo)
		self.running = 1
		tad.start()
		tdi.start()

	def adgo(self):
		"""Work function analog input thread.

		"""
		self.frags = []
		self.nsamps = 0
		self.nrunning += 1
		self.errorcount = 0
		while 1:
			# start/stop stream until the clock doesn't stradle a
			# rollover event.
			low = self.d.getFeedback(u3.Timer0(),)[0]
			t1 = self.d.getFeedback(u3.Timer1(),)[0]
			self.d.streamStart()
			self.fragstart_host = monotonic_time()
			t2 = self.d.getFeedback(u3.Timer1(),)[0]
			if t1 == t2:
				break
			else:
				self.d.streamStop()
		clockoffset = (t1 << 32)
		try:
			for r in self.d.streamData():
				if r is not None:
					self.nsamps += len(r['AIN0'])
					ts = (clockoffset +
                          (np.array(r['AIN224'])<<16) + np.array(r['AIN200']))
					self.frags.append((ts,
									   np.array(r['AIN0']),
									   np.array(r['AIN1']),
									   np.array(r['AIN2']),
									   np.array(r['AIN3']),
									   ))
					self.errorcount += r['errors']

				if not self.running:
					break
		finally:
			self.d.streamStop()
			self.nrunning -= 1

	def digo(self, nsamps=None):
		"""Work function digital input thread.

		"""

		# monitor digital input lines in tight loop in order to
		# generate an interrupt if something changes..
		self.idisable()
		self.nrunning += 1
		lasts = None
		try:
			while self.running:
				# use modbus to read FIO6 and FIO7; these were set to
				# be INPUTs in __init__()
				s = self.d.readRegister(6006, 2)
				if lasts:
					# if the state of either line has changed, interrupt
					# the main thread will os.kill(). self.ievent is used
					# to pass info about the event.
					if self.ienabled:
						if lasts[0] != s[0]:
							self.ievent = ('din', 0, s[0], monotonic_time())
							os.kill(os.getpid(), signal.SIGUSR1)
						if lasts[1] != s[1]:
							self.ievent = ('din', 1, s[0], monotonic_time())
							os.kill(os.getpid(), signal.SIGUSR1)
				lasts = s
		finally:
			self.nrunning -= 1

	def ienable(self):
		"""Enable interupt genration.

		"""
		self.ievent = []
		self.ienabled = True

	def idisable(self):
		"""Disable interupt genration.

		"""
		self.ienabled = False
		self.ievent = []

	def get(self, t0=0.0):
		"""Retrieve available data from fragment pool.

		Timestamp and Analog streams are reassembled from the fragment
		pool into numeric vectors and recorded as a tuple. Timestamps
		are in SECONDS, and by default aligned to the host's monotonic
		clock. Note: t0 is not required, but you can get precision
		problems if you don't use it!

		You should be able to call this in mid-acquisition, but
		in general, you should probably call .go(), .stop() and
		then .get() if possible.

		"""
		# reassemble analog datastream from fragment pool
		ts = np.array([])
		a0 = np.array([])
		a1 = np.array([])
		a2 = np.array([])
		a3 = np.array([])

		for (ts_, a0_, a1_, a2_, a3_) in self.frags:
			ts = np.concatenate((ts, ts_,))
			a0 = np.concatenate((a0, a0_,))
			a1 = np.concatenate((a1, a1_,))
			a2 = np.concatenate((a2, a2_,))
			a3 = np.concatenate((a3, a3_,))

		if 0:
			# not sure this is needed and not sure it's
			# correct..
			for n in 1+np.extract(np.diff(ts)<0, range(len(ts))):
				if n == 0:
					ts[n] = ts[n+1] - (ts[n+2] - ts[n+1])
				elif n == len(ts):
					ts[n] = ts[n-1] + (ts[n-1] - ts[n-2])
				else:
					ts[n] = (ts[n-1] + ts[n+1]) / 2.0

		# convert to elapsed time since self.go() and add in
		# the clock_monotonic time to get real system time back
		ts = ((ts - ts[0]) / U3CLOCK) + self.fragstart_host - t0

		return (ts, a0, a1, a2, a3)

	def interrupt_handler(self, signal, frame):
		# self.ievent contains information about what caused the
		# interrupt: channel, time etc..
		print self.ievent

	def digout(self, line, state):
		if line in [0, 1]:
			self.d.writeRegister(6004+line, state)

	def digin(self, line):
		# line should be 0 or 1
		if line in [0, 1]:
			return self.d.readRegister(6006+line)


if __name__ == "__main__":
	from pylab import *

	s = SamplerU3()

	try:
		while 1:
			s.go()
			time.sleep(0.25)
			s.stop(wait=1)

			(ts, a0, a1, a2, a3) = s.get(devtime=False)

			# compute lag between analog datastream and self-timed pulse
			ix = np.extract(a2 > 1.0, range(len(ts)))
			#lag = 1000. * (ts[ix[0]] - tn)

			clf()
			plot(ts, a0)
			xlim(-5, 5)
			xlim(ts[1], ts[-1])
			ylabel('voltage')
			xlabel('time (s)')
			#title('lag = %.2fms' % lag)
			draw()

	except KeyboardInterrupt:
		k = s.d.getFeedback(u3.BitStateWrite(4, 0),
							u3.BitStateWrite(5, 1),)
		s.stop(wait=1)
		s.d.close()
