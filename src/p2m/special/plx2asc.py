#!/usr/bin/env python
# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-
# $Id: plx2asc.py 2 2010-12-10 16:40:31Z mazer $

"""
Tools for extracting data from Plexon .plx files
------------------------------------------------

usage: plx2asc.py  [-i] [-v] [-p outprefix] plxfile

  -i     list summary info for spike & lfp channels
  -h     just dump header info
  -v     verbose dump (debugging only!)
  -p str filename/dir prefix for output files
          prefix+'.hdr'  --> hdr info
          prefix+'.spk'  --> spike times
          prefix+'.spw'  --> spike waveforms
          prefix+'.lfp'  --> spike lfp signals

Output Files
------------
<prefix>.hdr:		columns="% channel nunits lfp"
		table of electrodes/channels (1-based!) -- for each
		channel column #2 indicates # of single units recorded
		and column #3 indicates whether or not LFPs were recorded
<prefix>.spk:		columns="% trial channel unit time"
		spike timing info -- timestamps only. Columns should be
		self-explanatory; channel is 1-based; unit is 0-based, but
		unit 0 is 'unsorted' threshold crossings.

<prefix>.spw:		columns="% trial channel unit index time volt"
		again, pretty self explanatory: channel is 1-based, unit is
		0-based (0 for unsorted). index is sequence in the data stream
		to facilitate sorting -- each waveform is sequenced in order
		using 'index' with a NaN between events. 'time' is real
		time in MS relative to pype gating signal and 'volt' is the
		actual voltage on the electrode (waveform)

<prefix>.lfp:	   columns="% trial channel time volt"
		Same as .spw, but without 'index' and no NaN dividers are
		needed..

NOTE: 'trial' is always 1-based

Times are all in MS relative to the pype trigger signal for each trial
(assumes plexon is running in gated mode). Voltages are output in MV
using the conversion algorithm described in the Plexon supplied
documentation for file versions >= 105

IMPORT NOTES
------------
  About LFPs (slow ad)
    - lfp (slow adc) channels are 'named' AD01-AD16 (there are the
	  strings stored in 'fileheader.slows[n].name' by the plexon.
	- however, the actual channel numbers stored in the data records
	  are zero based, so AD01 has DataRecord.channel=0

	  HOWEVER: THIS PROGRAM ADDS ONE TO THE SLOW CHANNEL NUMBER SO
	  THEY WILL MATCH THE SPIKE DATA!

  For spikes, this the system is different -- again, the naming system
  is 1-based (sig001-sig016), however, this time, sig001 is stored
  with DataRecord.channel=1

  This means that when using DataRecord.channel to access the data
  in FileHeader.channels and FileHeader.slows you need to do:
    FileHeader.channels[d.channel - 1].gain etc..
	  or
    FileHeader.slows[d.channel].gain etc..

  Note that unit data is always 0-based, with 0 corresponding to unsorted
  spike data and 1 to unit 'a', 2 to unit 'b' etc..

REVISION HISTORY
----------------
Wed May  7 10:46:17 2008 mazer
  - DataRecord.ts was not being correctly computed -- the MSB word was
    typically being set to 1 (val<40 instead of val<<40..) regenerated
	plx files after fixing..
"""

import sys, struct

class NotPlx(Exception): pass

# Plexon type codes for DataRecords
PL_SPIKE=1								# single spike waveform
PL_STEREO=2								# stereotrode waveforms
PL_TETRO=3								# tetrode waveforms
PL_EVENT=4								# discrete event record
PL_SLOW=5								# block of slow (lfp) data

# Plexon event codes
PL_XSTROBE=257							# external strobe signal (?)
PL_XSTART=258							# external start trigger
PL_XSTOP=259							# external stop trigger
PL_PAUSE=260							# ..not used..
PL_RESUME=261							# ..not used..

def _readbytes(f, count, fmt):
	"""
	Read a block of data from a file and unpack using the struct module
	"""

	if count:
		fmt = '%d%s' % (count, fmt)
	buf = f.read(struct.calcsize(fmt))
	if len(buf) == 0:
		raise EOFError
	else:
		buf = struct.unpack(fmt, buf)
		if fmt[-1] == 's':
			return buf[0].split(chr(0))[0]
		if count == 1:
			return buf[0]
		else:
			return buf

