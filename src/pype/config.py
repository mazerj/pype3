# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""Simple 'config' file parser class

Author -- James A. Mazer (mazerj@gmail.com)

"""

import sys
import os
import posixpath
import string
import types

class Config(object):
	def __init__(self, fname=None):
		self.docdict = {}
		if fname:
			self.dict = self.load(fname)
		else:
			self.dict = {}

	def get(self, name, default=None):
		try:
			return self.dict[name]
		except KeyError:
			return default

	def iget(self, name, default=None):
		try:
			value = self.dict[name]
		except KeyError:
			value = default
		try:
			return int(value)
		except ValueError:
			return None
		except TypeError:
			return None

	def fget(self, name, default=None):
		try:
			value = self.dict[name]
		except KeyError:
			value = default
		try:
			return float(value)
		except ValueError:
			return None

	def getdoc(self, key):
		try:
			return self.docdict[key]
		except KeyError:
			return None

	def set(self, key, value, override=None, doc=None):
		keyp = key in self.dict
		if (keyp and override) or (not keyp):
			self.dict[key] = value
			self.docdict[key] = doc

	def keys(self):
		return self.dict.keys()

	def show(self, f):
		keys = self.dict.keys()
		keys.sort()
		for k in keys:
			v = self.dict[k]
			vt = type(v)
			if (vt is types.StringType) and len(v) == 0:
				f.write('\t%s=<empty string>\n' % k)
			else:
				f.write('\t%s=%s %s\n' % (k, v, vt))

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

