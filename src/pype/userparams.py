# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""Simple Config file parser and accessor class

Author -- James A. Mazer (james.mazer@yale.edu)

"""

"""Revision History

- Tue Aug 13 17:23:06 2002 mazer

  - removed save/iget/fget etc from UserParams class

  - changed UserParams to Config
"""

import sys
import os
import posixpath
import string

class Config(object):
	def __init__(self, fname):
		self.dict = self.load(fname)

	def get(self, name, default=None):
		try:
			return self.dict[name]
		except KeyError:
			return default

	def set(self, key, value, override=None):
		k = self.dict.has_key(key)
		if (k and override) or (not k):
			self.dict[key] = value

	def load(self, fname):
		d = {}
		if posixpath.exists(fname):
			f = open(fname, 'r')
			while 1:
				l = f.readline()
				if not l: break
				l = l[:-1]
				try:
					ix = string.index(l, '#')
					l = l[0:ix]
				except ValueError:
					pass
				try:
					ix = string.index(l, ':')
					name = string.strip(l[0:ix])
					value = string.strip(l[(ix+1):])
					d[name] = value
				except ValueError:
					pass
			f.close()
		return d

if __name__=='__main__' :
	pass