def _extractbytes(s, count, fmt):
	"""
	Unpack data already in memory using the struct module. This is to
	speed up processing so block of data can be read quickly using .read()
	and then converted later. Syntax is designed to be parallel to the
	_readbytes() function so you can switch back and forth during
	debugging..
	"""
	if len(s) == 0:
		raise EOFError
	
	if count:
		fmt = '%d%s' % (count, fmt)
	nbytes = struct.calcsize(fmt)
	s1, s2 = s[:nbytes], s[nbytes:]
	buf = struct.unpack(fmt, s1)
	if fmt[-1] == 's':
		return (s2, buf[0].split(chr(0))[0])
	if count == 1:
		return s2, buf[0]
	else:
		return s2, buf

class FileHeader:
	"""
	Encapsulated the entire Plexon .plx file header structure. This
	is a line-by-line translation (and optimization) of the Plexon.h
	file that describes the data structures contained in the .plx
	files.

	The 
	"""
	def __init__(self, f):
		start = f.tell()
		self.Magic = _readbytes(f, 1, 'I')
		if not self.Magic == 0x58454c50:
			# magic number doesn't match..
			raise NotPlx
		f.seek(start)
		

		buf = f.read(7504)
		(buf, self.Magic) = _extractbytes(buf, 1, 'I')
		(buf, self.Version) = _extractbytes(buf, 1, 'i')
		(buf, self.Comment) = _extractbytes(buf, 0, '128s')
		
		(buf, self.ADFrequency) = _extractbytes(buf, 1, 'i')
		(buf, self.NumDspChannels) = _extractbytes(buf, 1, 'i')
		(buf, self.NumEventChannels) = _extractbytes(buf, 1, 'i')
		(buf, self.NumSlowChannels) = _extractbytes(buf, 1, 'i')
		(buf, self.NumPointsWave) = _extractbytes(buf, 1, 'i')
		(buf, self.NumPointsPreThr) = _extractbytes(buf, 1, 'i')
		
		(buf, self.Year) = _extractbytes(buf, 1, 'i')
		(buf, self.Month) = _extractbytes(buf, 1, 'i')
		(buf, self.Day) = _extractbytes(buf, 1, 'i')
		(buf, self.Hour) = _extractbytes(buf, 1, 'i')
		(buf, self.Min) = _extractbytes(buf, 1, 'i')
		(buf, self.Sec) = _extractbytes(buf, 1, 'i')
		
		(buf, self.FastRead) = _extractbytes(buf, 1, 'i')
		(buf, self.WaveformFreq) = _extractbytes(buf, 1, 'i')
		(buf, self.LastTimeStamp) = _extractbytes(buf, 1, 'd')

		(buf, self.Trodalness) = _extractbytes(buf, 1, 'B')
		(buf, self.DataTrodalness) = _extractbytes(buf, 1, 'B')
		(buf, self.BitsPerSpikeSample) = _extractbytes(buf, 1, 'B')
		(buf, self.BitsPerSlowSample) = _extractbytes(buf, 1, 'B')
		(buf, self.SpikeMaxMagnitudeMV) = _extractbytes(buf, 1, 'h')
		(buf, self.SlowMaxMagnitudeMV) = _extractbytes(buf, 1, 'h')
		(buf, self.SpikePreAmpGain) = _extractbytes(buf, 1, 'h')

		(buf, padding) = _extractbytes(buf, 0, '46c')
	
		# read to appropriate place in file
		# constant part
		# ...don't really know what this stuff is for...
		(buf, tmp) = _extractbytes(buf, 5*130, 'i') # tscounts header
		(buf, tmp) = _extractbytes(buf, 5*130, 'i') # wfcounts header
		(buf, tmp) = _extractbytes(buf, 512, 'i')   # evcounts header

		self.channels = []
		for i in range(self.NumDspChannels):
			self.channels.append(ChannelHeader(f))
			
		self.events = []
		for i in range(self.NumEventChannels):
			self.events.append(EventHeader(f))
			
		self.slows = []
		for i in range(self.NumSlowChannels):
			self.slows.append(SlowHeader(f))
			
		if len(self.slows) > 0:
			# all slow ad channels will have same speed..
			self.slow_adfreq = self.slows[0].ADFrequency

	def pp(self, f):
		f.write('header.Magic=%0x\n' % self.Magic)
		f.write('header.Version=%d\n' % self.Version)
		f.write('header.Comment=<%s>\n' % self.Comment)
		f.write('header.ADFrequency=%d\n' % self.ADFrequency)
		f.write('header.NumDspChannels=%d\n' % self.NumDspChannels)
		f.write('header.NumEventChannels=%d\n' % self.NumEventChannels)
		f.write('header.NumSlowChannels=%d\n' % self.NumSlowChannels)
		f.write('header.NumPointsWave=%d\n' % self.NumPointsWave)
		f.write('header.NumPointsPreThr=%d\n' % self.NumPointsPreThr)
		f.write('header.date=%d %d %d %d %d %d\n' % \
				(self.Year, self.Month, self.Day,
				 self.Hour, self.Min, self.Sec))

		f.write('\n')

		for i in self.channels:
			i.pp(f)
			f.write('\n')
			
		for i in self.events:
			i.pp(f)
			f.write('\n')
			
		for i in self.slows:
			i.pp(f)
			f.write('\n')

