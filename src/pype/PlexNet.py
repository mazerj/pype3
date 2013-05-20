#!/usr/bin/env python
# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""Basic interface to Plexon network API

The plexon network API is massively broken, but this will get
you some of the data in a pure-python application.

Author -- James A. Mazer (james.mazer@yale.edu)
"""

"""Revision History
"""


import sys
import struct
import socket
import threading
from guitools import Logger
from PlexHeaders import Plex

class PlexNet(object):
	def __init__(self, host, port=6000, waveforms=0):
		self._status = 'No Connection'

		self.host = host
		self.port = port
		self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self._sock.connect((self.host, self.port))
		self._status = 'connected'

		self._last_NumMMFDropped = 0
		self._mmf_drops = 0
		self._tank = []
		self._neurons = {}

		packet = [0] * 6
		packet[0] = Plex.PLEXNET_CMD_SET_TRANSFER_MODE
		packet[1] = 1					# want timestamps?
		packet[2] = waveforms			# want waveforms?
		packet[3] = 0					# want analog data?
		packet[4] = 1					# chanel from
		packet[5] = 16					# chanel to

		self._put('6i', packet)
		data = self._get()

		# these values are precomputed to speed things up:
		self._db_header = 'iiii'
		self._db_header_size = struct.calcsize(self._db_header)
		self._db_size = struct.calcsize(Plex.fPL_DataBlockHeader)

		self._lock = threading.Lock()
		Logger("PlexNet: starting background retrieval thread\n")
		threading.Thread(target=self.run).start()

	def __del__(self):
		try:
			self._put('h', [Plex.PLEXNET_CMD_DISCONNECT,])
		except:
			pass
		self._sock.close()

	def _put(self, format, packet):
		# pack data into binary format for transfer
		bin = apply(struct.pack, [format,] + packet)

		# pad packet to full length with zeros
		bin = bin + "\0" * (Plex.PACKETSIZE-len(bin))
		self._sock.send(bin)

	def _get(self):
		nbytes = 0
		while nbytes < Plex.PACKETSIZE:
			data = self._sock.recv(Plex.PACKETSIZE)
			nbytes = nbytes + len(data)
		return data

	def start_data(self):
		self._put('i', [Plex.PLEXNET_CMD_START_DATA_PUMP,])

	def stop_data(self):
		self._put('i', [Plex.PLEXNET_CMD_STOP_DATA_PUMP,])

	def pump(self):
		data = self._get()

		(unknown1, unknown2, NumServerDropped, NumMMFDropped) = \
				   struct.unpack(self._db_header, data[:self._db_header_size])

		#print unknown1, unknown2, NumServerDropped, NumMMFDropped

		if (NumMMFDropped - self._last_NumMMFDropped) > 0:
			self._last_NumMMFDropped = NumMMFDropped
			Logger("PlexNet: Warning, MMF dropout!!\n" +
				   "		 Consider power cycling MAP box...\n")
			self._mmf_drops = self._mmf_drops + 1

		if NumServerDropped > 0:
			Logger("PlexNet: NumServerDropped=%d\n" % NumServerDropped +
				   "		 This should never happen. Tell Jamie,\n" +
				   "		 then quit and restart Plexon programs.\n")

		pos = 16
		events = []
		while (pos + self._db_size) <= Plex.PACKETSIZE:
			db = struct.unpack(Plex.fPL_DataBlockHeader,
							   data[pos:pos+self._db_size])

			if db[0] == 0:			# db[1] Type // empty block
				print "?empty?"
				break

			if db[0] == -1:
				# end of packet
				break
			pos = pos + self._db_size

			(Type, UpperTS, TimeStamp, Channel, \
			 Unit, nWaveforms, nWordsInWaveform) = db

			# compute 5 byte timestamp as L type (long int)
			ts = (1L<<24)+TimeStamp

			if nWaveforms > 0:
				# waveform samples/words are 2-bytes each
				wavesize = nWaveforms * nWordsInWaveform
				waveform = data[pos:pos+(wavesize*2)]
				waveform = struct.unpack('h' * (len(waveform)/2), waveform)
				pos = pos + (wavesize * 2)
			else:
				waveform = None

			# note: if type==4, then this is a non-waveform event, like
			# the trigger pulse. Channel contains the event id. I think
			# it's 258 for start and 259 for stop trial/recording.
			events.append((Type, Channel, Unit, ts, waveform))

		return events

	def run(self):
		self.start_data()
		while 1:
			# query the socket for a new set of plexon evens
			eventlist = self.pump()

			# Now crunch through the events. The appended None dummy event
			# will force a check on the tank status w/o requiring an
			# additional acquire/release cylce on the lock. This allows
			# the thread to correctly terminate and allow pype to cleanly
			# exit when no spike data is coming in.
			for e in eventlist + [None]:
				try:
					self._lock.acquire()
					if self._tank is None:
						# this is the termination signal from the main thread
						return
					if e is not None:
						self._tank.append(e)
						self._neurons[(e[1],e[2])] = 1
				finally:
					if self._tank is not None:
						self._status = "[%05d]" % len(self._tank)
					self._lock.release()
		self.stop_data()

	def drain(self, terminate=0):
		self._lock.acquire()
		t, self._tank, ndrops = self._tank, [], self._mmf_drops
		self._mmf_drops = 0
		if terminate:
			# signal collection thread to terminate next possible chance
			self._tank = None
		self._lock.release()
		return t, ndrops

	def neuronlist(self, clear=0):
		"""Get list of recently seen neurons"""
		self._lock.acquire()
		n = self._neurons.keys()
		if clear:
			self._neurons = {}
		self._lock.release()
		return n

	def status(self):
		self._lock.acquire()
		s = self._status
		self._lock.release()
		return s

if __name__ == '__main__':
	# try training plexon buffers for testing...
	import time
	p = PlexNet("192.168.1.111", 6000)
	for i in range(3):
		time.sleep(1)
		events, ndrops = p.drain()
		print "%d events (%d)" % (len(events), ndrops)
	p.drain(terminate=1)
	print "drained."
