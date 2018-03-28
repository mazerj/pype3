# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""
Sampler Class for LabJack U3.

This basically provides a class that allows streaming
of data from a LabJack U3 device. The sampling runs
in a separte thread (note: potential for GIL blocking
here). The thread collects 4 channels of analog input
from the U3 and stores it synced to the host clock. Sync
is within 1ms (verified 03/27/2018 by cross correlation
against dacq4 comedi drivers).

While AIN data is streaming a second stream controls
the digital inputs and outputs, allowing pulses to be
generated and detected. Latency of DOUT is <1ms (verified
03/27/2018 by recording DOUT using dacq4/comedi).

AINO[0-3] are used for analog input (fixed on U3-HV)
FIO4: digital output 0
FIO5: digital output 1
FIO6: digital input 0
FIO7: digital input 1

Notes:
  - timestamps are in SECONDS
  - analog input is in VOLTS
	- AIN lines seem to float to ~1.5V when left open
	- VS reads +5V
	- GND reads 0V
  - Digital outputs go between 0 and 3.5V
  - Digital inputs float high

Problem:
  - there's a bizarre backwards time offset between the time at
	which the pulse is recorded and the timestamp when the pulse
	was generated, such that the pulse appears to be generated
	about 12ms AFTER it was recorded (at 2khz). It seems somewhat
	sampling rate dependent, but not in any obvious way. Nor is
	it consistent enough to correct for.
  - are signals being generated on DIN transitions? need to
    check. which thread gets the signal??

