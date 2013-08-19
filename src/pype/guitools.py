# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""Various useful GUI functions.

Useful Tkinter and Pmw utility functions for GUI building
nd running. Things that get repeated over and over again
in the main pype code eventually end up here for
onsolidation.

Author -- James A. Mazer (james.mazer@yale.edu)

"""

"""Revision History

Wed Apr	 8 21:42:18 1998 mazer

- created

Thu Jan 27 15:27:15 2000 mazer

- added DockWindow class

Mon Jun 25 12:21:40 2007 mazer

- Container() class is obsolete... deleted it..

- Added SimpleDialog() class to replace use of the Tk builtin Dialog
  class (which is opaque and unchangable). This is much simpler..

Thu Jun 28 10:41:43 2007 mazer

- Switched use of ScrolledText to Pmw.ScrolledText - didn't realize
  there was a Tkinter version (that doesn't properly resize!). Hmmm,
  actually this is a problem - doesn't work for Tally window, so I
  reverted back to Tkinter's version..

Thu Mar 26 15:55:05 2009 mazer

- Merged in pbar.py (progress bar) stuff - should have been here
  all along.

Fri Mar 27 13:39:49 2009 mazer

- moved DancingBear and dance() (console versions) from pype.py to here

Fri Jun	 3 12:41:07 2011 mazer

- got rid of Simple in SimpleDialog etc.. replaced with trailing underscores

"""

import time
import string
from Tkinter import *
import Pmw

_viewed_warnings = {}

class DockWindow(Toplevel):
	"""Docking window class.

	This is a toplevel window class that's customized with
	hide/show functions so you can bind it's appearance to
	a button..

	"""
	def __init__(self, checkbutton=None, title=None, iconname=None, **kw):
		import pype

		apply(Toplevel.__init__, (self,), kw)

		if title:
			self.title(title)

		if iconname:
			self.iconname(iconname)
		elif title:
			self.iconname(title)

		if checkbutton:
			self._checkbutton = checkbutton
			self._v = IntVar()
			self._checkbutton.configure(command=self.toggle, variable=self._v)
		else:
			self._checkbutton = None

		mx, my = self.winfo_rootx()+20, self.winfo_rooty()+20
		pype.PypeApp().setgeo(self, default='+%d+%d' % (mx, my))

		# make close button really hide..
		self.protocol("WM_DELETE_WINDOW", self._hide)

		self.withdraw()
		self._visible = 0

	def _hide(self):
		self.withdraw()
		self._visible = 0
		if self._checkbutton:
			self._v.set(self._visible)

	def _show(self):
		self.deiconify()
		self._visible = 1
		if self._checkbutton:
			self._v.set(self._visible)

	def toggle(self):
		if self._visible:
			self._hide()
		else:
			self._show()

class TaskNotebook(DockWindow):
	def __init__(self, **options):
		apply(DockWindow.__init__, (self,), options)

		notebook = Pmw.NoteBook(self)
		notebook.pack(expand=1, fill=BOTH)
		self.notebook = notebook
		notebook.setnaturalsize(pageNames=None)

	def add(self, name, label):
		return self.notebook.add(label)

	def lift(self, name):
		self.notebook.lift(name)

class Logger(object):					# !SINGLETON CLASS!
	logwindow = None
	buffered = []
	msgs = {}
	_instance = None

	def __new__(cls, *args, **kwargs):
		"""This ensure a single instantation.
		"""
		if cls._instance is None:
			cls._instance = super(Logger, cls).__new__(cls)
			cls._init = 1
		else:
			cls._init = 0
		return cls._instance

	def __init__(self, text=None, window=None, popup=None, once=None):
		# handle multi-line message recursively..
		if text:
			if not text[-1] == '\n':
				text = text + '\n'
			s = text.split('\n')
			if len(s) > 2:
				for n in range(len(s)-1):
					Logger(text=s[n], window=window, popup=popup, once=once)
				return

		# otherwise, this is single-line message, just log it..
		if once:
			if text in Logger.msgs:
				return
			else:
				Logger.msgs[text] = 1

		if not text is None:
			(year, month, day,
			 hour, min, sec, x1, x2, x3) = time.localtime(time.time())
			text = '%02d:%02d:%02d %s' % (hour, min, sec, text)

		if window:
			Logger.logwindow = window
			# push buffered output into log window
			for s in Logger.buffered:
				Logger.logwindow.write(s)
			Logger.buffered = []
		else:
			if Logger.logwindow:
				Logger.logwindow.write(text)
			else:
				Logger.buffered.append(text)
			sys.stderr.write(text)
			sys.stderr.flush()

		if popup:
			warn('guitools:Logger', text)

class ConsoleWindow(Toplevel):
	def __init__(self, title='ConsoleWindow', iconname='Console',
				 font='courier 10', bg='gray75', **kw):

		apply(Toplevel.__init__, (self,), kw)
		if title:
			self.title(title)
		if iconname:
			self.iconname(iconname)

		f = Frame(self)
		f.pack(expand=1, fill=BOTH)

		self.ptext = Pmw.ScrolledText(f)
		self.ptext.pack(expand=1, side=TOP, fill=BOTH)
		self.text = self.ptext.component('text')
		self.text.config(state=DISABLED, font=font, bg=bg, height=10)

		clear = Button(f, text='clear', command=self.clear)
		clear.pack(expand=0, side=TOP, anchor=W)

		self.visible = 1
		self.protocol("WM_DELETE_WINDOW", self.showhide)

	def write(self, str):
		self.text.config(state=NORMAL)
		self.text.insert(END, str)
		self.text.config(state=DISABLED)
		self.text.update()
		self.text.see(END)

	def clear(self):
		self.text.config(state=NORMAL)
		self.text.delete(0.0, END)
		self.text.config(state=DISABLED)

	def showhide(self):
		if self.visible:
			self.withdraw()
			self.visible = 0
		else:
			self.deiconify()
			self.visible = 1

class Entry_(object):
	def __init__(self, parent, prompt=None, default=''):
		self.top = Toplevel(parent)
		if prompt:
			Label(self.top, text=prompt).pack()
		self.e = Entry(self.top)
		self.e.insert(0, default)
		self.e.pack(padx=5)

		Button(self.top, text="OK",
			   command=self.ok).pack(side=LEFT, padx=5)
		Button(self.top, text="Cancel",
			   command=self.cancel).pack(side=RIGHT, padx=5)
		self.top.protocol("WM_DELETE_WINDOW", self.cancel)
		self.top.bind('<Return>', self.ret)
		undermouse(self.top)

		self.e.focus_set()
		self.value = None
		return

	def ok(self):
		self.value = self.e.get()
		self.top.destroy()

	def cancel(self):
		self.value = None
		self.top.destroy()

	def ret(self, dummy):
		self.ok()

	def go(self):
		self.top.grab_set()
		self.top.wait_window(self.top)
		return self.value

class Dialog_(Toplevel):
	def __init__(self, msg, responses=('Ok',), default=None,
				 astext=None, title=None, iconname=None, grab=1,
				 **kw):

		apply(Toplevel.__init__, (self,), kw)

		if title:
			self.title(title)
		if iconname:
			self.iconname(iconname)

		self.parent = self._nametowidget(self.winfo_parent())

		self.transient(self.parent)

		f = Frame(self, relief=GROOVE, borderwidth=3)
		f.pack(side=TOP, expand=1, fill=BOTH)

		if astext:
			# use text box so message is copyable with mouse...
			m = Text(f, relief=RIDGE, borderwidth=3)
			m.insert(END, msg)
		else:
			m = Label(f, text=msg, justify=LEFT)

		m.pack(padx=25, pady=25)

		f = Frame(self)
		f.pack(side=TOP, expand=1, fill=X)
		n = 0
		for r in responses:
			b = Button(f, text=r, command=lambda n=n: self._respond(n))
			if n == default:
				b.configure(fg='blue')
			b.pack(side=LEFT, padx=10, pady=5)
			n = n + 1

		self.protocol("WM_DELETE_WINDOW", lambda n=None: self._respond(n))

		self.grab = grab

		if default:
			self.default = default
			self.bind('<Return>', self._return_event)

	def go(self, wait=1):
		screencenter(self)
		self.parent.bell()

		if wait:
			# don't grab, if we're not waiting!
			if self.grab:
				self.grab_set()
			self.wait_window(self)
			return self._choice

	def _respond(self, n):
		self._choice = n
		self.destroy()

	def _return_event(self, event):
		if self.default:
			self._choice = self.default
			self.destroy()

class LogWindow(object):
	def __init__(self, parent, height=20, width=70, bg='white',
				 font='Courier 8'):

		t = Pmw.ScrolledText(parent)
		t.pack(expand=1, side=TOP, fill=BOTH)
		self.text = t.component('text')
		self.text.config(bg=bg, font=font,
						 height=height,
						 width=width)
		self.text.config(state=DISABLED)
		self.next_tag = 0

	def write(self, line, color=None, update=1):
		self.text.config(state=NORMAL)
		if color:
			tag = "tag%d" % self.next_tag
			self.next_tag = self.next_tag + 1
			self.text.tag_config(tag, foreground=color)
			self.text.insert(END, line, tag)
		else:
			self.text.insert(END, line)
		self.text.config(state=DISABLED)
		if update:
			self.text.update()
		self.text.see(END)

	def writenl(self, line, color=None, update=1):
		self.write("%s\n" % line, color)

	def clear(self):
		self.text.config(state=NORMAL)
		self.text.delete(0.0, END)
		self.text.config(state=DISABLED)

	def update(self):
		self.text.update()

class EventQueue(object):
	"""TkInter event queue.

	Useful ev.state flags:
		- SHIFT = 1
		- CTRL = 4
	"""

	def __init__(self, parent, ev='<Key>'):
		self.buffer = []
		parent.bind_all(ev, self._push)

	def _push(self, ev):
		self.buffer.append((ev.keysym, ev))

	def pop(self):
		if len(self.buffer) > 0:
			r = self.buffer[0]
			self.buffer = self.buffer[1:]
			return r
		else:
			return (None, None)

	def flush(self):
		self.buffer = []

def warn(title, message, wait=None, action=None,
		 astext=0, grab=1, once=None):
	"""Popup a dialog box and warn the user about something. Lots of
	options, but only one possible response: "Continue" or "Close"

	:param title: (string) popup box title

	:param message: (string) message to display

	:param wait: (bool) wait for user response or return immediately?

	:param action: (string) name of action (goes in button)

	:param astext: (bool) use textbox to display (copy-able)

	:param grab: (bool) grab mouse/keyboard?

	:param once: (bool) only show this message once? (internal list kept)

	:return: (bool) 1 if displayed, 0 if not displayed (ie, once=True)

	"""

	if once:
		if message in _viewed_warnings:
			return 0
		else:
			_viewed_warnings[message] = 1

	if action is None:
		if wait:
			action = 'Continue'
		else:
			action = 'Close'
	dialog = Dialog_(message,
					 title=title, iconname='warning', astext=astext,
					 default=0, responses=(action,), grab=grab)
	undermouse(dialog)
	dialog.go(wait=wait)
	return 1

def ask(title, message, strings):
	"""Popup a dialog box and ask the user to choose one of several
	possible responses (strings is list of possible responses).

	:param title: (string) popup box title

	:param message: (string) message to display

	:param strings: (list of string) list of options

	:return: NUMBER of the selected response (starting with 0)
		or None if you close the box w/o selecting anything

	"""

	i = Dialog_(message, title=title,
				default=0, responses=strings).go()
	return i

def undermouse(w, query=None):
	"""Position a window 'w' directly underneath the mouse.

	"""
	rw, rh = w.winfo_reqwidth(), w.winfo_reqheight()
	x, y = w.winfo_pointerx()-(rw/2), w.winfo_pointery()-(rh/2)
	if x < 0:
		x = 0
	elif (x+rw) >= w.winfo_screenwidth():
		x = w.winfo_screenwidth() - rw
	if y < 0:
		y = 0
	elif (y+rh) >= w.winfo_screenheight():
		y = w.winfo_screenheight() - rh
	if query:
		return "+%d+%d" % (x, y)
	w.geometry("+%d+%d" % (x, y))

def screencenter(w):
	"""Position a window 'w' at the center of the screen.

	"""
	sw = w.winfo_screenwidth()
	sh = w.winfo_screenheight()
	if sw > 1280:
		# this is to keep dialog boxes from getting
		# split across a dual screen layout..
		sw = 1280

	x, y = (sw/2) - (w.winfo_reqwidth()/2), (sh/2) - (w.winfo_reqheight() / 2)
	w.geometry("+%d+%d" % (x, y))

class ProgressBar(object):
	"""Indicate progress for a long running task.

	"""

	def __init__(self, width=200, height=22, doLabel=None, labelText="",
				 value=0, title='Working', min=0, max=100):
		from Tkinter import _default_root

		if _default_root is None:
			root = Tk()
			root.withdraw()

		self.master = Toplevel()
		self.master.title('Working')
		self.master.iconname('Working')
		self.master.lift()
		self.min=min
		self.max=max
		self.width=width
		self.height=height
		self.doLabel=doLabel

		self.labelFormat="%d%%"
		self.value=value
		f = Frame(self.master, bd=3, relief=SUNKEN)
		f.pack(expand=1, fill=BOTH)
		Label(f, text=title).pack(expand=1, fill=Y, side=TOP)
		self.frame=Frame(f, relief=SUNKEN, bd=4, background='black')
		self.frame.pack(fill=BOTH)
		self.canvas=Canvas(self.frame, height=height, width=width, bd=0,
						   highlightthickness=0, background='green')
		self.scale=self.canvas.create_polygon(0, 0, width, 0,
											  width, height, 0, height,
											  fill='red')
		self.label=self.canvas.create_text(self.canvas.winfo_reqwidth() / 2,
										   height / 2, text=labelText,
										   anchor="c", fill='black')
		self.update()
		self.canvas.pack(side=TOP, fill=X, expand=NO)

		self.master.update_idletasks()
		sw = self.master.winfo_screenwidth()
		sh = self.master.winfo_screenheight()
		self.master.geometry("+%d+%d" %
							 (sw/2 - (self.master.winfo_reqwidth()/2),
							  sh/2 - (self.master.winfo_reqheight() / 2)))
		self.master.update_idletasks()

	def __del__(self):
		self.master.withdraw()
		self.update()
		self.master.destroy()

	def set(self, newValue, newMax=None):
		if newMax:
			self.max = newMax
		self.value = newValue
		self.update()

	def update(self):
		# Trim the values to be between min and max
		value=self.value
		if value > self.max:
			value = self.max
		if value < self.min:
			value = self.min

		# Adjust the rectangle
		self.canvas.coords(self.scale, 0, 0, 0, self.height,
						   float(value) / self.max * self.width, self.height,
						   float(value) / self.max * self.width, 0)

		# And update the label
		if self.doLabel:
			self.canvas.itemconfig(self.label)
			if value:
				if value >= 0:
					pvalue = int((float(value) / float(self.max)) * 100.0)
				else:
					pvalue = 0
				self.canvas.itemconfig(self.label, text=self.labelFormat
									   % pvalue)
			else:
				self.canvas.itemconfig(self.label, text='')
		self.canvas.update_idletasks()

class _DancingBear(object):
	_cursorPos = 0
	def __init__(self, ticker='.'):
		if ticker is None:
			sys.stderr.write('\n')
			DancingBear._cursorPos = 0
		else:
			ticker = "%s" % ticker
			DancingBear._cursorPos = DancingBear._cursorPos + len(ticker)
			if DancingBear._cursorPos > 50:
				ticker = ticker + '\n'
				DancingBear._cursorPos = 0
			sys.stderr.write(ticker)
			sys.stderr.flush()

def dance(ticker='.'):
	"""Indicate longer-term progress by calling this periodically.

	"""
	DancingBear(ticker)

class tkSelector:
	def __init__(self, items, title=None):
		self.dialog = Pmw.SelectionDialog(master = None,
										  title = 'Select one...',
										  label_text = title,
										  buttons=('OK', 'Cancel'),
										  defaultbutton='OK',
										  scrolledlist_labelpos='n',
										  scrolledlist_items=items,
										  command=self.execute)
		self.dialog.pack(fill='both', expand=1, padx=5, pady=5)

	def go(self):
		self.dialog.activate()
		self.dialog.destroy()
		return self.result

	def execute(self, buttonname):
		sels = self.dialog.getcurselection()
		if buttonname is None or buttonname is 'Cancel' or len(sels) == 0:
			self.result = None
		else:
			self.result = sels[0]
		self.dialog.deactivate()

def popselect(items):
	return tkSelector(items).go()

class ToolTip(object):
	def __init__(self, widget):
		self.widget = widget
		self.tipwindow = None
		self.id = None
		self.x = self.y = 0

	def showtip(self, text):
		"Display text in tooltip window"
		self.text = text
		if self.tipwindow or not self.text:
			return
		x, y, cx, cy = self.widget.bbox("insert")
		x = x + self.widget.winfo_rootx() + 27
		y = y + cy + self.widget.winfo_rooty() +27
		self.tipwindow = tw = Toplevel(self.widget)
		tw.wm_overrideredirect(1)
		tw.wm_geometry("+%d+%d" % (x, y))
		label = Label(tw, text=self.text, justify=LEFT,
					  background="#ffffe0", relief=SOLID, borderwidth=1,
					  font=("tahoma", "8", "normal"))
		label.pack(ipadx=1)

	def hidetip(self):
		tw = self.tipwindow
		self.tipwindow = None
		if tw:
			tw.destroy()

def createToolTip(widget, text):
	toolTip = ToolTip(widget)
	def enter(event):
		toolTip.showtip(text)
	def leave(event):
		toolTip.hidetip()
	widget.bind('<Enter>', enter)
	widget.bind('<Leave>', leave)

if __name__ == '__main__':
	sys.stderr.write('%s should never be loaded as main.\n' % __file__)
	sys.exit(1)
