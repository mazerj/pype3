# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

# tdev_/ttank_invoke --> tdev/ttank

"""
Think about something like this for the pype side. Would
really simplify coding...

 >> class Foo:
 >>     def __init__(self):
 >>         print 'init'
 >> 
 >>     def callit(self, method, *args, **kw):
 >>         print method, args, kw
 >> 
 >>     def __getattr__(self, key):
 >>         def func(*args, **kw):
 >>             return self.callit(key, *args, **kw)
 >>         return func
 >> 
 >> x = Foo()
 >> x.foobar(2, 3, 4, foo=1)
"""

__author__   = '$Author: mazer $'
__date__     = '$Date: 2009-05-25 16:00:02 -0400 (Mon, 25 May 2009) $'
__revision__ = '$Revision: 339 $'
__id__       = '$Id: tdt2.py 339 2009-05-25 20:00:02Z mazer $'

import sys
import os
import time
import socket
import cPickle
import struct
import traceback
import types
import string

try:
	import win32com.client
	WINDOWS = 1
except ImportError:
	WINDOWS = 0

TDEVACC = 'TDevAcc'
TTANK   = 'TTank'

PORT    = 10000							# default inital TCP port 
DEBUG   = 1								# debug mode?

# OpenEx run modes:
IDLE    = 0								# dsp completely idle
STANDBY = 1								# running, no display, no tank..
PREVIEW = 2								# running, not saving to tank
RECORD  = 3								# running and saving all data
MODES = { IDLE:'IDLE', STANDBY:'STANDBY',
		  PREVIEW:'PREVIEW', RECORD:'RECORD'}

class TDTError(Exception): pass

class Log:
	fp = None
	def __init__(self, msg=None):
		if msg:
			for ln in string.strip(msg).split('\n'):
				s = '%02d:%02d:%02d ' % time.localtime(time.time())[3:6]
				#s = s + '%s: %s\n' % (os.path.basename(sys.argv[0]), ln)
				s = s + '%s\n' % (ln,)
				if DEBUG:
					sys.stderr.write(s)
				if Log.fp:
					Log.fp.write(s)
					Log.fp.flush()

	def file(self, fname):
		if Log.fp:
			Log.fp.close()
		Log.fp = open(fname, 'a')


class MySocket:
    def __init__(self, clientsocket=None, host=None, port=None):
        if (clientsocket is None) and host and port:
            clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            clientsocket.connect((host, port))
		clientsocket.settimeout(None)
        self.sockfd = clientsocket
        
    def recv(self, packetsize=1024):
        # returns None when connection is closed..
        buf = self.sockfd.recv(struct.calcsize('!I'))
        if len(buf) == 0:
            return None
        N = struct.unpack('!I', buf)[0]
        data = ''
        while len(data) < N:
            packet = self.sockfd.recv(packetsize)
            data = data + packet
        return data

    def send(self, data):
        self.sockfd.send(struct.pack('!I', len(data)))
        return self.sockfd.sendall(data)

def strcleanup(a):
	import string, types
	newa = []
	for s in a:
		if type(s) is types.StringType:
			s = string.replace(s, '\\', '\\\\')
		newa.append(s)
	return tuple(newa)
	
