# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""User display window

Functions and classes in this module implement the user display
window. This includes all mouse & key inputs, display of shadow
stimuli on the user display (to mirror what the subject sees), etc.

Author -- James A. Mazer (james.mazer@yale.edu)

"""

"""Revision History

Wed Aug 14 13:09:50 2002 mazer

- removed scrollbar junk: no need, never used it.

Wed Mar	 5 19:26:47 2003 mazer

- added import points (from ascii file)

Thu Jun 16 15:20:45 2005 mazer

- added ben willmore's changes for mac-support

Sun Jul 24 21:47:12 2005 mazer

- made fx,fy automatically propagate back to pype.py via self.app.set_fxfy()

Mon Jan 16 11:18:57 2006 mazer

- added callback option to the UserDisplay class to support time
  marking from pype.py (see notes in pype.py)

Fri May 22 15:58:59 2009 mazer

- changed button-1 function to button-3 to avoid problems with WM..

Tue Jul	 7 10:25:19 2009 mazer

- BLOCKED is gone -- computed automatically from syncinfo..

Mon Jun 28 13:35:12 2010 mazer

- Removed menubar at top in favor of dropdown menus (saves screen
	space).	 One single dropdown menu off Button-1 now (Button-2 for
	task-specific menu, if needed).

- This means Pmw is no longer required here.. everything's simplified

Fri Jul 16 10:58:31 2010 mazer

- changed menu button to button-3 instead of button-1 to allow
	clicking button-1 to raise the interface window!

Tue Feb	 1 12:46:07 2011 mazer

- got rid of the callback/MARK function (bound to = key)

