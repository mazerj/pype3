# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-
#pypeinfo; module; owner:mazer; for:all; descr:custom handmapping engine

"""Handmap engine

To use in your own task:

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

See  http://www.mlab.yale.edu/lab/index.php/Handmap for more info.

"""

import sys
import math
#import cPickle

from pype import *
from Tkinter import *
from events import *
import pypedebug

import numpy
SEED=numpy.random.get_state()

import pype_aux

def B(x, on='ON ', off='OFF'):
	"""convert boolean value to human-readable string"""
	if x: return on
	else: return off

BLINK_STATES = ['OFF', 'ON', 'BLINK']
BTAG = ['OFF', '', '']

_n = 0
BAR=_n ; _n += 1
RECT=_n ; _n += 1
CART=_n ; _n += 1
HYPER=_n ; _n += 1
POLAR=_n ; _n += 1
DISK=_n ; _n += 1
CIRCLE=_n ; _n += 1

BARMODES = {
    BAR:'bar',
    CART:'cart',
    HYPER:'hyper',
    POLAR:'polar',
    RECT:'rect',
    CIRCLE:'circle',
    DISK:'disk',
    }

class _Probe(object):
	def __init__(self, app):
		self.ppd = float(app.rig_common.queryv('mon_ppd'))

		self.lock = 0
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
		self.app.udpy.xoffset = self.xoff
		self.app.udpy.yoffset = self.yoff
		self.live = 0
		self.blink_freq = 1.0
		self.blink_state = 0
		self.inten = 100
		self.colorstr = None
		self.barmode = BAR
		self.sfreq = 1.0
		self.rfreq = 0.0
		self.major_ax = None
		self.minor_ax = None
		self.onoff = None
		self.bg = sum(app.fb.bg) / len(app.fb.bg)
		self.showinfo = 1
		self.probeid = None
		self.lw = 10

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
        import cPickle
		x = Holder()

		x.lock = self.lock
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
		x.blink_freq = self.blink_freq
		x.blink_state = self.blink_state
		x.inten = self.inten
		x.barmode = self.barmode
		x.sfreq = self.sfreq
		x.rfreq = self.rfreq
		x.lw = self.lw

		file = open(pyperc('hmapstim'), 'w')
		cPickle.dump(x, file)
		file.close()

	def load(self):
        import cPickle
		try:
			file = open(pyperc('hmapstim'), 'r')
			x = cPickle.load(file)
			file.close()
		except IOError:
			return None

		try:
			self.lock = x.lock
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
			self.blink_freq = x.blink_freq
			self.blink_state = x.blink_state
			self.inten = x.inten
			self.barmode = x.barmode
			self.sfreq = x.sfreq
			self.rfreq = x.rfreq
			self.lw = x.lw
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
			color = string.join(map(lambda x:"%d"%x, self.colorshow),',')
		except TypeError:
			color = 'noise'

		z = self.sfreq/self.length

		s = ""
		s = s + "  o:%s " % B(self.xoff, 'OFFST', 'MOUSE')
		s = s + "  z:%s (mb2) " % B(self.lock, 'LOCK', 'FREE')
		s = s + "\n"
		s = s + "  j:%s " % B(self.jitter, 'ON  ', 'OFF ')
		s = s + "  d:%s " % B(self.drift, 'ON  ', 'OFF ')
		s = s + "  b:%s " % BLINK_STATES[self.blink_state]
		s = s + "\n"
		s = s +	"  h:hide info       p:post info\n"
		s = s + "\n"
		s = s +		" qw  length     %d\n" % self.length
		s = s +		" er  width      %d\n" % self.width
		s = s +		" 89  dir/ori    %d:%d deg\n" % angle
		s = s + "\n"
		s = s +		"  m  stim type  %s\n" % BARMODES[self.barmode]
		s = s +     " nN  rgb        %s\n" % color
		s = s +		"1-6  color      %s\n" % self.colorname
		s = s +		" iI  inten      %d\n" % self.inten
		s = s +		" -=  linewidth  %d\n" % self.lw
		s = s +		" tT  drift amp  %d px\n" % self.drift_amp
		s = s +		" yY  drift freq %.1f Hz\n" % self.drift_freq
		s = s +		" kK  blink freq %.1f Hz\n" % self.blink_freq
		s = s + "\n"
		s = s +     " []  sp-freq    %.1f c/rf\n" % self.sfreq
		s = s +     "                %.4f c/deg\n" % z
		s = s +     "                %.4f c/pix\n" % (z * self.ppd)
		s = s +     " {}  rad-freq   %.1f c/rf\n" % self.rfreq

		if s[:-1] == '\n':
			s = s[:-1]
		return s

	def clear(self):
		if self.major_ax:
			self.app.udpy.canvas.delete(self.major_ax)
			self.major_ax = None
		if self.minor_ax:
			self.app.udpy.canvas.delete(self.minor_ax)
			self.minor_ax = None
		if self.onoff:
			self.app.udpy.canvas.delete(self.onoff)
			self.onoff = None

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
        import PIL.ImageTk

		if self.probeid is None or redraw:
            self.im = self.s.asImage(xscale=self.app.udpy.canvas.xscale,
                                     yscale=self.app.udpy.canvas.yscale)
            self.photoim = PIL.ImageTk.PhotoImage(self.im)
			self.probeid = self.app.udpy.canvas.create_image(x, y, anchor=NW,
															 image=self.photoim)
			self.app.udpy.canvas.lower(self.probeid)
		else:
			self.app.udpy.canvas.coords(self.probeid, x, y)
			self.app.udpy.canvas.lower(self.probeid)


	def draw(self):
		t = self.app.ts()

		if self.blink_state == 0:
			self.contrast = 0.0
		if self.blink_state == 1:
            self.contrast = 1.0
        else:
			self.contrast = float(math.sin(self.blink_freq * 2.0 * \
										   math.pi * t / 1000.) > 0)

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
            if not self.drift or self.barmode in [BAR, RECT, CIRCLE, DISK]:
                phase = 0.0
            elif self.drift:
				phase = (t/1000.0) * self.drift_freq * 360.0

			if self.barmode == BAR:
				if color is None:
                    self.s = Sprite(width=max(1,self.width/self.lw),
                                    height=max(1,self.length/self.lw),
                                    fb=self.app.fb, depth=99)
                    #self.s.noise(0.5)
                    #uniformnoise(self.s, binary=True)
                    gaussiannoise(self.s)
                    self.s.scale(self.width, self.length)
				else:
                    self.s = Sprite(width=self.width,
                                    height=self.length,
                                    fb=self.app.fb, depth=99)
					self.s.fill(color)
				self.s.rotateCCW(self.a, 0, 1)
			elif self.barmode == RECT:
				if color is None:
                    self.s = Sprite(width=max(1,(self.width+2*self.lw)/self.lw),
                                    height=max(1,
                                               (self.length+2*self.lw)/self.lw),
                                               fb=self.app.fb, depth=99)
					#self.s.noise(0.5)
                    #uniformnoise(self.s, binary=True)
                    gaussiannoise(self.s)
                    self.s.scale(self.width+2*self.lw, self.length+2*self.lw)
				else:
                    self.s = Sprite(width=self.width+2*self.lw,
                                    height=self.length+2*self.lw,
                                    fb=self.app.fb, depth=99)
					self.s.fill(color)
                self.s.rect(0, 0, self.width, self.length, (0,0,0,0))
				self.s.rotateCCW(self.a, 0, 1)
			elif self.barmode == DISK:
				if color is None:
                    self.s = Sprite(width=max(1,self.length/self.lw),
                                    height=max(1,self.length/self.lw),
                                    fb=self.app.fb, depth=99)
					#self.s.noise(0.5)
                    #uniformnoise(self.s, binary=True)
                    gaussiannoise(self.s)
                    self.s.scale(self.length, self.length)
				else:
					self.s = Sprite(width=self.length, height=self.length,
                                    fb=self.app.fb, depth=99)
                    self.s.fill(color)
                self.s.circmask(0, 0, self.length/2)
			elif self.barmode == CIRCLE:
                l = self.length
				if color is None:
                    self.s = Sprite(width=max(1,(l+2*self.lw)/self.lw),
                                    height=max(1, (l+2*self.lw)/self.lw),
                                    fb=self.app.fb, depth=99)
					#self.s.noise(0.5)
                    #uniformnoise(self.s, binary=True)
                    gaussiannoise(self.s)
                    self.s.scale(l+2*self.lw, l+2*self.lw)
				else:
                    self.s = Sprite(width=l+2*self.lw,
                                    height=l+2*self.lw,
                                    fb=self.app.fb, depth=99)
					self.s.fill(color)
                r = l/2
                self.s.circmask(0, 0, l/2+self.lw)
                self.s.circlefill((0,0,0,0), l/2)
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

			self.lastx = None
			self.lasty = None

		x = self.x
		y = self.y
		if self.drift and self.barmode in [BAR, RECT, CIRCLE, DISK]:
			dt = t - self.drift;
			d = self.drift_amp * \
				math.sin(self.drift_freq * 2.0 * math.pi * dt / 1000.)
			y = y + d * math.sin(math.pi * self.a / 180.)
			x = x + d * math.cos(math.pi * self.a / 180.)

		if self.jitter:
			x = x + (2 * pype_aux.urand(-3, 3, integer=1))
			y = y + (2 * pype_aux.urand(-3, 3, integer=1))


		if self.live and self.blink_state > 0:
			if self.lastx != x or self.lasty != y:
				# only actually blit if new sprite or it moved
				self.s.on()
				self.s.moveto(x, y)
                self.s.contrast = self.contrast
				self.s.blit()
				self.lastx = x
				self.lastx = y
		else:
			self.s.off()

		(x, y) = self.app.udpy.cart2canv(x, y)

		# compute sizes for indicator axes/arrow
		ih = min(60, max(40, 0.25 * self.length))
		iw = min(30, max(20, ih/2))

		# major axis:
		_tsin = ih * math.sin(math.pi * (270.0 - self.a) / 180.0)
		_tcos = ih * math.cos(math.pi * (270.0 - self.a) / 180.0)
		(x1, y1) = (x + _tcos, y + _tsin)
		(x2, y2) = (x - _tcos, y - _tsin)

		# minor axis:
		dx = iw * math.cos(math.pi * -self.a / 180.0)
		dy = iw * math.sin(math.pi * -self.a / 180.0)

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
			self.app.udpy.canvas.coords(self.onoff, x, y)
			self.app.udpy.canvas.itemconfig(self.onoff,
											text=BTAG[self.blink_state])
		else:
			self.major_ax = \
              self.app.udpy.canvas.create_line(x1, y1, x2, y2,
                                               fill='magenta',
                                               width=4)
			self.minor_ax = \
              self.app.udpy.canvas.create_line(x, y, x+dx, y+dy,
                                               arrow=LAST,
                                               fill='magenta',
                                               width=4)
			self.onoff = \
              self.app.udpy.canvas.create_text(x, y,
                                               text=BTAG[self.blink_state],
                                               anchor=CENTER,
                                               font=('Courier', 30),
                                               fill='cyan')
			for l in (self.minor_ax, self.major_ax):
				self.app.udpy.canvas.lower(l)

        if self.blink_state > 0:
            c = self.contrast > 0
        else:
            c = 0

		if self.app.hmapstate.probe.live:
            for i in (self.major_ax, self.minor_ax):
                self.app.udpy.canvas.itemconfigure(i, dash=(200,1),
                                                   width=1+(4*c))
        else:
            for i in (self.major_ax, self.minor_ax):
                self.app.udpy.canvas.itemconfigure(i, dash=(4,4),
                                                   width=1+(4*c))

		if self.showinfo:
			s = self.pp()
		else:
			s = "  h: show info"
        for i in self.text:
            self.app.udpy.canvas.itemconfig(i, text=s)