class ChannelHeader:
	def __init__(self, f):
		buf = f.read(1020)
		(buf, self.Name) = _extractbytes(buf, 0, '32s')
		(buf, self.SIGName) = _extractbytes(buf, 0, '32s')
		(buf, self.Channel) = _extractbytes(buf, 1, 'i')
		(buf, self.WFRate) = _extractbytes(buf, 1, 'i')
		(buf, self.SIG) = _extractbytes(buf, 1, 'i')
		(buf, self.Ref) = _extractbytes(buf, 1, 'i')
		(buf, self.Gain) = _extractbytes(buf, 1, 'i')
		(buf, self.Filter) = _extractbytes(buf, 1, 'i')
		(buf, self.Threshold) = _extractbytes(buf, 1, 'i')
		(buf, self.Method) = _extractbytes(buf, 1, 'i')
		(buf, self.NUnits) = _extractbytes(buf, 1, 'i')
		(buf, self.Template) = _extractbytes(buf, 5*64, 'h')
		(buf, self.Fit) = _extractbytes(buf, 5, 'i')
		(buf, self.SortWidth) = _extractbytes(buf, 1, 'i')
		(buf, self.Boxes) = _extractbytes(buf, 5*2*4, 'h')
		(buf, self.SortBeg) = _extractbytes(buf, 1, 'i')
		(buf, self.Comment) = _extractbytes(buf, 0, '128s')
		(buf, padding) = _extractbytes(buf, 11, 'i')
		
	def pp(self, f):
		f.write('chan.Name=<%s>\n' % self.Name)
		f.write('chan.SIGName=<%s>\n' % self.SIGName)
		f.write('chan.Channel=%d\n' % self.Channel)
		f.write('chan.WFRate=%d\n' % self.WFRate)
		f.write('chan.SIG=%d\n' % self.SIG)
		f.write('chan.Ref=%d\n' % self.Ref)
		f.write('chan.Gain=%d\n' % self.Gain)
		f.write('chan.Filter=%d\n' % self.Filter)
		f.write('chan.Threshold=%d\n' % self.Threshold)
		f.write('chan.Method=%d\n' % self.Method)
		f.write('chan.NUnits=%d\n' % self.NUnits)
		f.write('chan.SortWidth=%d\n' % self.SortWidth)
		f.write('chan.SortBeg=%d\n' % self.SortBeg)
		f.write('chan.Comment=<%s>\n' % self.Comment)

class EventHeader:
	def __init__(self, f):
		buf = f.read(296)
		(buf, self.Name) = _extractbytes(buf, 0, '32s')
		# this channel is 1-based
		(buf, self.Channel) = _extractbytes(buf, 1, 'i')
		(buf, self.Comment) = _extractbytes(buf, 0, '128s')
		(buf, padding) = _extractbytes(buf, 33, 'i')

	def pp(self, f):
		f.write('event.Name=<%s>\n' % self.Name)
		f.write('event.Channel=%d\n' % self.Channel)
		f.write('event.Comment=<%s>\n' % self.Comment)
		
class SlowHeader:
	def __init__(self, f):
		buf = f.read(296)
		(buf, self.Name) = _extractbytes(buf, 0, '32s')
		# this channel is 0-based
		(buf, self.Channel) = _extractbytes(buf, 1, 'i')
		(buf, self.ADFrequency) = _extractbytes(buf, 1, 'i')
		(buf, self.Gain) = _extractbytes(buf, 1, 'i')
		(buf, self.Enabled) = _extractbytes(buf, 1, 'i')
		(buf, self.PreAmpGain) = _extractbytes(buf, 1, 'i')
		(buf, self.spikechannel) = _extractbytes(buf, 1, 'i')
		(buf, self.Comment) = _extractbytes(buf, 0, '128s')
		(buf, padding) = _extractbytes(buf, 28, 'i')

	def pp(self, f):
		f.write('slow.Name=<%s>\n' % self.Name)
		f.write('slow.Channel=%d\n' % self.Channel)
		f.write('slow.ADFrequency=%d\n' % self.ADFrequency)
		f.write('slow.Gain=%d\n' % self.Gain)
		f.write('slow.Enabled=%d\n' % self.Enabled)
		f.write('slow.PreAmpGain=%d\n' % self.PreAmpGain)
		f.write('slow.Comment=<%s>\n' % self.Comment)

