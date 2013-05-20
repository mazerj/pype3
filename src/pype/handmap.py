# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""Handmap engine

This module was derived from hmapstim.py (10-jul-2005) and
intended to make it easy (although less flexible) for users
to incorporate handmap stimuli into their tasks.

In your task (see http://www.mlab.yale.edu/lab/index.php/Handmap too)

- At the top of your module (taskfile.py), add::

   from handmap import *

- In your "main(app)" function, add::

   hmap_install(app)

- In your "cleanup(app)" function, add::

   hmap_uninstall(app)

- Keep all the sprites you want to display within the task inside a single
  DisplayList (call in dlist) and tell hmap where to find it::

   ...
   dlist = DisplayList(fb=app.fb, ...)
   dlist.add(somesprite)
   dlist.add(someothersprite)
   ...
   hmap_set_dlist(app, dlist)

- anywhere you want the handmap stimulus to be live on the monkey display
  (typically after fixation is acquired), call::

   hmap_show(app)

- and when you don't want it to display (after an error or during the
  intertrial interval), call::

   hmap_hide(app)

- at the end of each trial, it's probably a good idea to call::

   hmap_hide(app)
   hmap_set_dlist(app, None)

Sun Jul 24 16:30:25 2005 mazer

- minor changes in cleanup code trying to figure out why Jon's tasks
  are leaving text and markers behind..

Fri May 29 14:51:00 2009 mazer

- got rid of color-bink..