def _step(val, by=1, minval=None, maxval=None):
	val = val + by
	if not minval is None: val = max(val,minval)
	if not maxval is None: val = min(val, maxval)
	return val

def _key_handler(app, c, ev):
	p = app.hmapstate.probe

	if c == 'p':
		warn('handmap', p.pp(), grab=0, astext=1)
	elif c == 'z':
		p.lock = not p.lock
	elif c == 'h':
		p.showinfo = not p.showinfo
	elif c == 'm' or c == 'M':
		p.barmode = (p.barmode + 1) % len(BARMODES.keys())
		app.udpy.canvas.delete(p.major_ax)
		app.udpy.canvas.delete(p.minor_ax)
		app.udpy.canvas.delete(p.onoff)
		p.major_ax = None
		p.minor_ax = None
		p.onoff = None
		p.force_redraw()
	elif c == 'bracketleft':
		p.sfreq = max(1.0, p.sfreq - 1.0)
		p.force_redraw()
	elif c == 'bracketright':
		p.sfreq = p.sfreq + 1.0
		p.force_redraw()
	elif c == 'braceleft':
		p.rfreq = max(1.0, p.rfreq - 1.0)
		p.force_redraw()
	elif c == 'braceright':
		p.rfreq = p.rfreq + 1.0
		p.force_redraw()
	elif c == 'i':
		p.inten = _step(p.inten, by=-1, minval=1, maxval=100)
		p.force_redraw()
	elif c == 'I':
		p.inten = _step(p.inten, by=1, minval=1, maxval=100)
		p.force_redraw()
	elif c == 'b':
		p.blink_state = int((p.blink_state+1)%len(BLINK_STATES))
	elif c == 'k':
		p.blink_freq = _step(p.blink_freq, by=-0.1, minval=0.0)
	elif c == 'K':
		p.blink_freq = _step(p.blink_freq, by=0.1)
	elif c == 'V':
		p.verbose = not p.verbose
	elif c in '123456':
		p.colorn = ord(c) - ord('1')
		p.force_redraw()
	elif c == 'n':
		p.nextcolor(-1)
		p.force_redraw()
	elif c == 'N':
		p.nextcolor(1)
		p.force_redraw()
	elif c == '8':
		p.a = (p.a + 15) % 360
		p.force_redraw()
	elif c == '9':
		p.a = (p.a - 15) % 360
		p.force_redraw()
	elif c == 'Q':
		p.length = _step(p.length, by=1, minval=1)
		p.force_redraw()
	elif c == 'q':
		p.length = _step(p.length, by=10, minval=1)
		p.force_redraw()
	elif c == 'W':
		p.length = _step(p.length, by=-1, minval=2)
		if p.width > p.length:
			p.width = p.length-1
		p.force_redraw()
	elif c == 'w':
		p.length = _step(p.length, by=-10, minval=2)
		if p.width > p.length:
			p.width = p.length-1
		p.force_redraw()
	elif c == 'E':
		p.width = _step(p.width, by=1, minval=1)
		if p.width > p.length:
			p.length = p.width+1
		p.force_redraw()
	elif c == 'e':
		p.width = _step(p.width, by=10, minval=1)
		if p.width > p.length:
			p.length = p.width+1
		p.force_redraw()
	elif c == 'R':
		p.width = _step(p.width, by=-1, minval=1)
		p.force_redraw()
	elif c == 'r':
		p.width = _step(p.width, by=-10, minval=1)
		p.force_redraw()
	elif c == 'minus':
        p.lw = max(1, p.lw - 1)
		p.force_redraw()
	elif c == 'equal':
        p.lw = min(20, p.lw + 1)
		p.force_redraw()
	elif c == 'd':
		if p.drift:
			p.drift = 0
		else:
			p.drift = p.app.ts()
	elif c == 'y':
		p.drift_freq = _step(p.drift_freq, by=-0.1, minval=0.1)
	elif c == 'Y':
		p.drift_freq = _step(p.drift_freq, by=0.1, minval=0.1)
	elif c == 'j':
		p.jitter = int(not p.jitter)
	elif c == 'T':
		p.drift_amp = _step(p.drift_amp, by=10, minval=0)
	elif c == 't':
		p.drift_amp = _step(p.drift_amp, by=-10, minval=0)
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