class DataRecord:
	def __init__(self, f):
		buf = f.read(16)
		(buf, self.Type) = _extractbytes(buf, 1, 'h')
		# timestampes are 40-bits (5 bytes)
		# upper is upper byte, lower is lower 4 bytes
 		(buf, self.timestamp_upper) = _extractbytes(buf, 1, 'H')
		(buf, self.timestamp_lower) = _extractbytes(buf, 1, 'L')

		# BUG: prior to 5/7/2008 this was ...<40 instead of ...<<40
		self.ts = (self.timestamp_upper<<40) + self.timestamp_lower

		# channel and be a channel OR an event code!
		# if type == PL_EVENT, it's an event code..
		# and channel can be 0- or 1-based depending
		# on whether it's a spike waveform or an LFP
		# waveform
		(buf, self.Channel) = _extractbytes(buf, 1, 'h')

		# unit starts at 0, with 0=unsorted, 1='a' etc..
		(buf, self.Unit) = _extractbytes(buf, 1, 'h')
		(buf, self.NumberOfWaveforms) = _extractbytes(buf, 1, 'h')
		(buf, self.NumberOfWordsInWaveform) = _extractbytes(buf, 1, 'h')

		if (self.NumberOfWaveforms * self.NumberOfWordsInWaveform) > 0:
			self.waveform = _readbytes(f, self.NumberOfWordsInWaveform, 'h')
		else:
			self.waveform = None

	def pp(self, f):
		f.write('data.Type=%d\n' % self.Type)
		f.write('data.ts=0x%d\n' % self.ts)
		f.write('data.Channel=%d\n' % self.Channel)
		f.write('data.Unit=%d\n' % self.Unit)
		f.write('data.NumberOfWaveforms=%d\n' % self.NumberOfWaveforms)
		f.write('data.NumberOfWordsInWaveform=%d\n' % \
				self.NumberOfWordsInWaveform)
		if self.waveform:
			f.write('data.waveform=%d samples\n' % len(self.waveform))
		else:
			f.write('data.waveform=None\n')


def info(fname):
	f = open(fname, 'r')
	h = FileHeader(f)
	f.close()

	sys.stdout.write("chan\t#units\n")
	for s in h.slows:
		if s.Enabled:
			sys.stdout.write("%s\t%d\n" % \
							 (s.Name, 1, ))
		
	for s in h.channels:
		if s.NUnits > 0:
			sys.stdout.write("%s\t%d\n" % \
							 (s.SIGName, s.NUnits, ))


