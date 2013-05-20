# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""TDT connection interface object
"""

"""Revision History

Tue Jan 25 13:45:18 2011 mazer

- got rid of the hoop save/load stuff.. nobody uses it..

"""

import tdt

class Controller(object):
	def __init__(self, app, tdthost):
		self.tdtconnx = tdt.TDTClient(tdthost)
		self.app = app
		self._server = None
		self._tank = None
		self._block = None

	def settank(self, dirname, name):
		"""Send tank name (directory) to TDT.

		:param dirname: (string)

		:param name: (string)

		:return: (string) actual tank name

		"""
		# this will only work in IDLE or STANDBY mode, so do it 1st!

		td = self.tdtconnx.tdev
		tt = self.tdtconnx.ttank

		if not tt('CheckTank', '%s%s' % (dirname, name)):
			tt('AddTank', name, dirname)

		if td('SetTankName', '%s%s' % (dirname, name)) == 0:
			# circuit's probably not running, bail now..
			return None

		for x in [tdt.STANDBY, tdt.RECORD, tdt.PREVIEW]:
			td('SetSysMode', x)
			while td('GetSysMode') != x:
				pass

		tt('OpenTank', '%s%s' % (dirname, name), 'R')

		return td('GetTankName')

	def newblock(self, record=1):
		"""Tell TDT to start a new block in the current tank.

		:param record: (boolean) if true, new block is opened and
				data starts getting saved to new block, otherwise
				close block and set TDT to idle/standby mode.

		:return: (mult-val-ret) server, tank, block names

		"""
		(self._server,
		 self._tank, self._block) = self.tdtconnx.newblock(record=record)
		return (self._server, self._tank, self._block)

	def getblock(self):
		"""Query current block info.

		:return: (mult-val-ret) server, tank, block names

		"""
		tnum = self.tdtconnx.tnum()
		return (self._server, self._tank, self._block, tnum)

if __name__ == '__main__':
	sys.stderr.write('%s should never be loaded as main.\n' % __file__)
	sys.exit(1)