def hmap_state(app, enable=None):
    if enable is None:
        return (app.taskidle is _hmap_idlefn)
    elif enable:
        app.taskidle = _hmap_idlefn
    else:
        app.taskidle = None

def hmap_enable(app):
    app.taskidle = _hmap_idlefn

def hmap_install(app):
	app.hmapstate = Holder()
	app.hmapstate.dlist = None
	app.hmapstate.probe = _Probe(app)
	app.hmapstate.hookdata = app.set_canvashook(_key_handler, app)
	app.taskidle = _hmap_idlefn
    app.hmapstate.probe.text = []
    for n in [0, 1]:
        app.hmapstate.probe.text.append(
            app.udpy.canvas.create_text(11, 36+n,
                                        font=('Courier', 8),
                                        anchor=NW,
                                        justify=LEFT,
                                        fill=['black', 'red'][n])
                                        )
    app.udpy.set_taskcallback(lambda ev, app=app: _key_handler(app, 'z', ev))


def hmap_uninstall(app):
	app.udpy.xoffset = 0
	app.udpy.yoffset = 0
	app.taskidle = None
	app.hmapstate.probe.save()
	app.hmapstate.probe.clear()
	app.set_canvashook(app.hmapstate.hookdata[0], app.hmapstate.hookdata[1])
    for i in app.hmapstate.probe.text:
        app.udpy.canvas.delete(i)
    app.udpy.set_taskcallback(None)

	del app.hmapstate


if __name__ == '__main__':
	pass