"""

import u3
import os, threading, signal
import numpy as np
from monoclock import monotonic_time

# U3 internal clock speed (used for streaming timestamps)
U3CLOCK = 4000000.

class SamplerU3(object):
	def __init__(self, samplingRate=2000.0, dig_callback=None):
		"""Setup a LabJack U3 for multithreaded sampling.

		Open the LabJack using standard LabJack library calls, then
		instantiate this specifying the deviceHandle (really object
		you get back from u3.U3()) and optional samplingRate in Hz.

		Should be instantiated in main thread -- signals be caught
		by the main thread!

		If dig_callback is provided, then the callback function will
		be called when the DIN lines change state with two args: (self
		(this object), event-details). Either callback OR signals will
		happen, not both: callback, if defined, otherwise signal. In
		both cases, this will only happen if `running` and din_alerts
		are enabled!

		"""
		self.d = u3.U3()			# take first available U3
		self.samplingRate = samplingRate

		self.config = self.d.configU3()
		self.frags = []
		self.nsamps_ad = 0
		self.running = 0
		self.nrunning = 0
		self.errorcount = 0
		self.fragstart_host = None
		self.dig_callback = dig_callback

		# setup a timer on EIO0 (DB15) -- timers use an EIO or FIO line.
		# offset of 8 pushed it to the DB15 connector...
		self.d.configIO(TimerCounterPinOffset=8,
						NumberOfTimersEnabled=2)

		# timer0 as "system timer low" (mode 10; low 32bits of 4mhz clk)
		# timer1 as "system timer high" (mode 11; high 32bits of 4mhz clk)
		self.d.getFeedback(u3.TimerConfig(timer=0, TimerMode=10,
										  Value=0),
						   u3.TimerConfig(timer=1, TimerMode=11,
										  Value=0))

		# Set up streaming acquisition:
		#	Acquire 6 channels of two clocks + AIN (0-3) at max gain, at
		#   specified sampling rate (default: 2.0 kHz)
		self.d.streamConfig(NumChannels=6,
							PChannels=[200, 224,  0,  1,  2,  3],
							NChannels=[	 0,	  0, 31, 31, 31, 31],
							SampleFrequency=self.samplingRate)

		# configure FIO4-6 for Digital I/O
		self.d.writeRegister(6104, 1)		# Dig OUT
		self.d.writeRegister(6105, 1)		# Dig OUT
		self.d.writeRegister(6106, 0)		# Dig IN
		self.d.writeRegister(6107, 0)		# Dig IN

	def start(self):
		"""Start acquistion threads.

		This launches two threads:

		- One does continuous analog acquisition on FIO0-3/AIN0-3
		  locked to the host system clock.
		- The other monitors the two DigitalInput lines (FIO6,7) and
		  sends a SIGUSR1 to the parent if they change state.
		- Note that in python, signals are always handled in the
		  main thread, even though posix doesn't specify. See
		  https://docs.python.org/dev/library/signal.html
		- Details about the state change are stored in
		  self.ievent

		Method returns after starting the threads. To stop the
		threads, use the stop() method.

		"""
		tad = threading.Thread(target=self._start_ad)
		tdi = threading.Thread(target=self._start_dig)
		self.running = 1
		tad.start()
		tdi.start()

	def stop(self, wait=True):
		"""Signal running acquisition threads to stop and
		optionally wait for them to complete.

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

	def _start_ad(self):
		"""Work function analog input thread.

		"""
		self.frags = []
		self.nsamps_ad = 0
		self.nrunning += 1
		self.errorcount = 0

		self.d.streamStart()
		self.clockoffset_host = monotonic_time()

		if 0:
			# read clock directly
			lo = self.d.getFeedback(u3.Timer0(),)[0] # timer LSB
			hi = self.d.getFeedback(u3.Timer1(),)[0] # timer MSB
			u3_clock = (hi<<16) + lo
			
		try:
			for r in self.d.streamData():
				if r is not None:
					self.nsamps_ad += len(r['AIN0'])
					hi = np.bitwise_and(np.array(r['AIN224']), 0xffff)
					lo = np.bitwise_and(np.array(r['AIN200']), 0xffff)
					ts = (hi<<16) + lo
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

	def _start_dig(self):
		"""Work function digital input thread.

		"""

		# Watch digital input lines in tight loop.
		# If inputs change state when signals are
		# enabled, SIGUSR1 will be generated..
		#
		# Starts with interrupts disabled!
		self.din_alerts(enable=False)
		self.nrunning += 1
		laststate = None
		try:
			while self.running:
				# Read FIO6 and FIO7; these were set to
				# be INPUTs in __init__()
				state = self.d.readRegister(6006, 2)
				if laststate is None:
					laststate = state
				elif self._gen_alerts:
					# if the state of either line has changed, interrupt
					# the main thread will os.kill(). self.ievent is used
					# to pass info about the event.
					self.ievent = ('din', state, monotonic_time())
					if self.dig_callback:
						self.dig_callback(self, self.ievent)
					else:
						os.kill(os.getpid(), signal.SIGUSR1)
					laststate = state
		finally:
			self.nrunning -= 1

	def din_alerts(self, enable):
		"""Enable/disable `alert` generation - alerts are either
		calling of the defined callback function OR SIGUSR1 to
		main thread.

		"""
		self._gen_alerts = enable
		self.ievent = []

	def get(self, t0=0.0):
		"""Retrieve and assemble data from fragment pool.

		Timestamp and Analog streams are reassembled from the fragment
		pool into numeric vectors and recorded as a tuple. Timestamps
		are in SECONDS, and by default aligned to the host's monotonic
		clock.

		You should be able to call this in mid-acquisition, but
		in general, you should probably call .start(), .stop() and
		then .get() if possible.

		"""
		# reassemble analog datastream from fragment pool
		rawts = np.array([])
		ts = np.array([])
		a0 = np.array([])
		a1 = np.array([])
		a2 = np.array([])
		a3 = np.array([])

		for (ts_, a0_, a1_, a2_, a3_) in self.frags:
			rawts = np.concatenate((rawts, ts_,))
			ts = np.concatenate((ts, ts_,))
			a0 = np.concatenate((a0, a0_,))
			a1 = np.concatenate((a1, a1_,))
			a2 = np.concatenate((a2, a2_,))
			a3 = np.concatenate((a3, a3_,))

		# comb through data and delete negative dt's --- this
		# forces the time series to be monotonic increasing
		# I'm pretty sure this reflects a labjack bug..
		while 1:
			dt = np.diff(ts)
			ix = np.where(np.concatenate([[True,], np.greater(dt, 0.0)]))[0]
			if len(ix) == len(ts): break
			rawts = rawts[ix]
			ts = ts[ix]
			a0 = a0[ix]
			a1 = a1[ix]
			a2 = a2[ix]
			a3 = a3[ix]

		# convert to elapsed time since self.start() and add in
		# the clock_monotonic time to get real system time back
		ts = ((ts - ts[0]) / U3CLOCK) + self.clockoffset_host - t0

		return (rawts, ts, a0, a1, a2, a3)

	def digout(self, line, state):
		if line in [0, 1]:
			self.d.writeRegister(6004+line, state)

	def digin(self, line):
		# line should be 0 or 1
		if line in [0, 1]:
			return self.d.readRegister(6006+line)

if __name__ == "__main__":
	import sys, time

	# sample for 5s (or CLI specified time) and dump AIN data to stdou
	if len(sys.argv) > 1:
		t = int(sys.argv[1])
	else:
		t = 5.0
	
	s = SamplerU3()
	try:
		s.start()
		time.sleep(t)
		s.stop(wait=1)

		(rawts, ts, a0, a1, a2, a3) = s.get()

		print '# u3clk hostclk a0 a1 a2 a3'
		for n in range(len(rawts)):
			print '%.0f\t%.0f\t%f\t%f\t%f\t%f' % \
				  (rawts[n], ts[n], a0[n], a1[n], a2[n], a3[n],)

	except KeyboardInterrupt:
		print 'shutting down'
		k = s.d.getFeedback(u3.BitStateWrite(4, 0),
							u3.BitStateWrite(5, 1),)
		s.stop(wait=1)
		s.d.close()