if WINDOWS:
	from threading import Thread

	class ServersideClientHandler(Thread):
		COUNT = 0
		# ...windows side only..
		def __init__(self, clientsocket, src):
			Thread.__init__(self)

			self.s = MySocket(clientsocket)
			self.src = src

			Log('Connection from %s\n' % (self.src,))

			# these are not thread safe -- must be called in INIT,
			# not in run..
			self.TDevAcc = win32com.client.Dispatch('TDevAcc.X')
			self.TTank = win32com.client.Dispatch('TTank.X')

			ServersideClientHandler.COUNT = ServersideClientHandler.COUNT + 1

		def run(self):
			# result coding:
			#              success: (1, ...descr...)
			#          eval errors: (0, ...descr...)
			# server/client errors: (-1, ...descr...)
			#

			Log('Received connection from %s\n' % (self.src,))

			# these guys must be called in RUN, but not INIT..
			if self.TDevAcc.ConnectServer('Local'):
				self.s.send(cPickle.dumps(1))
				Log('thread connected to TDevAcc.X\n')
			else:
				self.TDevAcc = None
				self.s.send(cPickle.dumps(0))
				Log('thread failed to connect to TDevAcc.X');

			if self.TTank.ConnectServer('Local', 'Me'):
				self.s.send(cPickle.dumps(1))
				Log('thread connected to TTank.X\n')
			else:
				self.TTank = None
				self.s.send(cPickle.dumps(0))
				Log('thread failed to connect to TTank.X\n')

			errcode, descr = None, None
			try:
				while True:
					buff = self.s.recv()
					if buff is None:
						break
					cmd = cPickle.loads(buff)
					result = None
					(obj, method, args) = cmd
					#args = strcleanup(args)
					Log('Recieved command: %s\n' % ((obj,method,args),))
					if obj == TDEVACC:
						iobj = self.TDevAcc
					elif obj == TTANK:
						iobj = self.TTank
					else:
						result = (-1, 'invalid call object: %s' % (obj,))
						
					if not result and not iobj:
						result = (-1, '%s not available' % (obj,))
					elif not result:
						try:
							fn = getattr(iobj, method)
							try:
								result = (1, apply(fn, args))
							except:
								errinfo = sys.exc_info()
								LOG('Eval/Apply Exception:\n')
								LOG(traceback.format_exc(errinfo[2]))
								result = (0, result[errinfo:1])
						except AttributeError:
							result = (-1, 'invalid method: %s.%s' % \
									  (obj, method,))
					Log('result: %s\n' % (result,))
					self.s.send(cPickle.dumps(result))
					
			except socket.error, value:
				(errorcode, descr) = value
			finally:
				if self.TTank:
					self.TTank.CloseTank()
					self.TTank.ReleaseServer()
				if self.TDevAcc:
					if self.TDevAcc.CheckServerConnection():
						self.TDevAcc.CloseConnection()		
			if descr:
				Log('Error: %s\n' % (descr,))
			ServersideClientHandler.COUNT = ServersideClientHandler.COUNT - 1
			
			Log('Connection from %s closed (%d left)\n' % \
				(self.src, ServersideClientHandler.COUNT,))


	def RunServer(port=PORT):
		serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		try:
			serversocket.bind(('',port))
		except ValueError,e:
			Log(e)
			return
		serversocket.listen(5)
		Log('Listening on port #%d\n' % (port,))
		while 1:
			(clientsocket, address) = serversocket.accept()
			ServersideClientHandler(clientsocket,address).start()

	if __name__ == '__main__':
		Log().file('C:\\tdt2.log')
		Log('-----------------------------------------\n')
		RunServer()
		LOG('RunSever() returned -- should never happen!\n')
		#sys.stderr.write('<HIT RETURN TO QUIT>'); sys.stdin.readline()
		sys.exit(1)