"""

"""Revision History
"""

import sys
import math
import cPickle

from pype import *
from Tkinter import *
from events import *
import pypedebug

import numpy
SEED=numpy.random.get_state()

import pype_aux

def B(x):
	"""convert boolean value to human-readable string"""
	if x: return 'ON'
	else: return 'OFF'

BAR=0
CART=1
HYPER=2
POLAR=3
RDP=4
BARMODES = {BAR:'bar', CART:'cart', HYPER:'hyper', POLAR:'polar', RDP:'rdp'}

class _Probe(object):
	def __init__(self, app):
		self.lock = 0
		self.on = 1
		self.app = app
		self.s = None
		self.length = 100
		self.width = 10
		self.a = 0
		self.x = 100
		self.y = 100
		self.colorn = 0
		self.drift = 0
		self.drift_freq = 0.1;			# ~cycles/sec
		self.drift_amp = 50				# pixels
		self.jitter = 0
		self.xoff = 0
		self.yoff = 0
		self.blinktime = app.ts()
		self.app.udpy.xoffset = self.xoff
		self.app.udpy.yoffset = self.yoff
		self.live = 0
		self.blink = 0
		self.blink_freq = 1.0
		self.inten = 100
		self.colorstr = None
		self.barmode = BAR
		self.sfreq = 1.0
		self.rfreq = 0.0
		self.major_ax = None
		self.minor_ax = None
		self.bg = 128.0
		self.showinfo = 1
		self.probeid = None

		try:
			self.load()
		except:
			# [[effort to remove all unnamed exceptions:
			pypedebug.get_traceback(1)
			# effort to remove all unnamed exceptions:]]
			reporterror()
			#pass

	def __del__(self):
		self.clear()

	def save(self):
		x = Holder()

		x.lock = self.lock
		x.on = self.on
		x.length = self.length
		x.width = self.width
		x.a = self.a
		x.colorn = self.colorn
		x.drift = self.drift
		x.drift_freq = self.drift_freq
		x.drift_amp = self.drift_amp
		x.jitter = self.jitter
		x.xoff = self.xoff
		x.yoff = self.yoff
		x.live = self.live
		x.blink = self.blink
		x.blink_freq = self.blink_freq
		x.inten = self.inten
		x.barmode = self.barmode
		x.sfreq = self.sfreq
		x.rfreq = self.rfreq

		file = open(pyperc('hmapstim'), 'w')
		cPickle.dump(x, file)
		file.close()

	def load(self):
		try:
			file = open(pyperc('hmapstim'), 'r')
			x = cPickle.load(file)
			file.close()
		except IOError:
			return None

		try:
			self.lock = x.lock
			self.on = x.on
			self.length = x.length
			self.width = x.width
			self.a = x.a
			self.colorn = x.colorn
			self.drift = x.drift
			self.drift_freq = x.drift_freq
			self.drift_amp = x.drift_amp
			self.jitter = x.jitter
			self.xoff = x.xoff
			self.yoff = x.yoff
			self.app.udpy.xoffset = self.xoff
			self.app.udpy.yoffset = self.yoff
			self.live = x.live
			self.blink = x.blink
			self.blink_freq = x.blink_freq
			self.inten = x.inten
			self.barmode = x.barmode
			self.sfreq = x.sfreq
			self.rfreq = x.rfreq
		except AttributeError:
			sys.stderr.write('** loaded modified probe **\n');

		if self.s:
			del self.s
			self.s = None

	def pp(self):
		# Tue Mar  7 15:44:49 2006 mazer
		# this little bug-fixer is no longer needed -- the grating
		# functions were fixed today!
		#	a = -(self.a-90)+180
		#	a1 = a % 180

		angle = ((self.a % 180), (self.a % 180)+180)
		try:
			color = '#'+string.join(map(lambda x:"%02x"%x, self.colorshow),'')
		except TypeError:
			color = 'noise'

		s = ""
		s = s +		"  z: lock...... %s\n" % B(self.lock)
		s = s +		"  o: offset.... %s\n" % B(self.xoff)
		s = s +		"  u: on/off.... %s\n" % B(self.on)
		s = s +		"  M: bar mode.. %s\n" % BARMODES[self.barmode]
		s = s +		" []:	 s-freq. %.1f\n" % self.sfreq
		s = s +		" {}:	 r-freq. %.1f\n" % self.rfreq
		s = s +		" 89: a......... %d/%d\n" % angle
		s = s +		"n/m: rgb....... %s\n" % color
		s = s +		"1-6: color..... %s\n" % self.colorname
		s = s +		"q/w: len....... %d\n" % self.length
		s = s +		"e/r: wid....... %d\n" % self.width
		s = s +		"  j: jitter.... %s\n" % B(self.jitter)
		s = s +		"  d: drft...... %s\n" % B(self.drift)
		s = s +		"t/T: drft amp.. %dpix\n" % self.drift_amp
		s = s +		"y/Y: drft frq.. %.1fHz\n" % self.drift_freq
		s = s +		"  b: blink..... %s\n" % B(self.blink)
		s = s +		"p/P: blnk frq.. %.1fHz\n" % self.blink_freq
		s = s +		"i/I: inten..... %d\n" % self.inten
		s = s +		"\n"
		s = s +		"  h: hide/show info\n"

		return s[:-1]

	def clear(self):
		if self.major_ax:
			self.app.udpy.canvas.delete(self.major_ax)
			self.major_ax = None
		if self.minor_ax:
			self.app.udpy.canvas.delete(self.minor_ax)
			self.minor_ax = None
		self.app.udpy_note('')

	def force_redraw(self):
		"""force sprite to be redraw next cycle"""
		if self.s:
			del self.s
			self.s = None

	def color(self):
		colornames = ('noise', 'white', 'black', 'red', 'green', 'blue',
					  'yellow', 'aqua', 'purple')
		bg = self.bg
		maxi = max(255 - bg, bg)

		if self.colorn == 0:
			col = None
		elif self.colorn == 1:
			x = int(bg + (maxi * self.inten / 100.0))
			x = max(0, min(255, x))
			col = (x, x, x)
		elif self.colorn == 2:
			x = int(bg - (maxi * self.inten / 100.0))
			x = max(0, min(255, x))
			col = (x, x, x)
		elif self.colorn == 3:
			x = int(bg + (maxi * self.inten / 100.0))
			x = max(0, min(255, x))
			col = (x, 1, 1)
		elif self.colorn == 4:
			x = int(bg + (maxi * self.inten / 100.0))
			x = max(0, min(255, x))
			col = (1, x, 1)
		elif self.colorn == 5:
			x = int(bg + (maxi * self.inten / 100.0))
			x = max(0, min(255, x))
			col = (1, 1, x)
		elif self.colorn == 6:
			x = int(bg + (maxi * self.inten / 100.0))
			x = max(0, min(255, x))
			col = (x, x, 1)
		elif self.colorn == 7:
			x = int(bg + (maxi * self.inten / 100.0))
			x = max(0, min(255, x))
			col = (1, x, x)
		elif self.colorn == 8:
			x = int(bg + (maxi * self.inten / 100.0))
			x = max(0, min(255, x))
			col = (x, 1, x)
		return (col, colornames[self.colorn])

	def nextcolor(self, incr=1):
		self.colorn = (self.colorn + incr) % 9

	def showprobe(self, x=0, y=0, redraw=1):
		if self.probeid and not self.s.on:
			self.app.udpy.canvas.delete(self.probeid)
			self.probeid = None
		elif self.probeid is None or redraw:
			self.photoim = self.s.asPhotoImage()
			self.probeid = self.app.udpy.canvas.create_image(x, y, anchor=NW,
															 image=self.photoim)
			self.app.udpy.canvas.lower(self.probeid)
		else:
			self.app.udpy.canvas.coords(self.probeid, x, y)
			self.app.udpy.canvas.lower(self.probeid)


	def draw(self):
		t = self.app.ts()

		ms_bperiod = 1000.0 / self.blink_freq
		if (self.blink > 0) and (t - self.blinktime) > (ms_bperiod/2):
			self.on = not self.on
			self.blinktime = t

		(color, name) = self.color()
		if color:
			rc = self.inten * (color[0]-1) / 254.0 / 100.0
			gc = self.inten * (color[1]-1) / 254.0 / 100.0
			bc = self.inten * (color[2]-1) / 254.0 / 100.0
		else:
			rc = 1.0
			gc = 1.0
			bc = 1.0
		self.colorshow = color
		self.colorname = name
		olds = self.s
		if (self.s is None) or self.drift:
			if self.drift and not (self.barmode == BAR):
				phase = (t/1000.0) * self.drift_freq * 360.0
			else:
				phase = 0.0;

			if self.barmode == BAR:
				self.s = Sprite(width=self.width, height=self.length,
								fb=self.app.fb, depth=99)
				if color is None:
					self.s.noise(0.5)
				else:
					self.s.fill(color)
				self.s.rotateCCW(self.a, 0, 1)
			elif self.barmode == CART:
				l = self.length
				self.s = Sprite(width=l, height=l,
								fb=self.app.fb, depth=99)
				if color is None or sum(color) < 3:
					# 'black' is just 90deg phase shift of 'white'
					rc,gc,bc = -1.0,-1.0,-1.0
				singrat(self.s, abs(self.sfreq), phase, self.a,
						1.0*rc, 1.0*gc, 1.0*bc)
				self.s.alpha_aperture(l/2)
			elif self.barmode == HYPER:
				l = self.length
				self.s = Sprite(width=l, height=l,
								fb=self.app.fb, depth=99)
				if color is None or sum(color) < 3:
					# 'black' is just 90deg phase shift of 'white'
					rc,gc,bc = -1.0,-1.0,-1.0
				hypergrat(self.s, abs(self.sfreq), phase, self.a,
						  1.0*rc, 1.0*gc, 1.0*bc)
				self.s.alpha_aperture(l/2)
			elif self.barmode == POLAR:
				l = self.length
				self.s = Sprite(width=l, height=l,
								fb=self.app.fb, depth=99)
				if self.rfreq < 0:
					pol = -1
				else:
					pol = 1
				if color is None or sum(color) < 3:
					# 'black' is just 90deg phase shift of 'white'
					rc,gc,bc = -1.0,-1.0,-1.0
				polargrat(self.s, abs(self.sfreq), abs(self.rfreq), phase, pol,
						  1.0*rc, 1.0*gc, 1.0*bc)
				self.s.alpha_aperture(l/2)
			elif self.barmode == RDP:
				# rds
				l = self.length
				self.s = Sprite(width=l/3, height=l/3, fb=self.app.fb, depth=99)
				if color is None:
					c = (255,255,255)
				else:
					c = color
				simple_rdp(self.s, fraction=0.10,
						   fgcolor=c, bgcolor=(self.bg,self.bg,self.bg),
						   rseed=SEED)
				self.s.scale(l, l)
				self.s.alpha_aperture(l/2)

			self.lastx = None
			self.lasty = None

		if self.drift and self.barmode == RDP:
			# advance the RDP one tick..
			simple_rdp(self.s, self.a, self.drift_freq, rseed=SEED)

		x = self.x
		y = self.y
		if self.drift and (self.barmode == BAR):
			dt = t - self.drift;
			d = (self.drift_amp * 
				 math.sin(self.drift_freq * 2.0 * math.pi * dt / 1000.))
			y = y + d * math.sin(math.pi * self.a / 180.)
			x = x + d * math.cos(math.pi * self.a / 180.)

		if self.jitter:
			x = x + (2 * pype_aux.urand(-3, 3, integer=1))
			y = y + (2 * pype_aux.urand(-3, 3, integer=1))


		if self.on and self.live:
			if self.lastx != x or self.lasty != y:
				# only actually blit if new sprite or it moved
				self.s.on()
				self.s.moveto(x, y)
				self.s.blit()
				self.lastx = x
				self.lastx = y
		else:
			self.s.off()

		(x, y) = self.app.udpy.fb2can(x, y)

		# compute line for long axis (orientation indicator)
		hh = max(10, self.length / 2.0)
		hh = 15
		_tsin = hh * math.sin(math.pi * (270.0 - self.a) / 180.0)
		_tcos = hh * math.cos(math.pi * (270.0 - self.a) / 180.0)
		(x1, y1) = (x + _tcos, y + _tsin)
		(x2, y2) = (x - _tcos, y - _tsin)

		# compute line for short axis (direction indicator)
		hw = max(10, self.width / 2.0)
		hw = 15
		dx = hw * math.cos(math.pi * -self.a / 180.0)
		dy = hw * math.sin(math.pi * -self.a / 180.0)

		# compute photoimage position in canvas coords
		cx = x - (self.s.w / 2.0)
		cy = y - (self.s.h / 2.0)

		if not self.s is olds:
			# new sprite, redraw the probe
			self.showprobe(x=cx, y=cy, redraw=1)
		else:
			self.showprobe(x=cx, y=cy, redraw=0)

		if self.major_ax:
			self.app.udpy.canvas.coords(self.major_ax, x1, y1, x2, y2)
			self.app.udpy.canvas.coords(self.minor_ax, x, y, x+dx, y+dy)
		else:
			self.major_ax = self.app.udpy.canvas.create_line(x1, y1, x2, y2,
															 width=4)
			self.minor_ax = self.app.udpy.canvas.create_line(x, y, x+dx, y+dy,
															 fill='blue',
															 arrow=LAST,
															  width=4)
			for l in (self.minor_ax, self.major_ax):
				self.app.udpy.canvas.lower(l)

		if self.on and self.app.hmapstate.probe.live:
			self.app.udpy.canvas.itemconfigure(self.major_ax, fill='green')
		else:
			self.app.udpy.canvas.itemconfigure(self.major_ax, fill='red')

		if self.showinfo:
			self.app.udpy_note(self.pp())
		else:
			self.app.udpy_note("  h: hide/show info")


def step(val, by=1, minval=None, maxval=None):
	val = val + by
	if minval and val < minval:
		val = minval
	elif maxval and val > maxval:
		val = maxval
	return val


def _key_handler(app, c, ev):
	p = app.hmapstate.probe

	if c == 'z':
		p.lock = not p.lock
	elif c == 'h':
		p.showinfo = not p.showinfo
	elif c == 'M':
		p.barmode = (p.barmode + 1) % len(BARMODES.keys())
		app.udpy.canvas.delete(p.major_ax)
		app.udpy.canvas.delete(p.minor_ax)
		p.major_ax = None
		p.minor_ax = None
		p.force_redraw()
	elif c == 'bracketleft':
		p.sfreq = step(p.sfreq, by=-0.2)
		p.force_redraw()
	elif c == 'bracketright':
		p.sfreq = step(p.sfreq, by=0.2)
		p.force_redraw()
	elif c == 'braceleft':
		p.rfreq = round(step(p.rfreq, by=-1.0))
		p.force_redraw()
	elif c == 'braceright':
		p.rfreq = round(step(p.rfreq, by=1.0))
		p.force_redraw()
	elif c == 'b':
		p.blink = step(p.blink, by=1)
		if p.blink >= 2: p.blink = 0
		p.blinktime = app.ts()
		if not p.blink:
			p.on = 1
	elif c == 'i':
		p.inten = step(p.inten, by=-1, minval=1, maxval=100)
		p.force_redraw()
	elif c == 'I':
		p.inten = step(p.inten, by=1, minval=1, maxval=100)
		p.force_redraw()
	elif c == 'p':
		p.blink_freq = step(p.blink_freq, by=-0.1, minval=0.1)
	elif c == 'P':
		p.blink_freq = step(p.blink_freq, by=0.1, minval=0.1)
	elif c == 'u':
		p.on = not p.on
	elif c in '123456':
		p.colorn = ord(c) - ord('1')
		p.force_redraw()
	elif c == 'n':
		p.nextcolor(-1)
		p.force_redraw()
	elif c == 'm':
		p.nextcolor(1)
		p.force_redraw()
	elif c == '8':
		p.a = (p.a + 15) % 360
		p.force_redraw()
	elif c == '9':
		p.a = (p.a - 15) % 360
		p.force_redraw()
	elif c == 'q':
		p.length = step(p.length, by=1, minval=1)
		p.force_redraw()
	elif c == 'Q':
		p.length = step(p.length, by=10, minval=1)
		p.force_redraw()
	elif c == 'w':
		p.length = step(p.length, by=-1, minval=2)
		if p.width > p.length:
			p.width = p.length-1
		p.force_redraw()
	elif c == 'W':
		p.length = step(p.length, by=-10, minval=2)
		if p.width > p.length:
			p.width = p.length-1
		p.force_redraw()
	elif c == 'e':
		p.width = step(p.width, by=1, minval=1)
		if p.width > p.length:
			p.length = p.width+1
		p.force_redraw()
	elif c == 'E':
		p.width = step(p.width, by=10, minval=1)
		if p.width > p.length:
			p.length = p.width+1
		p.force_redraw()
	elif c == 'r':
		p.width = step(p.width, by=-1, minval=1)
		p.force_redraw()
	elif c == 'R':
		p.width = step(p.width, by=-10, minval=1)
		p.force_redraw()
	elif c == 'd':
		if p.drift:
			p.drift = 0
		else:
			p.drift = p.app.ts()
	elif c == 'j':
		p.jitter = not p.jitter
	elif c == 'T':
		p.drift_amp = step(p.drift_amp, by=10, minval=0)
	elif c == 't':
		p.drift_amp = step(p.drift_amp, by=-10, minval=0)
	elif c == 'Y':
		p.drift_freq = step(p.drift_freq, by=0.1, minval=0.1)
	elif c == 'y':
		p.drift_freq = step(p.drift_freq, by=-0.1, minval=0.1)
	elif c == 'o':
		if app.hmapstate.probe.xoff:
			app.hmapstate.probe.xoff = 0
			app.hmapstate.probe.yoff = 0
		else:
			app.hmapstate.probe.xoff = -50
			app.hmapstate.probe.yoff =	50
		app.udpy.xoffset = app.hmapstate.probe.xoff
		app.udpy.yoffset = app.hmapstate.probe.yoff
	else:
		return 0
	return 1

def _hmap_idlefn(app):
	p = app.hmapstate.probe
	if not p.lock:
		p.x = app.udpy.mousex + app.hmapstate.probe.xoff
		p.y = app.udpy.mousey + app.hmapstate.probe.yoff

	if app.running:
		# if running, then may need to draw fixspot etc..
		if app.hmapstate.dlist:
			app.hmapstate.dlist.update()
		else:
			app.fb.clear()
	p.draw()
	if app.running:
		app.fb.flip()

def hmap_set_dlist(app, dlist):
	app.hmapstate.dlist = dlist

def hmap_show(app, update=None):
	app.hmapstate.probe.live = 1
	if update:
		_hmap_idlefn(app)

def hmap_hide(app, update=None):
	app.hmapstate.probe.live = 0
	if update:
		_hmap_idlefn(app)

def hmap_install(app):
	app.hmapstate = Holder()
	app.hmapstate.dlist = None
	app.hmapstate.probe = _Probe(app)
	app.hmapstate.hookdata = app.set_canvashook(_key_handler, app)
	app.taskidle = _hmap_idlefn

def hmap_uninstall(app):
	app.udpy.xoffset = 0
	app.udpy.yoffset = 0
	app.taskidle = None
	app.hmapstate.probe.save()
	app.hmapstate.probe.clear()
	app.set_canvashook(app.hmapstate.hookdata[0], app.hmapstate.hookdata[1])
	del app.hmapstate

if __name__ == '__main__':
	pass
