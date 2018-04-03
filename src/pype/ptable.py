# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""Parameter tables with type validation

Parameter table (aka worksheet) implementation. This module
provides a standard way to create task-specific parameter
tables to be filled out by the user and passed into running
tasks.

Validator function (is_int, is_pdf etc) are provided for
a number of common cases. If you want to write your own,
the validation function must be a function two args, eg:

  def is_int(s, evaluate=None): ...

s is a string to validate -- when evaluate is None, then
the function simply decides whether or not s is in a valid
form and returns True or False. If evaluate is True, then
the validator function should return the actual valid of
the string -- ie, for is_int, return a validated integer
(not a string, but an actual integer).

Author -- James A. Mazer (mazerj@gmail.com)

"""

from Tkinter import *
import Pmw
import string
import types
import re
import os
import posixpath
import cPickle
import ConfigParser
import numpy as np

import pype
import pype_aux
from guitools import *
from filebox import Open, SaveAs
from guitools import Logger

from pypedebug import keyboard


# (custom) validator functions must return one of these:
VALID = Pmw.OK
INVALID = Pmw.PARTIAL

_KEEPLOCKED = -1

def _unpack_slot(slot):
	(name, default, validate, descr, runlock) = [None] * 5
	if len(slot) < 1:
		raise FatalPypeError, 'ptable:_unpack_slot bad worksheet slot'
	name = slot[0]
	if len(slot) > 1: default = slot[1]
	if len(slot) > 2: validate = slot[2]
	if len(slot) > 3: descr = slot[3]
	if len(slot) > 4: runlock = slot[4]

	return (name, default, validate, descr, runlock)

class ParamTable(object):
	_list = []

	def __init__(self, parent, table, file=None,
				 decorate=1, locks=1, allowalt=True, loadable=1):
		"""Parameter management table class"""

		if parent is None and table is None: return

		self._parent = parent
		self._table = table
		self._entries = {}
		self._locks = {}
		self._file = file
		self._allowalt = allowalt

		# got to check for duplicates before this table's added
		# into the global list.
		for slot in self._table:
			(name, default, validate, descr, runlock) = _unpack_slot(slot)
			if default is not None:
				found = self.find(name, show=0)
				for (duptab, dupname, duprow) in found:
					if name == dupname:
						Logger('ptable: ''%s'' dup in %s - priority '
							   'to %s\n' % (name, duptab.tablename, file))
		ParamTable._list.append(self)

		self.tablename = 'noname'

		if file:
			try:
				self._file = pype.subjectrc(file)
			except KeyError:
				self._file = file
			self.tablename = file
		else:
			self._file = None

		self.balloon = Pmw.Balloon(parent, master=1, relmouse='both')

		f = Frame(parent)
		f.pack(expand=0, fill=X, side=TOP)
		self.frame = f

		if self._file:
			Button(f, text='Save',
				   command=self.save).pack(expand=0, fill=X, side=LEFT)
		if decorate:
			Button(f, text="View",
				   command=self.view).pack(expand=0, fill=X, side=LEFT)
			
		if loadable:
			Button(f, text="Load (<-datafile)",
				   command=self.frompypefile).pack(expand=0, fill=X, side=LEFT)

			
		f = Pmw.ScrolledFrame(parent)
		f.pack(expand=1, fill=BOTH)

		entries = []
		self.names = []
		nrow = 0
		for slot in self._table:
			nrow = nrow + 1
			(name, default, validate, descr, runlock) = _unpack_slot(slot)

			lf = Frame(f.interior())
			lf.pack(expand=1, fill=X)
			if default is None and validate is None:
				e = Label(lf, text=name, bg='yellow', anchor=W)
				e.pack(expand=1, fill=X)
			elif isinstance(validate, types.TupleType):
				tmpf = Frame(lf, height=12, width=12)
				tmpf.pack(side=LEFT)
				e = Pmw.RadioSelect(lf,
									buttontype = 'radiobutton',
									labelpos = 'w',
									label_text = name + ':',
									pady=0, padx=2)
				e.pack(anchor=W)
				for v in validate:
					e.add(v)
				e.invoke(default)
				self._entries[name] = e
				entries.append(e)
			elif isinstance(validate, types.DictType):
				tmpf = Frame(lf, height=12, width=12)
				tmpf.pack(side=LEFT)
				e = Pmw.RadioSelect(lf,
									buttontype = 'radiobutton',
									labelpos = 'w',
									label_text = name + ':',
									pady=0, padx=2)
				e.pack(anchor=W)
				for v in validate:
					e.add(v)
				e.invoke(default)
				self._entries[name] = e
				self._entries[(name,'dict')] = validate
				entries.append(e)
			else:
				e = Pmw.EntryField(lf,
								   labelpos = 'w',
								   label_text = name + ':',
								   validate = validate,
								   value = default)
				if descr:
					self.balloon.bind(e, '%d: %s' % (nrow, descr))
				else:
					self.balloon.bind(e, '%d: %s' % (nrow, '???'))
				e.component('entry').configure(bg='white', width=75)
				tmpf = Frame(lf, height=12, width=12)
				tmpf.pack_propagate(0)
				tmpf.pack(side=LEFT)
				if locks:
					if runlock == _KEEPLOCKED:
						lockbut = Label(tmpf, text = '')
					else:
						lockbut = Button(tmpf, text = '',
										 command=lambda n=name:
												self.lockfield(n, toggle=1))
					lockbut.pack(fill=BOTH, expand=1)

					if runlock == _KEEPLOCKED:
						# usr can NEVER set this value!
						e.component('entry').configure(state=DISABLED)
						e.component('label').configure(fg='red')
						lockbut.configure(state=DISABLED)
				self._entries[name] = e
				entries.append(e)
				self.names.append(e)
				e.pack(expand=1, anchor=W, fill=X, side=RIGHT)

		Pmw.alignlabels(entries)

		if self._file:
			self.load()

	def __del__(self):
		if self in ParamTable._list:
			ParamTable._list.remove(self)

	def addbutton(self, text='userdef', command=None):
		"""Add user-defined button to param table.

		:param text: (string) text of button label

		:param command: (function) function to call when clicked

		:return: Button

		"""
		b = Button(self.frame, text=text, fg='green', command=command)
		b.pack(expand=0, fill=X, side=LEFT)
		return b

	def find(self, name, show=1):
		"""Find parameter tables fields that (partial) match name.

		:param name: (string) name of field find/match

		:param show: (bool) popup table with found entries?

		:return: list of matching tables [(table, slotname, index), ...]

		"""

		intabs = []
		for pt in ParamTable._list:
			n = 0
			for slot in pt._table:
				n = n + 1
				if string.find(slot[0], name) >= 0:
					intabs.append((pt, slot[0], n,))
					if show:
						pt._parent._show()
		return intabs

	def _get(self, evaluate=1, mergewith=None, readonly=1):
		"""Retrieve parameter table current state.

		:param evaluate: (bool) if true, then table slots are 'evaluated'
				before returned, otherwise the raw, unprocessed strings
				are returned.

		:param mergewith: (dict) optional dictionary to start with; values
				from the table will be merged into this existing dictionary
				and the merged dictionary returned.

		:param readonly: (bool) validate 'readonly' fields?

		:returns: (2-tuple) Returned valiue is a pair (valid, dict),
				where dict contains all the values in the parameter
				table.	Dictionary keys are the slot names. Default is
				to evaluate the parameters, which means they should
				come back correctly) typed (ie, is_int's should come
				back as Integers).

		"""

		if mergewith:
			d = mergewith
		else:
			d = {}

		for slot in self._table:
			(name, default, validate, descr, runlock) = _unpack_slot(slot)
			if default is None:
				continue
			v = self.query(name)
			if evaluate:
				# Wed Mar 11 11:08:13 2009 mazer
				# store raw string version of param in dictionary in addition
				# to the evaluated version for future reference..  only do
				# this if evaluating
				d[name+'_raw_'] = v
				if validate and not (isinstance(validate, types.TupleType) or
									 isinstance(validate, types.DictType)):
					(r, v) = apply(validate, (v,), {"evaluate": 1})
					if (runlock == _KEEPLOCKED) and not readonly:
						continue
					elif r != VALID:
						return (0, name)
			d[name] = v
		return (1, d)

	def lockfield(self, name, toggle=None, state=DISABLED):
		"""Lock specififed row of table.

		:return: nothing

		"""
		try:
			w = self._entries[name].component('entry')
		except KeyError:
			# obsolete field...
			return

		if toggle:
			if w.cget('state') == DISABLED:
				state = NORMAL
			else:
				state = DISABLED
		w.configure(state=state)
		self._locks[name] = state

	def keys(self):
		"""Get list of keys (ie, row names) for this table/

		"""
		return self._entries.keys()

	def query(self, qname):
		"""Retrieve single value from the parameter table by name
		without validation.

		:param qname: (string) slot name

		:return: (string) current value

		"""
		try:
			v = self._entries[qname].get()
		except AttributeError:
			v = self._entries[qname].getvalue()

		if (qname,'dict') in self._entries:
			return self._entries[(qname,'dict')][v]
		else:
			return v

	def queryv(self, qname):
		"""Retrieve single value from the parameter table by name
		with validation.

		:param qname: (string) slot name

		:return: (variable) validated current value -- might not be string!

		"""
		for slot in self._table:
			(name, default, validate, descr, runlock) = _unpack_slot(slot)
			if default is None:
				continue
			if name is qname:
				v = self.query(name)
				if validate and not (isinstance(validate, types.TupleType) or
									 isinstance(validate, types.DictType)):
					(r, v) = apply(validate, (v,), {"evaluate": 1})
					if r != VALID:
						(r, v) = apply(validate, (default,), {"evaluate": 1})
				return v
		warn('ptable:queryv',
			 'No value associated with "%s".' % qname)
		return None

	def set(self, name, value):
		"""Set current value for named row.

		:param name: (string) slot name

		:param value: (string) new value

		:return: nothing

		Warning: this might not work for Dict and Tuple fields anymore..

		"""
		self._entries[name].setentry(value)

	def save(self, file=None, remove=1):
		"""Save state for table to file.

		:param file: (string) If specified, name of output file (goes in
				subject-specific-dir).

		:return: nothing

		"""
		if file is None:
			file = self._file

		tmpfile = file + '.tmp'
		f = open(tmpfile, 'w')

		(ok, x) = self._get(evaluate=0)

		c = ConfigParser.ConfigParser()
		c.add_section('params')
		c.add_section('locks')
		for k in x.keys():
			c.set('params', k, x[k])
			if k in self._locks:
				if self._locks[k] == DISABLED:
					c.set('locks', k, 1)
					lock = 1
		c.write(f)
		f.close()
		os.rename(tmpfile, file)

		if self in ParamTable._list:
			ParamTable._list.remove(self)


	def load(self, file=None):
		"""
		Load pickled table database - note that the pickled dictionary
		will be unpickled, but only those values referenced in the table
		will actually be used.	The rest (ie, obsolete) are discarded.
		This way you can safely inherit from previous modules w/o
		accumulating excess garbage.
		"""
		if file is None:
			file = self._file

		if self._load(file=file) == 1:
			return

		if not self._allowalt:
			return

		try:
			initialdir = pype.subjectrc('')
		except KeyError:
			initialdir = os.getcwd()

		while 1:
			(file, mode) = Open(initialdir=initialdir,
								initialfile=self.tablename,
								text='No saved parameter\n'+
								'Select task to inherit params or\n'+
								'Cancel to accept defaults.')
			if file is None:
				return
			if self._load(file=file) == 1:
				sys.stderr.write("Loaded params from '%s'\n" % file)
				return

	def _load(self, file=None):
		# try all the load methods in order until one works..
		# or if none work, return 0..
		for method in (self._load_cfg, self._load_txt, self._load_pickle):
			if method(file=file):
				if not method  == self._load_cfg:
					sys.stderr.write("Warning: updating '%s'\n" % file)
				return 1
		return 0

	def _load_cfg(self, file=None):
		"""Load config-file base ptable state file.

		"""

		try:
			f = open(file, 'r')
		except IOError:
			return 0

		c = ConfigParser.ConfigParser()
		try:
			c.readfp(f)
		except:
			c = None
		f.close()
		if c is None:
			return 0

		for slot in self._table:
			(name, default, validate, descr, runlock) = _unpack_slot(slot)
			if default is None:
				continue
			try:
				val = c.get('params', name)
			except:
				sys.stderr.write('WARNING: %s:params:%s missing/corrupt\n' %
								 (os.path.basename(file), name))
				val = default

			if isinstance(validate, types.TupleType):
				try: self._entries[name].invoke(val)
				except ValueError: pass
			elif isinstance(validate, types.DictType):
				for k in validate.keys():
					if '%s'%validate[k] == val:
						try: self._entries[name].invoke(k)
						except ValueError: pass
			else:
				self._entries[name].setentry(val)

		if c.has_section('locks'):
			for (name, lockstate) in c.items('locks'):
				if int(lockstate):
					self.lockfield(name)

		return 1

	def _load_pickle(self, file=None):
		"""Backward compatibility only.

		"""
		try:
			f = open(file, 'r')
			x = cPickle.load(f)
			try:
				locks = cPickle.load(f)
			except EOFError:
				locks = {}
			f.close()
			for slot in self._table:
				(name, default, validate, descr, runlock) = _unpack_slot(slot)
				if default is None:
					continue
				if (isinstance(validate, types.TupleType) or
					isinstance(validate, types.DictType)):
					self._entries[name].invoke(x[name])
				else:
					try:
						self._entries[name].setentry(x[name])
					except KeyError:
						pass

			for k in locks.keys():
				self.lockfield(k, state=locks[k])

			return 1
		except IOError:
			return 0

	def _load_txt(self, file=None):
		"""Backward compatibility only.

		"""
		try:
			x = {}
			locks = {}

			f = open(file, 'r')
			while 1:
				line = f.readline()
				if not line: break
				source, key, lockstate, value = line.split('!!')
				# value has trailing \n
				x[key] = value[:-1]
				locks[key] = lockstate
			f.close()

			for slot in self._table:
				(name, default, validate, descr, runlock) = _unpack_slot(slot)
				if default is None:
					continue
				if (isinstance(validate, types.TupleType) or
					isinstance(validate, types.DictType)):
					self._entries[name].invoke(x[name])
				else:
					try:
						self._entries[name].setentry(x[name])
					except KeyError:
						pass
			for k in locks.keys():
				if len(locks[k]) > 0:
					self.lockfield(k, state=locks[k])
			return 1
		except IOError:
			return 0
		except ValueError:
			return 0

	def frompypefile(self):
		import filebox, pypedata
		
		(file, mode) = filebox.Open(initialdir=os.getcwd(),
									pattern='*.[0-9][0-9][0-9]',
									initialfile='', datafiles=1)
		if file:
			pf = pypedata.PypeFile(file)
			rec = pf.nth(0)
			if rec:
				s = ''
				keys = rec.params.keys()
				for k in self.keys():
					kraw = k + '_raw_'
					if kraw in keys:
						s = s + '%s = %s --> %s\n' % (k, self.query(k),
													rec.params[kraw])
						try:
							self.set(k, rec.params[kraw])
						except:
							# radio buttons etc..
							self._entries[k].invoke(rec.params[kraw])
				warn('Loaded values', s, astext=1)
		
		
	def view(self):
		"""View current contents of table (in a popup dialog box).

		:returns: nothing

		"""
		(ok, x) = self._get(evaluate=0)
		s = ''

		for slot in self._table:
			(name, default, validate, descr, runlock) = _unpack_slot(slot)
			if default is None: continue
			try:
				s = s + '%20s: %s\n' % (name, x[name])
			except KeyError:
				s = s + '%20s: %s\n' % (name, '<undefined>')
		warn('ptable:view', s, wait=None, astext=1)

	def check(self, mergewith=None):
		"""Validate parameter table.

		NOTE: This forces the user to actually make all the slots valid!

		:param mergewith: (dict) optional dictionary to start with; values
				from the table will be merged into this existing dictionary
				and the merged dictionary returned.

		:return: (dict) validated dictionary of all params

		"""
		while 1:
			(ok, P) = self._get(mergewith=mergewith)
			if self.tablename:
				w = "Check parameter table '%s'.\n" % self.tablename
			else:
				w = "Check parameter tables.\n"
			if not ok:
				warn('ptable:check', w +
					 "Field '%s' contains invalid data.\n\n" % P +
					 "Please fix and then click Continue.",
					 wait=1, grab=None)
			else:
				break
		return P

	def runlock(self, lock=1):
		"""Lock table (in preparation for a run.

		"""
		for slot in self._table:
			(name, default, validate, descr, runlock) = _unpack_slot(slot)
			if default:
				e = self._entries[name].component('label')
				if runlock == 1:
					if lock:
						e.configure(state=DISABLED)
					else:
						try:
							e.configure(state=self._locks[name])
						except KeyError:
							e.configure(state=NORMAL)

# helper functions for creating rows in the parameter table:

def psection(name):
	"""Header for ParamTable (starts new section); same as ptitle"""
	return (name, None, None, None, None)

def ptitle(name):
	"""Header for ParamTable (starts new section); same as psection"""
	return (name, None, None, None, None)

def pslot(name, default=None, val=None, info='', lockonrun=None):
	"""Generic parameter ParamTable slot"""
	return (name, default, val, info, lockonrun)

def pslot_ro(name, default=None, val=None, info=''):
	"""Generic READONLY ParamTable slot"""
	return (name, default, val, info, _KEEPLOCKED)

def pchoice(name, default=None, choices=None, info='', lockonrun=None):
	"""Dropdown list of choices"""
	return (name, default, choices, info, lockonrun)

def pbool(name, default=1, info='', lockonrun=None):
	"""Yes/No box that (generates bool 0/1 value)"""
	return (name, default, is_bool, info, lockonrun)

def pyesno(name, default=1, info='', lockonrun=None):
	"""Yes/No box that (generates bool 0/1 value); save as pbool"""
	return (name, 1-default, {'yes':1, 'no':0}, info, lockonrun)

def pparam(name, default, info='', lockonrun=None):
	"""param slot -- see pype_aux.param_expand"""
	return (name, default, is_iparam, info, lockonrun)

def piparam(name, default, info='', lockonrun=None):
	"""integer param slot -- see pype_aux.param_expand"""
	return (name, default, is_iparam, info, lockonrun)

def pcolor(name, default, info='', lockonrun=None):
	"""Color spec (R,G,B,A)"""
	return (name, default, is_color, info, lockonrun)

def pint(name, default, info='', lockonrun=None):
	"""Integer"""
	return (name, default, is_int, info, lockonrun)

def pfloat(name, default, info='', lockonrun=None):
	"""Floating point number"""
	return (name, default, is_float, info, lockonrun)

def plist(name, default, info='', lockonrun=None):
	"""List of numbers (really should be pseq, for sequence)"""
	return (name, default, is_list, info, lockonrun)

def pany(name, default, info='', lockonrun=None):
	"""Anything -- basically no validation at all"""
	return (name, default, is_any, info, lockonrun)

# validator functions

def is_dir(s, evaluate=None):
	"""Must be a directory.

	"""
	if posixpath.isdir(s):
		r = VALID
	else:
		r = INVALID
	if evaluate:
		return (r, s)
	return r

def is_file(s, evaluate=None):
	"""Must be name of an EXISTING file.

	"""
	if posixpath.exists(s):
		r = VALID
	else:
		r = INVALID
	if evaluate:
		return (r, s)
	return r

def is_newfile(s, evaluate=None):
	"""Must be name of NON-EXISTING file.

	"""
	if posixpath.exists(s):
		r = INVALID
	else:
		r = VALID
	if evaluate:
		return (r, s)
	return r

def is_any(s, evaluate=None):
	"""No type checking --> always returns true.

	"""
	r = VALID
	if evaluate:
		return (r, s)
	return r

def is_boolean(s, evaluate=None):
	"""Must be some sort of boolean flag.

	Try to do a bit of parsing:
		- 1,yes,on,true -> 1
		- 0,no,off,false -> 0

	Use pyesno() or something like that for drop down.

	"""
	try:
		x = string.lower(s)
		if (x == 'yes') or (x == 'on') or (x == 'true'):
			r = VALID
			i = 1
		elif (x == 'no') or (x == 'off') or (x == 'false'):
			r = VALID
			i = 1
		else:
			i = int(s)
			if (i == 0) or (i == 1):
				r = VALID
			else:
				i = 0
				r = INVALID
	except ValueError:
		i = 0
		r = INVALID
	if evaluate:
		return (r, i)
	return r

# alias for is_boolean:
is_bool = is_boolean

def is_int(s, evaluate=None):
	"""Must be simple integer (positive, negative or zero).

	"""

	try:
		i = int(s)
		r = VALID
	except ValueError:
		i = 0
		r = INVALID
	if evaluate:
		return (r, i)
	return r

def is_posint(s, evaluate=None):
	"""Must be positive (> 0) integer.

	"""
	try:
		i = int(s)
		if i > 0:
			r = VALID
		else:
			r = INVALID
	except ValueError:
		i = 0
		r = INVALID
	if evaluate:
		return (r, i)
	return r

def is_negint(s, evaluate=None):
	"""Must be negative (< 0) integer.

	"""
	try:
		i = int(s)
		if i > 0:
			r = VALID
		else:
			r = INVALID
	except ValueError:
		i = 0
		r = INVALID
	if evaluate:
		return (r, i)
	return r

def is_gteq_zero(s, evaluate=None):
	"""Must be greater than or equal to zero.

	"""

	try:
		i = int(s)
		if i >= 0:
			r = VALID
		else:
			r = INVALID
	except ValueError:
		i = 0
		r = INVALID
	if evaluate:
		return (r, i)
	return r

def is_lteq_zero(s, evaluate=None):
	"""Must be less than or equal to zero.

	"""

	try:
		i = int(s)
		if i <= 0:
			r = VALID
		else:
			r = INVALID
	except ValueError:
		i = 0
		r = INVALID
	if evaluate:
		return (r, i)
	return r

def is_rgb(s, evaluate=None):
	"""Must be a properly formed RGB color triple.

	Form should be (R,G,B) were R G and B are all
	in the range 0-255. Parens are required.

	Note: is_color is an alias for this fn

	"""
	l = None
	try:
		l = eval(s)
		if (len(l) == 3 and
					(l[0] >= 0 and l[0] < 256) and
					(l[1] >= 0 and l[1] < 256) and
					(l[2] >= 0 and l[2] < 256)):
			r = VALID
		elif len(l) == 1 and (l[0] >= 0 and l[0] < 256):
			r = VALID
			l = (l[0],l[0],l[0])
		else:
			r = INVALID
	except:
		r = INVALID
	if evaluate:
		return (r, l)
	return r

is_color = is_rgb

def is_rgba(s, evaluate=None):
	"""Must be proper RGBA tuple (RGB+alpha).

	Like is_color()/is_rgb(), but allows for alpha channel
	specification.
	"""
	l = None
	try:
		l = eval(s)
		if (len(l) == 3 and
			(l[0] >= 0 and l[0] < 256) and (l[1] >= 0 and l[1] < 256) and
			(l[2] >= 0 and l[2] < 256)):
			r = VALID
		elif (len(l) == 4 and
			  (l[0] >= 0 and l[0] < 256) and (l[1] >= 0 and l[1] < 256) and
			  (l[2] >= 0 and l[2] < 256) and (l[3] >= 0 and l[3] < 256)):
			r = VALID
		else:
			r = INVALID
	except:
		r = INVALID
	if evaluate:
		return (r, l)
	return r

def is_gray(s, evaluate=None):
	"""
	entry must be a valid 8-bit grayscale value (0-255)
	"""
	try:
		i = int(s)
		if (i >= 0) and (i <= 255):
			r = VALID
		else:
			i = 0
			r = INVALID
	except ValueError:
		i = 0
		r = INVALID
	if evaluate:
		return (r, i)
	return r

def is_rgba2(s, evaluate=None, meanlum=(128,128,128)):
	"""RGBA triple where values are 0-1

	"""
	l, r = None, INVALID
	try:
		l = tuple(eval(s))
		if all(map(lambda x: x>=0 and x<=1, l)):
			r = VALID
			if len(l) == 3:
				l = l + (1.0,)
	except SyntaxError:
		pass

	l = map(lambda x: int(x[0] + (255 * (x[1] - 0.5))),
			zip(meanlum, x)) + (l[3],)
	if evaluate:
		return (r, l)
	return r

def is_float(s, evaluate=None):
	"""Must be a valid floating point number

	"""
	try:
		f = float(s)
		r = VALID
	except ValueError:
		f = 0.0
		r = INVALID
	if evaluate:
		return (r, f)
	return r

def is_percent(s, evaluate=None):
	"""Must be valid percentage (ie, float in range 0-1)
	(technically this is is_fraction!)

	"""
	try:
		f = float(s)
		if (f >= 0.0) and (f <= 1.0):
			r = VALID
		else:
			f = 0.0
			r = INVALID
	except ValueError:
		f = 0.0
		r = INVALID
	if evaluate:
		return (r, f)
	return r

def is_angle_degree(s, evaluate=None):
	"""Must be valid angle in degrees (ie, float in range 0-360)

	"""
	try:
		f = float(s)
		if (f >= 0.0) and (f <= 360.0):
			r = VALID
		else:
			f = 0.0
			r = INVALID
	except ValueError:
		f = 0.0
		r = INVALID
	if evaluate:
		return (r, f)
	return r

def is_param(s, evaluate=None):
	"""Is 'special parameter' string.

	See the param_expand function (pype_aux.py) for
	full documentation on the valid forms of special
	parameter strings.

	"""
	try:
		x = pype_aux.param_expand(s)
		if x is None:
			r = INVALID
		else:
			r = VALID
	except ValueError:
		x = 0.0
		r = INVALID
	if evaluate:
		return (r, x)
	return r

def is_iparam(s, evaluate=None):
	"""Like is_param, but integer values.

	"""
	try:
		x = pype_aux.param_expand(s)
		if x is None:
			r = INVALID
		else:
			r = VALID
	except ValueError:
		x = 0
		r = INVALID
	if evaluate:
		try:
			return (r, int(round(x)))
		except TypeError:
			return (INVALID, 0)
	return r

def is_cdf(s, evaluate=None):
	"""Must describe a cummulative distribution <-- NO REALLY, PDF...

	This ensures that the specified value is an integer or a vector
	describing a valid cummulative PDF.	 If an integer, then return a
	n-length cdf of uniform prob (eg, [1/n, 1/n .. 1/n]) Otherwise,
	normalize the vector to have unity area.

	IMPROVED: 23-mar-2002 JM --> changed so you don't have
	to make stuff add to 1.0, evaluating divides by the
	sum to force it to add up to 1.0...

	"""
	try:
		i = int(s)
		if evaluate:
			val = []
			for n in range(i):
				val.append(1.0 / float(i))
		r = VALID
	except ValueError:
		try:
			i = eval(s)
			val = []
			if isinstance(i, types.ListType):
				sum = 0.0
				for f in i:
					sum = sum + float(f)
				for f in i:
					val.append(float(f) / sum)
			r = VALID
		except:
			val = 0
			r = INVALID
	if evaluate:
		return (r, val)
	return r

def _toint(s):
	try:
		return int(s)
	except ValueError:
		return None

def is_pdf(s, evaluate=None):
	"""Probability density function.

	- If a list, then the list is normalized to sum=1.0 when retrieved.

	- If an integeer, then a uniform distribution of specified length
	  is used (ie, [1/n, 1/n .. 1/n]) is generated on retrieval

	- If of the form 'hazard(N)', where N is an integer

	"""

	try:
		i = int(s)
		if evaluate:
			val = []
			for n in range(i):
				val.append(1.0 / float(i))
		r = VALID
	except ValueError:
		# this re pulls out the argument for the hazard function
		hparse = re.compile('^hazard\(([0-9]+)\)$').split(s)
		if len(hparse) == 3 and not toint(hparse[1]) is None:
			val = np.exp(-np.arange(toint(hparse[1])))
			r = VALID
		else:
			try:
				i = eval(s)
				val = []
				if isinstance(i, types.ListType):
					sum = 0.0
					for f in i:
						sum = sum + float(f)
					for f in i:
						val.append(float(f) / sum)
				r = VALID
			except:
				val = 0
				r = INVALID
	if evaluate:
		return (r, val)
	return r

def is_list(s, evaluate=None):
	"""Must be a list/vector or range.

	Lists are specified in []'s. Ranges can be either:

		=start:stop:step (inclusive: both start and stop in list)

		start:stop:step	 (stop is not included in the list)

	"""

	try:
		v = s.split(':')
		if len(v) > 1:
			if s[0] == '=':
				inc = 1
				v = map(int, s[1:].split(':'))
			else:
				v = map(int, s.split(':'))
				inc = 0
			if len(v) < 3:
				stride = 1
			else:
				stride = v[2]
			r = VALID
			if inc:
				val = range(v[0], v[1]+1, stride);
			else:
				val = range(v[0], v[1], stride);
			if evaluate:
				return (r, val)
			return r
	except:
		pass

	try:
		val = eval(s)
		if isinstance(val, types.ListType):
			r = VALID
		else:
			r = INVALID
			val = []
	except:
		r = INVALID
		val = []

	if evaluate:
		return (r, val)

	return r

if __name__ == '__main__':
	import sys

	root = Tk()
	Pmw.initialise(root)
	exitButton = Button(root, text = 'Exit', command = root.destroy)
	exitButton.pack(side = 'bottom')
	p = ParamTable(root,
				   (ptitle('test'),
					pslot('a', default='500+-10%', val=is_param),
					pslot('l', default='', val=is_list),
					pslot('b', default='3', val=None),
					pslot('choice', default=1, val=('true', 'false')),
					pslot('yn', default=1, val={'no':0, 'yes':1}),
					pslot('c', default='4', val=None)),
				   file='foobar', allowalt=False)

	Button(root, text = 'info',
		   command = lambda p=p:
				   sys.stdout.write('%s\n'%p.query('yn'))).pack(side='bottom')

	p.load('foobar')

	root.mainloop()