"""

import os
import sys
import time
import string
import cPickle
import math
from Tkinter import *
from tkSimpleDialog import askstring

import Pmw

from pype import *
from guitools import *
import pype_aux
import filebox

from pypedebug import keyboard

class ScaledCanvas(Canvas):
	def __init__(self, *args, **kwargs):
		if 'xscale' in kwargs:
			self.xscale = kwargs['xscale']
			del(kwargs['xscale'])
		else:
			self.xscale = 1.0
		if 'yscale' in kwargs:
			self.yscale = kwargs['yscale']
			del(kwargs['yscale'])
		else:
			self.yscale = 1.0

		Canvas.__init__(self, *args, **kwargs)

	def create_line(self, x1, y1, x2, y2, **kwargs):
		x1 *= self.xscale
		x2 *= self.xscale
		y1 *= self.yscale
		y2 *= self.yscale
		return Canvas.create_line(self, x1, y1, x2, y2, **kwargs)

	def window2scaled(self, x, y):
		"""convert from window to scaled coords"""
		return (x / self.xscale), (y / self.yscale)

	def coords(self, item, *args, **kwargs):
		if len(args) == 2:
			x1, y1 = args
			x1 *= self.xscale
			y1 *= self.yscale
			return Canvas.coords(self, item, x1, y1)
		else:
			x1, y1, x2, y2 = args
			x1 *= self.xscale
			x2 *= self.xscale
			y1 *= self.yscale
			y2 *= self.yscale
			return Canvas.coords(self, item, x1, y1, x2, y2)

	def create_rectangle(self, x, y, w, h, **kwargs):
		x *= self.xscale
		w *= self.xscale
		y *= self.yscale
		h *= self.yscale
		return Canvas.create_rectangle(self, x, y, w, h, **kwargs)

	def create_oval(self, x, y, w, h, **kwargs):
		x *= self.xscale
		w *= self.xscale
		y *= self.yscale
		h *= self.yscale
		return Canvas.create_oval(self, x, y, w, h, **kwargs)

	def create_text(self, x, y, **kwargs):
		x *= self.xscale
		y *= self.yscale
		return Canvas.create_text(self, x, y, **kwargs)

	def create_image(self, x, y, **kwargs):
		# note: this doesn't resize the image!!!
		x *= self.xscale
		y *= self.yscale
		return Canvas.create_image(self, x, y, **kwargs)

	def create_window(self, x, y, **kwargs):
		x *= self.xscale
		y *= self.yscale
		return Canvas.create_window(self, x, y, **kwargs)


class UserDisplay(object):
	def __init__(self, master, fbsize, scale=1.0, pix_per_dva=1.0,
                 xscale=1.0, yscale=1.0, app=None, eyemouse=False):
		"""UserDisplay Class.

		The UserDisplay is a pype local window on the user's computer
		screen that shows a shadow/copy of what the subject is viewing
		plus other useful information and fiduciary marks.

		**master** - parent window (None for make new toplevel window)

		**fbsize** - size of framebuffer (width, height) pair.

		**pix_per_dva** - pixels per degree visual angle

		**app** - PypeApp handle

		**eyemouse** - Use Button-1 as pseudo eye position signal..

		**NOTE:** Just because most of these arguments are keywords
		(and therefore optional), doesn't mean they're not
		required. You should really supply all the parameters to this
		function each time it's called.

		"""

		self.app = app

		if master:
			self.master = master
		else:
			self.master = Toplevel()
			self.master.title('userdpy')
			self.master.iconname('userdpy')
			if self.app:
				self.app.setgeo(self.master, default='-0-0', posonly=1)
			else:
				self.master.geometry('-0+20')
			self.visible = 1

		(cwidth, cheight) = fbsize

		self.background_nofocus = 'red'
		self.background_focus = 'green'

		self.frame = Frame(self.master, relief=FLAT,
						   bd=2, bg=self.background_nofocus)

		f = Frame(self.frame)
		f.pack(expand=1, fill=X)
		self._info = Label(f, font="Courier 10", relief=SUNKEN)
		self._info.pack(expand=1, fill=X, side=LEFT)

		self.barstate = Label(f, relief=RAISED)
		self.barstate.pack(expand=0, side=RIGHT)
        Label(f, font="Courier 10", \
              text='%dppd' % (pix_per_dva,), \
              relief=SUNKEN).pack(expand=0, side=RIGHT)
		if xscale != 1.0 or yscale != 1.0:
            Label(f, font="Courier 10", \
                  text='%.1fx%.1f' % (xscale, yscale), \
                  relief=SUNKEN).pack(expand=0, side=RIGHT)

        self._mouseinfo_x = Label(f, font="Courier 10",
                                  fg='red', bg='white', relief=SUNKEN)
        self._mouseinfo_y = Label(f, font="Courier 10",
                                  fg='red', bg='white', relief=SUNKEN)
        self._mouseinfo_x.pack(expand=0, side=RIGHT)
		self._mouseinfo_y.pack(expand=0, side=RIGHT)

		# tkinter vars for linking GUI to python vars:
		self._photomode_tvar = IntVar()
		self._photomode_tvar.set(0)		# photo mode starts up OFF!!
		self._photomode = self._photomode_tvar.get()
		self.gridinterval = pix_per_dva

		# don't use this yet -- not quite working properly with handmap2
		# except when scale=1.0..
		self.canvas = ScaledCanvas(self.frame,
								   xscale=xscale,
								   yscale=xscale,
								   width=round(xscale*cwidth),
								   height=round(yscale*cheight))
		self.canvas.pack()
		self.canvas.configure(cursor='tcross', bg='grey80')

		self.canvas.bind("<FocusIn>",
						 lambda ev,s=self:
								 s.frame.configure(bg=s.background_focus))
		self.canvas.bind("<FocusOut>",
						 lambda ev,s=self:
								s.frame.configure(bg=s.background_nofocus))

		self.frame.pack(expand=1, fill=BOTH)

		self._htrace = []
		self._vtrace = []
		self._tracecursor = self.canvas.create_line(1, 50-20, 1, 50+20,
													 fill='black')
		for x in range(1,cwidth):
			self._htrace.append(self.canvas.create_line(x-1, 50, x, 50,
														 fill='red', width=3))
			self._vtrace.append(self.canvas.create_line(x-1, 50, x, 50,
														 fill='violet', width=3))
		self._traceptr = 0


		self.mousex = 0
		self.mousey = 0
		self.xoffset = 0
		self.yoffset = 0

		self._mouse_motion(ev=None)

		p = Menu(self.canvas, tearoff=0)

		m = Menu(p, tearoff=0)
		m.add_command(label="Set fixspot here",
					  command=self._fixset)
		m.add_command(label="Set fixspot to (0,0)",
					  command=self._fixzero)
		m.add_command(label="Project fixspot up/down to X-AXIS",
					  command=lambda:self._fixset(y=0))
		m.add_command(label="Project fixspot left/right to Y-AXIS",
					  command=lambda:self._fixset(x=0))
		m.add_command(label="Enter fixspot coords", command=self._fixxy)
		p.add_cascade(label='Fixspot', menu=m)

		m = Menu(p, tearoff=0)
		m.add_command(label='Clear all marks (C)', command=self._clearfidmarks)
		m.add_command(label='Save (s)', command=self.savefidmarks)
		m.add_command(label='Load (l)', command=self.loadfidmarks)
		m.add_command(label='View (v)', command=self._showfidmarks)
		m.add_command(label='clear closest (c)')
		p.add_cascade(label='Fiduciary Marks', menu=m)

		m = Menu(p, tearoff=0)
		m.add_command(label="Set a box corner (/)", command=self.setbox)
		m.add_command(label="Clear box", command=self.clearbox)
		m.add_command(label='Enter box position', command=self.manualbox)
		p.add_cascade(label='Box', menu=m)

		m = Menu(p, tearoff=0)
		m.add_command(label='Clear all points', command=self.clearpoints)
		m.add_command(label='Load .pts file',
					   command=lambda s=self: s.loadpoints(merge=None))
		m.add_command(label='Merge .pts file',
					   command=lambda s=self: s.loadpoints(merge=1))
		m.add_command(label='Save .pts file', command=self.savepoints)
		m.add_command(label='Load ascii file',
					  command=lambda s=self: s.loadpoints_ascii(merge=None))
		m.add_command(label='Merge ascii file',
					  command=lambda s=self: s.loadpoints_ascii(merge=1))
		m.add_command(label='set (.)', state=DISABLED)
		m.add_command(label='clear closest (,)', state=DISABLED)
		p.add_cascade(label='Tracker calibration', menu=m)

		m = Menu(p, tearoff=0)
		m.add_checkbutton(label='Photo mode', command=self._phototoggle,
						  variable=self._photomode_tvar)
		p.add_cascade(label='Display Options', menu=m)

		m = Menu(p, tearoff=0)
		m.add_command(label='show shortcuts', command=self.help)
		p.add_cascade(label='Help', menu=m)

		if eyemouse:
			self.canvas.bind("<Button-1>", self._mouse1)
			self.canvas.bind("<Key-space>", self._space)
			self.canvas.bind("<KeyRelease-space>", self._space)
		self.canvas.bind("<Button-3>", lambda ev,p=p,s=self: s._dopopup(ev,p))
		self.canvas.bind("<Motion>", self._mouse_motion)
		self.canvas.bind("<Enter>", self._mouse_enter)
		self.canvas.bind("<Leave>", self._mouse_leave)
		self.canvas.bind("<KeyPress>", self._key)

		self.canvas.pack(expand=0)

		self._iconlist = []
		self._displaylist_icons = []
		self._fid_list = []
		self._fidstuff = []
		self._axis = []
		self.markstack = []
		self.markbox = None

		self.w = cwidth                      # full width
		self.h = cheight                     # full height
		self.hw = int(round(self.w / 2.0))   # half width
		self.hh = int(round(self.h / 2.0))   # half height

		self._axis = []

        # Wed Oct 16 17:01:56 2013 mazer
        # big mystery: if you do this coords are correct, otherwise,
        # the y values are off. I think it has something to do with
        # forcing the canvas widget to update its width and height
        # parameters in a funny, buggy way.. just leave it for now.
        bug = self.canvas.create_rectangle(0, 0, 0, 0,
                                           fill="black", outline="")
        del bug

		self._eye_at = None            # current eye position marker
		self._eye_trace = []           # trace history sample markers
		self._eye_trace_lines = []     # trace history lines
		self._eye_trace_maxlen = 20    # length of history buffer
		self._eye_lxy = None           # last x,y eye position

		self.fix_x = 0
		self.fix_y = 0

		self.userhook = None
		self.userhook_data = None

		self._lastEyeUpdate = time.time()
		self.eye_at(0,0)

		self.points = []

		self.msg_label = None
		self.msg_win = None

        if 0:
            self.set_taskpopup()
        else:
            self.canvas.bind("<Button-2>",
                             lambda ev,s=self: s._taskcallbackfn(ev))

		self.visible = 1

		self.canvas.config(scrollregion=self.canvas.bbox(ALL))

    def set_taskcallback(self, callbackfn=None):
        if callbackfn:
            self._taskcallbackfn = callbackfn
        else:
            self._taskcallbackfn = lambda ev: None


	def showhide(self):
		if self.visible:
			try:
				self.master.withdraw()
			except:
				self._forgot = self.master.pack_info()
				self.master.forget()
		else:
			try:
				self.master.deiconify()
			except:
				self.master.pack(**self._forgot)
		self.visible = not self.visible

	def info(self, msg=''):
		self._info.configure(text=msg)

	def note(self, msg):
		if msg is None or len(msg) == 0:
			if self.msg_win:
				self.canvas.delete(self.msg_win)
				self.msg_win = None
			if self.msg_label:
				self.msg_label.destroy()
				self.msg_label = None
		else:
			if self.msg_win is None:
				f = Frame(self.canvas)
				self.msg_win = self.canvas.create_window(5, 25, window=f,
														  anchor=NW)
				self.msg_label = Label(f, text=msg, justify=LEFT,
									   font="Courier 10",
									   borderwidth=3, relief=RIDGE,
									   bg='white', fg='black')
				self.msg_label.pack(ipadx=3, ipady=3)
				self._placenote()
			else:
				self.msg_label.configure(text=msg)

	def _placenote(self, x=None, y=None):
		if self.msg_win is None:
			return
		if x is None:
			x = int(self.app.rig_common.queryv('note_x'))
		if y is None:
			y = int(self.app.rig_common.queryv('note_y'))
		self.canvas.coords(self.msg_win, x, y)
		self.app.rig_common.set('note_x', x)
		self.app.rig_common.set('note_y', y)

	def help(self):
		warn('userdpy:help',
			 "Fiduciary marks (aka fidmarks)\n"+
			 "-----------------------------------------\n"+
			 "Arrows  Move all fidmarks left, right etc\n"+
			 "f	 Set fidmark at cursor\n"+
			 "<	 Shrink fidmarks in\n"+
			 ">	 Expand fidmarks out\n"+
			 "c/C  Clear nearest-one/all fidmark(s)\n"+
			 "s	 Save fidmarks to file\n"+
			 "l	 Load fidmarks from file\n"+
			 "\n"+
			 "Eyecal marks\n"+
			 "-----------------------------------------\n"+
			 ".	 Set eyecal point (period) at cursor\n"+
			 ",	 Delete nearest eyecal point (comma)\n"+
			 "\n"+
			 "Other\n"+
			 "-----------------------------------------\n"+
			 "/	 Mark box corner (twice to set box)\n"+
			 "x	 postion message window at cursor\n"+
			 "R-mouse access fixation menu\n"+
			 "M-mouse access task-specific dropdown\n",
			 astext=1)

	def deltags(self, taglist):
		for tag in taglist:
				self.canvas.delete(tag)
		return []

	def eye_at(self, rx, ry, xt=False):
		# throttle eye trace update to 60hz max:
		now = time.time()
		if (now - self._lastEyeUpdate) < 0.008:
			return
		self._lastEyeUpdate = now

		# clip at display edges
		rx = max(-self.hw+5, min(self.hw-5, rx))
		ry = max(-self.hh+5, min(self.hh-5, ry))
		(x, y) = self.cart2canv(rx, ry)

		C = self.canvas
		if self._eye_lxy is not None:
            l = C.create_line(self._eye_lxy[0], self._eye_lxy[1], x, y,
							  fill="red")
			C.tag_lower(l)
            self._eye_trace_lines.append(l)
			if len(self._eye_trace_lines) > self._eye_trace_maxlen:
				C.delete(self._eye_trace_lines[0])
				self._eye_trace_lines.pop(0)
        self._eye_lxy = (x, y)

		tag = C.create_text(x, y, text='+',
							font=('Courier', 10),
							fill='red', justify=CENTER)
		C.tag_lower(tag)

		self._eye_trace.append(tag)
        if len(self._eye_trace) > self._eye_trace_maxlen:
			C.delete(self._eye_trace[0])
			del self._eye_trace[0]

        if self._eye_at is None:
            self._eye_at = (C.create_text(x+1, y+1, text='o',
                                          font=('Courier', 10),
                                          fill='white', justify=CENTER),
                            C.create_text(x, y, text='o',
                                          font=('Courier', 10),
                                          fill='black', justify=CENTER))
        for i in self._eye_at:
            C.coords(i, x, y)
			C.tag_raise(i)

		if xt:
			# update X-T display
			n = self._traceptr
			h = self._htrace[n]
			v = self._vtrace[n]
			self._traceptr = (self._traceptr + 1) % len(self._htrace)
			n = self._traceptr
			h = self._htrace[n]
			v = self._vtrace[n]
			C.coords(h, n, 50 + rx/10.0, n+1, 50 + rx/10.0)
			C.coords(v, n, 50 + ry/10.0, n+1, 50 + ry/10.0)
			C.coords(self._tracecursor, n, 50-20, n, 50+20)

	def canv2cart(self, x, y=None):
		"""Convert canvas (including event position) coords to
        frame buffer coords.

        Inverse of cart2canv() method.

		Tkinter canvas coords have (0,0) in upper left, frame buffer
		has 0,0 at center and has normal Cartesian directions.

		"""
		if y is None:
			(x, y) = x
		return (x - (self.hw), (self.h - y) - self.hh)

	def cart2canv(self, x, y=None):
		"""Convert frame buffer coords to canvas coords

		Inverse of canv2cart() method.
		"""
		if y is None:
            (x, y) = x
		return (self.hw + x, self.hh - y)

	def drawaxis(self, axis=1, sync=1):
		if axis:
			# draw cardinal axis (0,0)
			(x, y) = self.cart2canv(0, 0)
			self.canvas.create_line(x, 0, x, self.h, width=1,
									 fill='black', dash=(7,2))
			self.canvas.create_line(0, y, self.w, y, width=1,
									 fill='black', dash=(7,2))

		if sync and self.app.fb.syncinfo:
			(sx, sy, ss) = self.app.fb.syncinfo
			(a, b) = self.cart2canv(sx - ss/2, sy - ss/2)
			(c, d) = self.cart2canv(sx + ss/2, sy + ss/2)
			self.canvas.create_rectangle(a, b, c, d, fill='black')

		# gridinterval is pix/deg
		d = int(round(self.gridinterval))
		if d > 0:
			(xo, yo) = self.cart2canv(0,0)
			for x in range(0, int(round(self.w/2)), d):
				for y in range(0, int(round(self.h/2)), d):
					for (sx, sy) in ((1,1),(-1,1),(-1,-1),(1,-1)):
						if x != 0 and y != 0:
							if ((round(x/d)%5) == 0 or (round(y/d)%5) == 0):
								color = 'gray50'
							else:
								color = 'gray70'
							self._axis.append(
								self.canvas.create_rectangle(xo+(sx*x),
															 yo+(sy*y),
															 xo+(sx*x),
															 yo+(sy*y),
															 outline=color,
															 fill=color))

	def manualbox(self):
		x1 = float(min(self.markstack[0][0], self.markstack[1][0]))
		x2 = float(max(self.markstack[0][0], self.markstack[1][0]))
		y1 = float(min(self.markstack[0][1], self.markstack[1][1]))
		y2 = float(max(self.markstack[0][1], self.markstack[1][1]))
		cx = (x1 + x2)/2
		cy = (y1 + y2)/2
		w = (x2 - x1)
		h = (y2 - y1)
		s = askstring('position box exactly',
					  'Enter center-x, center-y, width, height:',
					  initialvalue='%d,%d,%d,%d' % (cx, cy, w, h))
		try:
			s = map(int, s.split(','))
		except ValueError:
			return
		if len(s) == 3:
			[cx, cy, r] = s
			w = 2*r
			h = 2*r
		elif len(s) == 4:
			[cx, cy, w, h] = s
		else:
			return
		self.clearbox()
		self.markstack.append(((cx-w), (cy-h)))
		self.markstack.append(((cx+w), (cy+h)))
		self.drawbox()

	def clearbox(self):
		self.setbox(clear=1)

	def setbox(self, clear=None):
		if clear is None:
			# mouse position in retinal coords (re fixspot)
			mx = self.mousex + self.xoffset - self.fix_x
			my = self.mousey + self.yoffset - self.fix_y
			self.markstack.append((mx, my))
			self.markstack = self.markstack[-2:]
		else:
			self.markstack = []
		self.drawbox()

	def drawbox(self):
		if self.markbox:
			self.canvas.delete(self.markbox)
			self.markbox = None
		if len(self.markstack) == 1:
			x1, y1 = self.markstack[0][0], self.markstack[0][1]
			x1 = self.fix_x + x1
			y1 = self.fix_y + y1
			x1,y1 = self.cart2canv(x1, y1)
			self.markbox = self.canvas.create_rectangle(x1-1,y1-1,x1+1,y1+1,
														 fill='black',
														 outline="black")
		elif len(self.markstack) == 2:
			x1, y1 = self.markstack[0][0], self.markstack[0][1]
			x1 = self.fix_x + x1
			y1 = self.fix_y + y1
			x1,y1 = self.cart2canv(x1, y1)

			x2, y2 = self.markstack[1][0], self.markstack[1][1]
			x2 = self.fix_x + x2
			y2 = self.fix_y + y2
			x2,y2 = self.cart2canv(x2, y2)

			self.markbox = self.canvas.create_rectangle(x1,y1,x2,y2,
														 fill=None,
														 outline="red",
														 dash=(5,5))

	def _key(self, ev):
		# ev.state values:
		# NOMOD = 0; SHIFT = 1; CONTROL = 4; ALT = 8; WIN = 64

		c = ev.keysym
		if c == 'Left':
			if ev.state:
				# any modifier...
				self.app.eyeshift(x=1,y=0)
			else:
				self._movefidmarks(xoff=-1, yoff=0)
		elif c == 'Right':
			if ev.state:
				# any modifier...
				self.app.eyeshift(x=-1,y=0)
			else:
				self._movefidmarks(xoff=1, yoff=0)
		elif c == 'Up':
			if ev.state:
				# any modifier...
				self.app.eyeshift(x=0,y=-1)
			else:
				self._movefidmarks(xoff=0, yoff=1)
		elif c == 'Down':
			if ev.state:
				# any modifier...
				self.app.eyeshift(x=0,y=1)
			else:
				self._movefidmarks(xoff=0, yoff=-1)
		elif c == 'less':
			self._scalefidmarks(-1)
		elif c == 'greater':
			self._scalefidmarks(1)
		if c == 'f':
			self._putfidmark()
		elif c == 'c':
			self._clearfidmark()
		elif c == 'C':
			self._clearfidmark(all=1)
		elif c == 's':
			self.savefidmarks()
		elif c == 'l':
			self.loadfidmarks()
		elif c == 'x':
			self._placenote(ev.x, ev.y)
		elif c == 'v':
			self._showfidmarks()
		elif c == 'period':
			self.addpoint(ev.x, ev.y)
		elif c == 'comma':
			self.deletepoint(ev.x, ev.y)
		elif c == 'slash':
			self.setbox()
		elif not self.userhook is None:
			return self.userhook(self.userhook_data, c, ev)
		else:
			pass
		return 1

	def addpoint(self, x, y):
		"""(x, y) specifies point in CANVAS coords (0,0) is upper left"""
		(px, py) = (int(round(x - (self.w/2.0))), int(round((self.h/2.0) - y)))
		d = 2; o = 6;
		tb = self.canvas.create_oval(x-o, y-o, x+o, y+o, fill='red', width=0)
		t = self.canvas.create_text(x, y, anchor=CENTER, justify=CENTER,
									text='i', fill='white')
		self.points.append((px, py, t, tb))

	def deletepoint(self, x, y):
		"""
		Delete nearest point to (x, y) in CANVAS coords.
		(0,0) is upper left.
		"""
		px = int(round(x - (self.w/2.0)))
		py = int(round((self.h/2.0)) - y)
		nearest = None
		for n in range(len(self.points)):
			(x, y, t, tb) = self.points[n]
			d = (px - x) ** 2 + (py - y) ** 2
			if n == 0 or d < dmin:
				dmin = d
				nearest = n
		if not nearest is None:
			(x, y, t, tb) = self.points[nearest]
			self.canvas.delete(t)
			self.canvas.delete(tb)
			self.points.remove(self.points[nearest])

	def querypoint(self, x, y):
		"""
		Identify nearest point to (x, y) in CANVAS coords.
		(0,0) is upper left.
		"""
		px = int(round(x - (self.w/2.0)))
		py = int(round((self.h/2.0) - y))
		nearest = None
		for n in range(len(self.points)):
			(x, y, t, tb) = self.points[n]
			d = (px - x) ** 2 + (py - y) ** 2
			if n == 0 or d < dmin:
				dmin = d
				nearest = n
		if not nearest is None:
			return (x, y)
		else:
			return (None, None)

	def clearpoints(self):
		"""Clear all points"""
		for n in range(len(self.points)):
			(x, y, t, tb) = self.points[n]
			self.canvas.delete(t)
			self.canvas.delete(tb)
		self.points = []

	def savepoints(self, filename=None):
		"""Save points to file"""

		if filename is None:
			from pype import subjectrc
			(filename, mode) = filebox.SaveAs(initialdir=subjectrc(),
											  pattern="*.pts", append=None,
											  text='Save points to file')
		if filename:
			file = open(filename, 'w')
			cPickle.dump(self.points, file)
			file.close()

	def loadpoints(self, filename=None, merge=None):
		"""Load points from file (pickle file make by savepoints)"""
		if filename is None:
			from pype import subjectrc
			(filename, mode) = filebox.Open(initialdir=subjectrc(),
											pattern="*.pts",
											text='Load points from save file')
			if filename is None:
				return
		try:
			file = open(filename, 'r')
			newpoints = cPickle.load(file)
			file.close()
		except IOError:
			return
		except EOFError:
			return

		if not merge:
			self.clearpoints()

		for n in range(len(newpoints)):
			if len(newpoints[n]) == 3:
				(px, py, t) = newpoints[n]
			else:
				(px, py, t, tb) = newpoints[n]
			x = int(round(px + (self.w/2.0)))
			y = int(round((self.h/2.0) - py))
			self.addpoint(x, y)

	def loadpoints_ascii(self, filename=None, merge=None):
		"""
		Load points from ascii file.
		One point per line containing X and Y position in
		pixels separated by commas or spaces
		"""
		if filename is None:
			from pype import subjectrc
			(filename, mode) = filebox.Open(initialdir=subjectrc(),
											pattern="*.asc",
											text='Load points from ASCII file')
			if filename is None:
				return
		try:
			fp = open(filename, 'r')
		except IOError:
			return

		if not merge:
			self.clearpoints()

		while 1:
			l = fp.readline()
			if not l:
				break
			if string.find(l, ',') >= 0:
				l = l.split(',')
			else:
				l = l.split()
			px = int(l[0])
			py = int(l[1])
			x = int(round(px + (self.w/2.0)))
			y = int(round((self.h/2.0) - py))
			self.addpoint(x, y)
		fp.close()

	def getpoints(self):
		"""
		Get vector of points in proper SCREEN/WORLD coords.
		(0,0) is center of the screen!!
		"""
		points = []
		for n in range(len(self.points)):
			(x, y, t, tb) = self.points[n]
			points.append((x, y))
		return points

	def _phototoggle(self):
		self._photomode = self._photomode_tvar.get()

	def _mouse1(self, ev=None):
		x, y = self.canvas.window2scaled(ev.x, ev.y)
		x, y = self.canv2cart(x, y)
		self.app.eyeshift(x=x, y=y, rel=False)

	def _space(self, ev=None):
		if ev.type == "2":
			# key-press
			self.app.eyebar = 1
		elif ev.type == "3":
			# key-release
			self.app.eyebar = 0
		self.app._int_handler(None, None, iclass=1, iarg=0)

	def _mouse_motion(self, ev=None):
		if not ev is None:
			x, y = self.canvas.window2scaled(ev.x, ev.y)
			(self.mousex, self.mousey) = self.canv2cart(x, y)
            rx, ry = (self.mousex-self.fix_x, self.mousey-self.fix_y,)
        else:
            rx, ry = 0, 0
        self._mouseinfo_x.configure(text='X:%5d' % rx)
        self._mouseinfo_y.configure(text='Y:%5d' % ry)

	def _mouse_enter(self, ev):
		self.canvas.focus_set()

	def _mouse_leave(self, ev):
		pass

	def display(self, displaylist=None):
		"""
		Automatically-draw a DisplayList object as a set of icons on the
		UserDisplay (faster than exact copies).

		**displaylist** - DisplayList or None for clear all.

		"""

		# first clear previsou displaylist icons
		for icon in self._displaylist_icons:
			self.icon(icon)

		if displaylist is None:
			return

		self._displaylist_icons = []
		if not displaylist is None:
			for s in displaylist.sprites:
				if s._on:
					ii = []
					if hasattr(s, 'points'):
						xy = s.points	# PolySprite
						for n in range(1,len(xy)):
							(x0, y0) = self.cart2canv(xy[n-1])
							(x1, y1) = self.cart2canv(xy[n])
							ii.append(self.canvas.create_line(x0, y0, x1, y1,
															   width=s.width,
															   fill='black'))
					else:
						forcephoto = 0
						if hasattr(s, 'forcephoto'):
							forcephoto = s.forcephoto

						if forcephoto or (self._photomode and
										  s.w < 300 and s.h < 300):
							(x, y) = self.cart2canv(s.x-(s.w/2), s.y+(s.h/2))
							im = s.asPhotoImage()
							ii.append(self.canvas.create_image(x, y, anchor=NW,
																image=im))
						else:
							ii.append(self.icon(s.x, s.y, s.iw, s.ih,
												type='box', color=s.icolor))
							ii.append(self.icon(s.x, s.y, r=(s.iw+s.ih)/2.0/2.0,
												type='circle', color=s.icolor))
					for i in ii: self._displaylist_icons.append(i)

	def icon(self, x=None, y=None, w=5, h=5,
			 text=None, color='black', type='box', dash=None, r=5):
		if y is None and x is None:
			self._iconlist = self.deltags(self._iconlist)
		elif y is None:
			# just delete x from iconlist
			self.canvas.delete(x)
		else:
			# create an icon
			(x, y) = self.cart2canv(x, y)

			w = w / 2
			h = h / 2
			if not text is None:
				txt = self.canvas.create_text(x, y-(1.5*h),
											   text=text, fill='red', dash=dash)
				self._iconlist.append(txt)

			if type == 'box' or type == 1:
				tag = self.canvas.create_rectangle(x-w, y-h, x+w, y+h,
													fill='', outline=color,
													dash=dash)
			elif type == 'oval' or type == 2:
				tag = self.canvas.create_oval(x-w, y-h, x+h, y+h,
											   fill='', outline=color,
											   dash=dash)
			elif type == 'circle' or type == 3:
				if r is None:
					r = (w + h) / 2.0
				tag = self.canvas.create_oval(x-r, y-r, x+r, y+r,
											   fill='', outline=color,
											   dash=dash)
			self._iconlist.append(tag)
			return tag

	def texticon(self, x=None, y=None, text=None, color='black'):
		if y is None and x is None:
			self._iconlist = self.deltags(self._iconlist)
		elif y is None:
			# just delete x from iconlist
			self.canvas.delete(x)
		else:
			# create an icon
			(x, y) = self.cart2canv(x, y)
			tag = self.canvas.create_text(x, y, text=text, fill=color)
			self._iconlist.append(tag)
			return tag

	def _showfidmarks(self):
		s = ''
		n = 0
		for mark in self._fid_list:
			if mark:
				(tag, tagb, x, y) = mark
				s = s + ( '%3d%6d%6d\n' % (n, x, y) )
				n = n + 1
		if len(s) > 0:
			s = '### .XPOS. .YPOS.\n' + s + '\n'
		(xs, ys, r) = self.fidinfo()
		s = s + 'CTR=(%d,%d) R=%.1f px (%.1f deg)\n' % (xs, ys, r,
														r/self.gridinterval)
		s = s + 'ECC=%d px (%.1f deg)\n' % (math.sqrt((xs * xs) + (ys * ys)),
											math.sqrt((xs * xs) + (ys * ys))
											/ self.gridinterval)

		s = s + 'FIX=(%d, %d)\n' % (self.fix_x, self.fix_y)
		s = s + '>>> COORDS ARE RE:FIX <<<\n'

		warn('userdpy:fidmarks', s, astext=1)

	def fidinfo(self, file=None):
		for f in self._fidstuff:
			try:
				self.canvas.delete(f)
			except AttributeError:
				pass
		self._fidstuff = []

		n = 0
		xs = 0.
		ys = 0.
		r = 0.
		for f in self._fid_list:
			if not f is None:
				(tag, tagb, x, y) = f
				xs = xs + x;
				ys = ys + y;
				n = n + 1
		if n > 0:
			xs = int(xs / n)
			ys = int(ys / n)
			r = 0.
			for f in self._fid_list:
				if not f is None:
					(tag, tagb, x, y) = f
					r = r + math.sqrt((xs - x) * (xs - x) + (ys - y) * (ys - y))
			r = int(r / n)

		if n > 1:
			_xs = self.fix_x + xs
			_ys = self.fix_y + ys
			(cx, cy) = self.cart2canv(_xs, _ys)
			self._fidstuff = (
				self.canvas.create_text(cx, cy, anchor=CENTER, justify=CENTER,
										 fill='blue', text='o'),
				self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r,
										 fill='', outline='blue',
										 dashoffset=0,
										 dash=(10,10)),
				self.canvas.create_line(cx, cy-r, cx, cy+r, fill='blue',
										 dash=(10,10)),
				self.canvas.create_line(cx-r, cy, cx+r, cy, fill='blue',
										 dash=(10,10)),
				)
		if file:
			fp = open(file, 'w')
			fp.write('%% %s\n' % pype_aux.Timestamp())
			fp.write('% fiduciary mark data\n')
			fp.write('%\n')
			fp.write('% fix position (x,y) in framebuf coords:\n')
			fp.write('f\t%d\t%d\n' % (self.fix_x, self.fix_y))
			fp.write('% fids (x,y) in framebuf coords:\n')
			n = 0;
			for f in self._fid_list:
				if not f is None:
					(tag, tagb, x, y) = f
					fp.write('p\t%d\t%d\t%d\n' % (n, x, y))
					n = n + 1
			fp.write('%\n')
			fp.write('% rf center (x, y) framebuf coords + rad (pix):\n')
			fp.write('r\t%d\t%d\t%f\n' % (xs, ys, r))
			if len(self.markstack) > 0:
				fp.write('% markstack points (pix):\n')
				for n in range(len(self.markstack)):
					fp.write('m\t%d\t%d\t%d\n' % (n,
												  self.markstack[n][0],
												  self.markstack[n][1]))
			fp.close()

		return (xs, ys, r)

	def loadfidmarks(self, file=None):
		if file is None:
			(file, mode) = Open(initialdir=os.getcwd(),
								pattern='*.fid',
								text='Load fiduciary marks')
		if not (file is None):
			self._clearfidmarks()
			fp = open(file, 'r')
			while 1:
				l = fp.readline()
				if not l: break
				if l[0] == 'f':
					(foo, x, y) = l.split()
					self._fixset(x=int(x), y=int(y))
				elif l[0] == 'p':
					(foo, n, x, y) = l.split()
					self._putfidmark(int(x), int(y), update=0)
				if l[0] == 'm':
					(foo, n, x, y) = l.split()
					self.markstack.append((int(x), int(y)))
					self.markstack = self.markstack[-2:]
					self.drawbox()
			fp.close()
			self.fidinfo()

	def savefidmarks(self, file=None):
		if self.app:
			if self.app.use_elog:
				import elogapi
				animal = self.app.sub_common.queryv('subject')
				initf = "%s.fid" % (elogapi.GetExper(animal), )
			else:
				subj = self.app.sub_common.queryv('subject')
				cell = self.app.sub_common.queryv('cell')
				try:
					initf = "%s%04d.fid" % (subj, int(cell))
				except ValueError:
					initf = "%s%s.fid" % (subj, cell)
		else:
			initf=pype_aux.nextfile('marks.%04d.fid')

		if file is None:
			(file, mode) = SaveAs(initialdir=os.getcwd(),
								  pattern='*.fid',
								  initialfile=initf,
								  append=None,
								  text='Save fiduciary marks to file')

		if not (file is None):
			self.fidinfo(file=file)

	def _redrawfidmarks(self):
		l = self._fid_list
		self._clearfidmarks()
		for mark in l:
			if mark:
				(tag, tagb, x, y) = mark
				self._putfidmark(mx=x, my=y, update=0)
		self.fidinfo()

	def _putfidmark(self, mx=None, my=None, update=1):
		if (mx is None) or (my is None):
			# convert current mouse position to retinal coords
			mx = self.mousex + self.xoffset - self.fix_x
			my = self.mousey + self.yoffset - self.fix_y

		# draw mark at absolute screen coords:
		ax = mx + self.fix_x
		ay = my + self.fix_y
		(cx, cy) = self.cart2canv(ax, ay)

		o = 6
		tagb = self.canvas.create_oval(cx-o, cy-o, cx+o, cy+o,
									   fill='green', width=0)
		tag = self.canvas.create_text(cx, cy, anchor=CENTER, justify=CENTER,
									   fill='black', text='x')

		# save mark in retinal coords
		self._fid_list.append((tag, tagb, mx, my))
		if update:
			self.fidinfo()
		return tag

	def _clearfidmarks(self):
		self._clearfidmark(all=1)

	def _clearfidmark(self, all=None):
		if all is None:
			d1 = None
			ix = None
			n = 0
			for i in self._fid_list:
				if not i is None:
					mx = self.mousex + self.xoffset
					my = self.mousey + self.yoffset
					# remember: coords are stored re:fix
					# so convert mx,my to re:fix
					mx = mx - self.fix_x
					my = my - self.fix_y
					(tag, tagb, x, y) = i
					if d1 is None:
						ix = n
						d1 = (mx - x) * (mx - x) + (my - y) * (my - y)
					else:
						d2 = (mx - x) * (mx - x) + (my - y) * (my - y)
						if d2 < d1:
							ix = n
							d1 = d2
				n = n + 1

			if not d1 is None:
				(tag, tagb, x, y) = self._fid_list[ix]
				self.canvas.delete(tag)
				self.canvas.delete(tagb)
				self._fid_list[ix] = None
		else:
			for i in self._fid_list:
				if not i is None:
					tag = i[0]
					tagb = i[1]
					self.canvas.delete(tag)
					self.canvas.delete(tagb)
			self._fid_list = []
		self.fidinfo()

	def _movefidmarks(self, xoff, yoff):
		x = self._fid_list[::]
		self._clearfidmarks()
		for mark in x:
			if mark:
				(tag, tagb, x, y) = mark
				self._putfidmark(x + xoff, y + yoff, update=0)
		self.fidinfo()

	def _scalefidmarks(self, delta):
		(xc, yc, r) = self.fidinfo()
		x = self._fid_list[::]
		self._clearfidmarks()
		for mark in x:
			if mark:
				(tag, tagb, x, y) = mark
				r = math.sqrt((x - xc)**2 + (y - yc)**2)
				t = math.atan2((y - yc), (x - xc))
				r = r + delta
				x = xc + (r * math.cos(t));
				y = yc + (r * math.sin(t));
				self._putfidmark(x, y, update=0)
		self.fidinfo()

	def _fixset(self, x=None, y=None):
		if x is None:
			x = self.mousex
		if y is None:
			y = self.mousey
		try:
			self.canvas.delete(self._fixtag)
		except AttributeError:
			pass
		self.fix_x = x
		self.fix_y = y
		if (not x is None) and (not y is None):
			(x, y) = self.cart2canv(x, y)
			self._fixtag = self.canvas.create_rectangle(x-5, y-5, x+5, y+5,
														 fill='',
														 outline='blue')
		self._redrawfidmarks()
		self.drawbox()

		# automatically update application's fixspot location info
		if self.app:
			self.app.sub_common.set('fix_x', "%d" % self.fix_x)
			self.app.sub_common.set('fix_y', "%d" % self.fix_y)

	def _fixzero(self, ev=None):
		self._fixset(x=0, y=0)

	def _fixxy(self, ev=None):
		s = askstring('fixspot', 'new fixspot:',
					  initialvalue='%d,%d' % (self.fix_x, self.fix_y))
		if s:
			s = s.split(',')
			if len(s) == 2:
				self._fixset(x=int(s[0]), y=inta(s[1]))

	def _dopopup(self, event, popupwin):
		popupwin.tk_popup(event.x_root, event.y_root)

	def set_taskpopup(self, menu=None):
		if menu is None:
			menu = Menu(self.canvas, tearoff=0)
			menu.add_command(label="no task-specific menu")
		else:
			self.taskpopup = menu
		self.canvas.bind("<Button-2>",
						  lambda ev,p=menu,s=self: s._dopopup(ev,p))

class FID(object):
	def __init__(self, file=None):
		self.fx, self.fy = 0, 0
		self.cx, self.cy, self.r = 0, 0, 0
		self.x = []
		self.y = []
		self.file = None
		if file:
			self._load(file)
			self.file = file

	def _load(self, file):
		f = open(file, 'r')
		while 1:
			l = f.readline()
			if not l:
				break
			if l[0] == 'f':
				(foo, x, y) = l.split()
				self.fx = int(x)
				self.fy = int(y)
			elif l[0] == 'p':
				(foo, n, x, y) = l.split()
				self.x.append(int(x))
				self.y.append(int(y))
			elif l[0] == 'r':
				(foo, cx, cy, r) = l.split()
				self.cx = float(cx)
				self.cy = float(cy)
				self.r = float(r)
		f.close()

if __name__ == '__main__':
	from Tkinter import *
	tk = Tk()
	bb = BlackBoard(tk, 100, 100)
	bb.frame.pack()
	tk.mainloop()