else:
	class TDTClient:
		def __init__(self, server, port=PORT):
			self.server = server
			try:
				self.s = MySocket(host=server, port=port)
			except socket.error:
				# tdt's not available -- reraise the exception for now..
				raise

			self.gotTDevAcc = cPickle.loads(self.s.recv())
			self.gotTTank = cPickle.loads(self.s.recv())
			if DEBUG:
				sys.stderr.write('tdtstatus: circuit=%d tank=%d\n' % \
								 (self.gotTDevAcc, self.gotTTank, ))

		def __repr__(self):
			return '<TDTClient server=%s TDevAcc=%d TTank=%d>' % \
				   (self.server, self.gotTDevAcc, self.gotTTank)

		def _sendtuple(self, cmdtuple):
			"""
			Send a command string for remove evaluation to the server.
			Command string (cmd) should be a valid python expression
			that can be eval'ed in the remote envrionment. Access to
			the Tucker-Davis API is via:

			- TDevAcc (for the direct DSP interface), or,

			- TTank (for access to the data tank)

			The return value is a pair: (statusFlag, resultValue), where
			statusFlag is 1 for normal evaluation and 0 for an error and
			resultValue is the actual value returned by the function
			call (the value is pickled on the Server side and returns, so
			data typing should be correctly preserved and propagated.
			"""
			try:
				self.s.send(cPickle.dumps(cmdtuple))
				p = self.s.recv()
				(ok, result) = cPickle.loads(p)
			finally:
				pass
			return (ok, result)

		def _invoke(self, which, method, args):
			if which == TDEVACC and not self.gotTDevAcc:
				raise TDTError, \
					  'No %s.X available; cmd=<%s>' % (which, method,)
			if which == TTANK and not self.gotTTank:
				raise TDTError, \
					  'No %s.X available; cmd=<%s>' % (which, method,)
			
			if DEBUG:
				sys.stderr.write(repr(('exec:', which, method, args,)))
			(ok, result) = self._sendtuple((which, method, args,))
			if DEBUG:
				sys.stderr.write('--> %s\n' % ((ok, result),))
				
			if ok:
				return result
			else:
				raise TDTError, \
					  '%s.X Error; cmd=<%s>; err=<%s>' % (which, method, result)
		

		def tdev(self, method, *args):
			return self._invoke(TDEVACC, method, args)

		def ttank(self, method, *args):
			return self._invoke(TTANK, method, args)

		def mode(self, mode=None, name=None, wait=None):
			"""
			Query current run mode for the TDT device.

			Run modes are defined by TDT as follows (and also declared
			as global constants/vars in this file)::

			  IDLE = 0		# dsp completely idle
			  STANDBY = 1	# running, no display, no tank..
			  PREVIEW = 2	# running, not saving to tank
			  RECORD = 3	# running and saving all data

			"""
			if mode is None:
				r = self.tdev('GetSysMode')
			else:
				self.tdev('SetSysMode', mode)
				while 1:
					r = self.tdev('GetSysMode')
					if (not wait) or (r == mode):
						break
			if name:
				r = MODES[r]
			return r

		def tnum(self, reset=None):
			"""
			Read trial count, or if reset==1 reset the counter to zero. This
			should really be done when OpenEx is in standby mode..
			"""
			if reset:
				self.tdev('SetTargetVal', 'Amp1.TNumRst', 1.0)
				while 1:
					if self.tdev('GetTargetVal', 'Amp1.TNum') == 0:
						break
			return self.tdev('GetTargetVal', 'Amp1.TNum')

		def chaninfo(self):
			"""
			Figure out number of analog channels and length of spike snippet.
			The actual length of the snippet is hoopsize/3 points, since
			cSnip refers to the hoops, not the waveform.
			"""
			n = 1
			while 1:
				s = self.tdev('GetTargetSize',
									 'Amp1.cSnip~%d' % n)
				if s < 0:
					self.tdev('SetSysMode', PREVIEW)
					s = self.tdev('GetTargetSize',
										 'Amp1.cSnip~%d' % n)
				if s == 0:
					break
				if n == 1:
					hoopsize = s
				n = n + 1
			return (n-1, hoopsize/3)

		def getblock(self):
			"""
			Query current block info -- this is enough info to find the current
			data record later (assuming tank doesn't get deleted...)
			"""
			return (self.server,
					self.tdev('GetTankName'),
					self.ttank('GetHotBlock'),
					self.tdev('GetTargetVal', 'Amp1.TNum'))

		def newblock(self, record=1):
			"""
			Start a new block in the current tank. Each block corresponds
			to a single run. If record==1, then a new block is started for
			recording. Otherwise, the current block is terminated and the
			system is left in standby mode.

			Basically, you should call newblock(record=1) at the start
			of a run and then neweblock(record=0) at the end.

			NOTE: In IDLE and STANDBY mode, GetHotBlock() returns an empty
			string, in PREVIEW mode 'TempBlk' and in RECORD mode a true
			block name (typically 'Block-NNN')

			RETURNS: (servername, tankname, blockname); this should be enough
			info to track down the location of the record no matter what..
			"""
			# set OpenEx to STANDBY and wait for this to register in the
			# tank as a change in the block name to '' (or if it was already
			# in STANDBY mode, we're good to go..

			self.mode(PREVIEW)

			tank = self.tdev('GetTankName')
			err = self.ttank('OpenTank', tank, 'R')

			while 1:
				oldblock = self.ttank('GetHotBlock')
				if str(oldblock) == 'TempBlk' or len(oldblock) == 0:
					break
				sys.stderr.write('waiting1...')

			# actually, I do not think this is necessary, as long as the
			# tnum's are unique, so just let it count up continuously..
			# reset the trial counter
			# self.tnum(reset=1)

			# switch back to record mode and wait for this to get into the
			# tank, so we can store the block name for easy access later..
			if record:
				# should probably wait here (wait=1) to make sure we
				# really switch to RECORD mode.. this seems to be the problem..
				self.mode(RECORD)
				while 1:
					newblock = self.ttank('GetHotBlock')
					if not (newblock == oldblock) and len(newblock) > 0:
						break
					sys.stderr.write('waiting2: oldblock=<%s> newblock=<%s>' %
									 (oldblock, newblock,))
			else:
				self.mode(PREVIEW)
				newblock = self.ttank('GetHotBlock')

			# and return the tank & block name --> this is enough info to
			# find the record later..
			tank = self.tdev('GetTankName')
			return (self.server, str(tank), str(newblock))


		def sortparams(self, params=None):
			"""
			Get or set current sort parameters (aka hoop settings). If called
			with no arguments, current settings are returned. Otherwise, the
			params arg specifies a new set of settings to setup
			"""

			# just assume 16 channels to be safe...
			nchans = 16
			sniplen = -1
			while sniplen < 0:
				sniplen = self.tdev('GetTargetSize',
										   'Amp1.cSnip~%d' % 1)
				if sniplen < 0:
					# sniplen means circuit hasn't been started up yet, so
					# start it going and try again..
					self.tdev('SetSysMode', PREVIEW)

			if params is None:
				params = {}
				for n in range(1, nchans+1):
					try:
						params[n, 'thresh'] = \
								  self.tdev('GetTargetVal',
												   'Amp1.aSnip~%d' % n)
					except ValueError:
						# not sure what this is --> comes back as -1.#IND..
						params[n, 'thresh'] = 1.0
					params[n, 'hoops'] = \
							  self.tdev('ReadTargetV',
											   'Amp1.cSnip~%d' % n,
											   0, sniplen)
				return params
			else:
				for n in range(1, nchans+1):
					t = params[n, 'thresh']
					h = params[n, 'hoops']
					self.tdev('SetTargetVal', 'Amp1.aSnip~%d' % n, t)
					self.tdev('WriteTargetVEX',
									 'Amp1.cSnip~%d' % n, 0, 'F32', h)

	if __name__ == '__main__':
		import pypedebug
		t = TDTClient(server='tdt1.mlab.yale.edu')
		sys.stdout.write('t=TDTClient()\n')
		pypedebug.keyboard()
		sys.exit(1)