def xall(fname, prefix):
	spikes = 1
	lfp = 1
	
	if prefix is None:
		prefix = fname

	f = open(fname, 'r')
	h = FileHeader(f)

	t0 = 0.0;
	trial_number = 0

	if prefix is None:
		o = '/dev/null'
	else:
		o = prefix + '.hdr'
		#sys.stderr.write('header -> %s\n' % o)
	hdrout = open(o, 'w')
	hdrout.write('% channel nunits lfp\n')

	if prefix is None:
		o = '/dev/null'
	else:
		o = prefix + '.spk'
		#sys.stderr.write('spikes -> %s\n' % o)
	spikeout = open(o, 'w')
	spikeout.write('% trial channel unit time\n')
	
	if prefix is None:
		o = '/dev/null'
	else:
		o = prefix + '.spw'
		#sys.stderr.write('spike waveforms -> %s\n' % o)
	spwout = open(o, 'w')
	spwout.write('% trial channel unit index time volt\n')

	if prefix is None:
		o = '/dev/null'
	else:
		o = prefix + '.lfp'
		#sys.stderr.write('lfp -> %s\n' % o)
	lfpout = open(o, 'w')
	lfpout.write('% trial channel time volt\n')

	for i in range(h.NumDspChannels):
		hdrout.write('%d\t' % (i+1,))
		hdrout.write('%d\t' % h.channels[i].NUnits)
		hdrout.write('%d\n' % h.slows[i].Enabled)

	nspikes = 0
	nsamps = 0
	nwavesamps = 0
	nrec = 0

	t0 = None
	adshift = None

	while 1:
		try:
			d = DataRecord(f)
			nrec = nrec + 1
		except EOFError:
			break

		if d.Type == PL_EVENT and d.Channel == PL_XSTART:
			if t0 is None:
				t0 = float(d.ts)
				trial_number = trial_number + 1
			else:
				sys.stderr.write('double XSTART: trial %d\n' % trial_number)
				sys.exit(1)
			
		elif d.Type == PL_EVENT and d.Channel == PL_XSTOP:
			t0 = None

		elif lfp and d.Type == PL_SLOW and (not t0 is None):
			if adshift is None:
				# assume the very first LFP sample in the file starts
				# at time ZERO (for pype, this is the same time as the
				# very first PL_XSTART). The assumption here is that
				# the NIDAQ card lags a bit behind the MAP box (group
				# delay), so timestamps are later than the actual time
				# the data came in, but the 1st sample should really be
				# zero..
				adshift = d.ts
				
			# compute timestamp in secs
			ts = (float(d.ts) - t0 - adshift) / float(h.ADFrequency)
			
			for i in range(len(d.waveform)):
				# convert waveform value to voltage (from plexon docs,
				# this is corret for file version >= 103 ONLY!)
				# note that refs for h.slow via d.Channel are correct, since
				# 'channel' values are 0-based for lfp..
				v = float(d.waveform[i])
				v = (v * h.SlowMaxMagnitudeMV) / \
					(0.5 * (2.0**h.BitsPerSlowSample) * \
					 h.slows[d.Channel].Gain * h.slows[d.Channel].PreAmpGain)

				# the +1 on d.Channel
				lfpout.write("%d\t%d\t%f\t%f\n" % \
							 (trial_number, d.Channel+1, \
							  1000.0 * (ts + (float(i) / float(h.slow_adfreq))),
							  1000.0 * v))
				nsamps += 1

		elif spikes and d.Type == PL_SPIKE and (not t0 is None):
			# compute timestamp in secs
			ts = (float(d.ts) - t0) / float(h.ADFrequency)
			spikeout.write("%d\t%d\t%d\t%f\n" % 
						   (trial_number, d.Channel, d.Unit, 1000.0 * ts))
			nspikes += 1
			for i in range(len(d.waveform)):
				# convert waveform value to voltage (from plexon docs,
				# this is corret for file version >= 103 ONLY!)
				# note that need to -1 to access h.Channels using d.Channel
				# since 'channel' values are 1-based for spike data..
				v = float(d.waveform[i])
				v = (v * h.SpikeMaxMagnitudeMV) / \
					(0.5 * (2.0**h.BitsPerSpikeSample) * \
					 h.channels[d.Channel-1].Gain * h.SpikePreAmpGain)
				spwout.write("%d\t%d\t%d\t%d\t%f\t%d\n" % \
						  (trial_number, d.Channel, d.Unit, \
							  i, 1000.0 * (ts + (i / float(h.ADFrequency))),
							  1000.0 * v))
				nwavesamps += 1
			spwout.write("%d\t%d\t%d\tNaN\tNaN\tNaN\n" % \
						 (trial_number, d.Channel, d.Unit))

	sys.stderr.write('%d trials\n' % trial_number)
	sys.stderr.write(' %d spikes\n' % nspikes)
	sys.stderr.write(' %d spike waveform samples\n' % nwavesamps)
	sys.stderr.write(' %d slow samples\n' % nsamps)
	
	f.close()
	
	spikeout.close()
	lfpout.close()
	spwout.close()
	hdrout.close()
	
	return 1
		

if __name__ == '__main__':
	from optparse import OptionParser

	p = OptionParser('usage: %prog [ options] plx-file')

	# flag options (store_true is for flags)
	p.add_option('-v', '--verbose', dest='dump',
				 action='store_true', default=0,
				 help='dump all header info')
	p.add_option('-i', '--info', dest='info',
				 action='store_true', default=0,
				 help='info on channels')
	
	
	# options with mandatory arguments
	p.add_option('-p', '--prefix', dest='prefix',
				 action='store', type='string', default=None,
				 help='file prefix for ascii dump files')

	(options, args) = p.parse_args()

	try:
		if len(args) != 1:
			p.error('must specify .plx file')
		elif options.info:
			info(args[0])
		else:
			xall(args[0], options.prefix)
	except NotPlx:
		sys.stderr.write('"%s" is not a plx file\n' % args[0])
		sys.exit(1)

