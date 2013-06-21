# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""Parameter tables with type validation

PMW (Python MegaWidgets) based parameter tables (aka worksheets)
for use by the pype GUI. Most of these functions are **INTERNAL**
only and should never be called directly, except by "power users"!

The exceptions are the *is_????* functions to be used as validators
for task worksheets.

Author -- James A. Mazer (james.mazer@yale.edu)

"""

"""Revision History

Mon Aug 14 13:46:27 2006 mazer

- Added field locking buttons ('X' to left of entry fields) to let
  user lock individual entries to avoid accidental changes.. For
  Jon Touryan... should work ok with runlock'ing, but I haven't
  tested it. Is anybody using runlock??

Fri Feb 13 11:15:35 2009 mazer

- changed load/save format to a human-readable (non-pickled) version
  change should be transparent - old pickle versions will get read
  and new text versions written from now on..

Wed Mar 11 11:08:19 2009 mazer

- when parameter tables are evaluated, added storage of the raw
  unevaluated string version of the var for future reference..

Sun May 31 15:13:23 2009 mazer

- changed load/save of param tables to use standard pythong ConfigParser
  object -- this makes it easier to have external programs generate
  params files..

Tue Dec 14 16:54:50 2010 mazer

- purged old pickle-based config file code

Fri Apr 29 11:41:42 2011 mazer

- added dictionary type (like tuple) to allow {'yes':1, 'no':0} type stuff..

"""

from Tkinter import *
import Pmw
import string
import types
import os, posixpath
import cPickle
import ConfigParser


import pype
import pype_aux
from guitools import *
from filebox import Open, SaveAs
from guitools import Logger

from pvalidators import *

from pypedebug import keyboard

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
				 decorate=1, locks=1, allowalt=True):
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
			elif type(validate) is types.TupleType:
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
			elif type(validate) is types.DictType:
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
				if not (type(validate) is types.TupleType or
						type(validate) is types.DictType) and validate:
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

		if self._entries.has_key((qname,'dict')):
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
				if not (type(validate) is types.TupleType or
						type(validate) is types.DictType) and validate:
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
			if self._locks.has_key(k):
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

			if type(validate) is types.TupleType:
				try: self._entries[name].invoke(val)
				except ValueError: pass
			elif type(validate) is types.DictType:
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
				if (type(validate) is types.TupleType or
						   type(validate) is types.DictType):
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
				source, key, lockstate, value = string.split(line, '!!')
				# value has trailing \n
				x[key] = value[:-1]
				locks[key] = lockstate
			f.close()

			for slot in self._table:
				(name, default, validate, descr, runlock) = _unpack_slot(slot)
				if default is None:
					continue
				if (type(validate) is types.TupleType or
						   type(validate) is types.DictType):
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
    return (name, None, None)

def pslot(name, default=None, val=None, info='', lockonrun=None):
	"""Starting parameter table entry.

	"""
	return (name, default, val, info, lockonrun)

def pslot_ro(name, default=None, val=None, info=''):
	"""Readonly parameter table entry.

	"""
	return (name, default, val, info, _KEEPLOCKED)


def pchoice(name, default=None, choices=None, info='', lockonrun=None):
	"""Dropdown list.

	"""
	return (name, default, choices, info, lockonrun)

def pbool(name, default=1, info='', lockonrun=None):
	"""Yes/No box that generated 0/1.

	"""
	return (name, default, is_bool, info, lockonrun)

def pyesno(name, default=1, info='', lockonrun=None):
	"""Yes/No box that generated 0/1.

	"""
	return (name, 1-default, {'yes':1, 'no':0}, info, lockonrun)

def piparam(name, default, info='', lockonrun=None):
	return (name, default, is_iparam, info, lockonrun)

def pcolor(name, default, info='', lockonrun=None):
	return (name, default, is_color, info, lockonrun)

def pint(name, default, info='', lockonrun=None):
	return (name, default, is_int, info, lockonrun)

def pfloat(name, default, info='', lockonrun=None):
	return (name, default, is_float, info, lockonrun)

def pfloat(name, default, info='', lockonrun=None):
	return (name, default, is_float, info, lockonrun)

def plist(name, default, info='', lockonrun=None):
	return (name, default, is_list, info, lockonrun)


def ptitle(name):
	"""Title row.

	"""
	return (name, None, None, None, None)


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

