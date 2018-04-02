# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""Pygame/SDL/OpenGL based sprite engine.

Pygame-based sprite engine for doing real-time graphics
during behavioral/neurophysiological experiments.

Author -- James A. Mazer (james.mazer@yale.edu)

"""

"""Revision History

Mon Jan	 6 18:03:09 2003 mazer

- added userdict to Image/Sprite classes

Tue Jul	 5 12:28:24 2005 mazer

- fastblit now pays attention to the on/off flag!

Sun Jul 24 15:46:53 2005 mazer

- added synclevel=255 to FrameBuffer __init__ method.

Mon Nov 21 18:35:39 2005 mazer

- Sprite.clone() method correctly sets the sprite name to avoid
  errors on deletion.

Tue Mar	 7 09:26:05 2006 mazer

- Added Sprite.rotateCW(0 and Sprite.rotateCCW() methods. This is
  because the standard pygame-based rotation method actually rotates
  CW, and really we want CCW rotation. This has previously been
  corrected at the task level..

Tue Mar	 7 16:27:40 2006 mazer

- oops - missed one thing -> barsprite

Fri Mar 24 11:09:23 2006 mazer

- fixed fb.show()/hide() methods - I think these should work
  now, at least with the OPENGL driver..

Mon Jan	 5 14:36:35 2009 mazer

- got rid of unrender() method - you can force unrendering by calling
  render with the clear=1 optional argument, but otherwise, deleting the
  sprite will free up the render storage to avoid leaks

- noticed that fastblit() method was blitting even when the sprite was
  not turn off - fixed that and deleted a redundant coordinate calculation

- generate cleanup while considering switching to a pure OpenGL solution..

- moved gen{axes,d,rad,theta} axes generator functions into spritetools

Fri Jan 23 12:37:10 2009 mazer

- Framebuffer - removed dga and videodriver options. Now just specify
  full screen or not and opengl or not and let the code sort out the
  best driver. Basically for GL you get quartz or X11 depending on
  the platform and for non-GL you get quartz on mac, DGA for linux-fullscreen
  and X11 for anything else.

- Framebuffer - only flag you can specify now is full screen, DOUBLEBUFFER
  and HWSURFACE are always..

- fopengl -> opengl

- everything's much simpler now - only big confusion points are:

  - why can't we request a specific bits/pixel in opengl mode..

  - why does ALPHAMASKS need hard coding?

Tue Mar 31 12:21:17 2009 mazer

- made lower right-hand corner default syncpulse position

- fb.phdiode_mode -> fb.sync_mode

Fri Apr 17 10:45:46 2009 mazer

- added mouse options for FrameBuffer/quickinit

- improved noise() function (added color flag) (from numsprite.py)

- Tue Jul  7 10:25:19 2009 mazer

  - FrameBuffer.syncinfo is stashed to allow UserDisplay to automatically
	mark the sync spot location on the screen..

Wed Jan 26 14:49:42 2011 mazer

- added antialiasing option to PolySprite clas

Fri May	 6 14:44:29 2011 mazer

- Converted to pure OpenGL -- OpenGL is needed now. This basically
  means that everything is done using texture memory, should be
  faster and more flexible..

- render() method now actually moves image data onto video card
  texture memory, so blits should be super fast. This also means
  that rotations and contrast changes can be applied using the
  GL pipeline (use sprite's set_rotation() and set_contrast()
  methods).

Mon May 16 13:51:44 2011 mazer

- removed MpegMovie class for now -- this isn't working, perhaps
  due to a known pygame bug.. Plus, nobody's using it for anything..

- _ImageBase was folded directly into the Sprite class

Tue May 17 16:29:01 2011 mazer

- MovieDecoder added -- this can decode MPEG movies into a live
  sprite that can be blitted as normal. This is more flexible and
  actually works...

Thu Jun 23 11:15:37 2011 mazer

- root access no longer required with opengl..

Fri Jan 13 10:39:00 2012 mazer

- added DisplayList.after() method -- allows for timer-based actions
  during updating of display list

"""

import os
import sys
import time
import string
import types
import math

try:
	from guitools import Logger
	from spritetools import *
	from pypedebug import keyboard
	from events import MARKFLIP
except ImportError:
	def Logger(s, *args):
		sys.stderr.write(s)

try:
	import numpy as np
except ImportError:
	Logger('sprite: numpy is required.\n')
	sys.exit(1)

try:
	import OpenGL
	OpenGL.ERROR_CHECKING = False
	OpenGL.ERROR_LOGGING  = False
	OpenGL.ERROR_ON_COPY  = True
	import OpenGL.GL as ogl
except ImportError:
	Logger('sprite: python opengl OpenGL package required.\n')
	sys.exit(1)


try:
	import pygame
	from pygame.constants import *
	if pygame.version.vernum[0] <= 1 and pygame.version.vernum[1] < 9:
		Logger('sprite: pygame >= 1.9 required')
		sys.exit(1)
	# force pygame to use numpy over Numeric in case they are both
	# installed
	pygame.surfarray.use_arraytype('numpy')
except ImportError:
	Logger('sprite: python pygame package required.\n' % __name__)
	sys.exit(1)


GLASS	= (0,0,0,0)
WHITE	= (255,255,255)
BLACK	= (1,1,1)
RED		= (255,1,1)
GREEN	= (1,255,1)
BLUE	= (1,1,255,1)
YELLOW	= (255,255,1)
MAGENTA = (255,1,255)
CYAN	= (1,255,255)

import PIL.Image

if PIL.Image.VERSION >= '1.1.7':
    # newer versions of PIL use .frombytes() instead of .fromstring()
	def image2pil(image):
		return PIL.Image.frombytes('RGBA', image.get_size(),
								   pygame.image.tostring(image, 'RGBA'))
else:
    # old version
	def image2pil(image):
		return PIL.Image.fromstring('RGBA', image.get_size(),
								    pygame.image.tostring(image, 'RGBA'))

class FrameBuffer(object):
	_instance = None

	def __new__(cls, *args, **kwargs):
		"""This ensure a single instantation.
		"""
		if cls._instance is None:
			cls._instance = super(FrameBuffer, cls).__new__(cls)
			cls._init = 1
		else:
			cls._init = 0
		return cls._instance

	def __init__(self, dpy, width, height, fullscreen,
				 bg=(128, 128, 128),
				 sync=1, syncsize=50, syncx=None,
				 syncy=None, synclevel=255,
				 mouse=0, app=None, eyefn=None,
				 fbw=None, fbh=None,
				 xscale=1.0, yscale=1.0):
		"""pygame+GL-based framebuffer class for pype.

		Wrapper for the pygame platform-independent interface to the
		framebuffer hardware. This should provide a platform
		independent handle to the video hardware, which is now
		accessed via OpenGL.  Only one instance per application.

		:param dpy: string containing name of X11 display to contact
				(None for default, taken from os.environ['DISPLAY']

		:param width, height: (pixels) size of requested display. This
				corresponds to the PHYSICAL size of the display. In full
				screen mode, it must match one of the available hardware
				modes. See [xy]scale and fb[wh] below.

		:param fullscreen: (boolean) full screen or windowed mode?

		:param bg: default background color. This can be a color
				triple (r,g,b) or a grey scale value. Actually, it can
				be anything that the C() function in this module can
				parse.

		:param sync: boolean flag indicating whether or not to setup
				(and subsequently use) a sync pulse placed on the
				monkey's video display for external synchronization
				(this is to drive photodiode that can be used to
				detect the presence or absence of the syncpulse).

		:param syncx, syncy: Position of the sync pulse generator spot
				in standard sprite coordinates - (0,0) is screen
				center, positive to left and up. *NB* this indicates
				the position for the *center* of the sync spot, so if
				you are at a corner, you should probably double the
				size to get the expected value.	 Default position
				(when syncx and syncy are not specified or are None)
				is lower right hand corner.

		:param syncsize: (pixels) size of sync pulse (sync pulse will
				be syncsize x syncsize pixels and located in the lower
				right corner of the screen (if syncsize <= 0, then
				sync pulses are disabled - same as sync=0)

		:param mouse: show mouse cursor? default is no

		:param app: (PypeApp) application handle

		:param eyefn: (optional fn that returns (x,y)) If provided should
				be a function that returns the current eye position. Flip's
				will add a mark on the framebuffer at this location (for
				debugging!)
				
		:param fb[wh]: (optional) specify the size of the internal
				framebuffer. If specified and not equal to width and
				height above, specifies the size of the virtual framebuffer
				that will be scaled onto the physical display.
		
		:param [xy]scale: (optional) alternative (older) method for
				specifying size of framebuffer. The internal framebuffer
				will be set to be (width*xscale, height*yscale). fb[wh]
				overrides this parameter.
		
		:return: nothing

		"""

		if not FrameBuffer._init: return

		self.app = app					# store for joybut access..
		self.eyefn = eyefn

		self.record = 0
		self._keystack = []
		self._font = None
		
		if fbw:
			xscale = fbw / float(width)
		if fbh:
			yscale = fbh / float(height)
		self.xscale = xscale
		self.yscale = yscale
		self.gamma = (1.0, 1.0, 1.0)
		if not width or not height:
			Logger('sprite: must specify display width and height\n')
		else:
			self.physicalw = width
			self.physicalh = height
			self.w = int(0.5 + width * self.xscale)
			self.h = int(0.5 + height * self.yscale)
			self.hw = self.w / 2
			self.hh = self.h / 2

		# Mon Oct 30 15:16:46 2017 mazer
		# note: `self.flags = self.flags | NOFRAME` breaks things on osx!
		self.flags = OPENGL | DOUBLEBUF
		if fullscreen:
			self.flags = self.flags | HWSURFACE | FULLSCREEN
		else:
			if sys.platform.startswith('linux'):
				self.flags = self.flags | NOFRAME

		if sys.platform.startswith('linux'):
			os.environ['__GL_SYNC_TO_VBLANK'] = '1' # nvidia specific!

		if dpy:
			self.gui_dpy = os.environ['DISPLAY']
			self.fb_dpy = dpy

		# change DISPLAY transiently to allow separate servers for
		# the stimulus display and the gui
		try:
			os.environ['DISPLAY'] = self.fb_dpy
			pygame.init()
		finally:
			os.environ['DISPLAY'] = self.gui_dpy

		# position display window at upper right corner based on screen size
		modes = pygame.display.list_modes()
		if not (self.physicalw, self.physicalh) in modes:
			Logger('sprite: warning %dx%d not an avialable resolution\n' %
				   (self.physicalw, self.physicalh))
		if fullscreen:
			Logger('sprite: available modes are %s\n' % \
				   pygame.display.list_modes())
		else:
			# anchor non-fullscreen window in upper right corner of screen
			(dpyw, dpyh) = pygame.display.list_modes()[0]
			os.environ['SDL_VIDEO_WINDOW_POS'] = '%d,%d' % \
												 (dpyw - self.physicalw, 0,)

		try:
			if pygame.display.mode_ok((self.physicalw, self.physicalh),
									  self.flags) == 0:
				Logger('sprite: mode %dx%d:%s not available.\n' %
					   (self.physicalw, self.physicalh, ppflag(self.flags)))
				Logger('sprite: available modes are %s\n' % modes)
				sys.exit(1)
		except pygame.error:
			Logger('FrameBuffer: check X server status!');
			sys.exit(1)

		Logger("sprite: physical=%dx%d" % (self.physicalw, self.physicalh))
		Logger("sprite: framebuffer=%dx%d" % (self.w, self.h))

		# in theory, it works to open and close the pygame display
		# on the fly to hide the graphics window..
		self.screen_open(init=1)
		Logger('sprite: display is %dx%d %s\n' % \
			   (self.physicalw, self.physicalh, ppflag(self.flags)))
		Logger('sprite: fb is %dx%d %s\n' % \
			   (self.w, self.h, ppflag(self.flags)))

		self.bg = bg

		# disable the sync pulse in config with 'SYNCSIZE: -1'
		self.sync_mode = not (syncsize <= 0 or (not sync))
		if self.sync_mode:
			# If sync pulse location is not specified, then put it in
			# the lower right corner:
			if syncx is None:
				syncx = int(round(self.w/2))
			if syncy is None:
				syncy = int(round(-self.h/2))

			# if sync position is [-1,+1] -- consider it as normalized
			# position relative to the screen geometry (-1,-1) is lower
			# left corner..
			if abs(syncx) <= 1:
				syncx = syncx * int(round(self.w/2))
			if abs(syncy) <= 1:
				syncy = syncy * int(round(self.h/2))
			
			# pre-build sync/photodiode driving sprites:
			self._sync_low = Sprite(syncsize, syncsize, syncx, syncy,
									name='sync_low', on=1, fb=self)
			self._sync_low.fill((1, 1, 1))
			self._sync_low.render()

			self._sync_high = Sprite(syncsize, syncsize, syncx, syncy,
									 name='sync_high', on=1, fb=self)
			self._sync_high.fill((synclevel, synclevel, synclevel))
			self._sync_high.render()

			self.syncinfo = (syncx, syncy, syncsize)
			# initial sync state is OFF
			self.sync(0)
		else:
			self._sync_low = None
			self._sync_high = None
			self.syncinfo = None

		# Timer initialized and used by flip() method for
		# checking for frame rate glitches. To enage the
		# timer check, set maxfliptime to some positive value
		# min ms in your task:
		self.maxfliptime = 0
		self.fliptimer = None

		self.cursor(mouse)
		pygame.event.set_grab(0)

		# From here on out, use 'fullscreen' to track full screen mode
		self.fullscreen =  self.flags & FULLSCREEN

	def screen_open(self, init=0):
		self.screen = pygame.display.set_mode((self.physicalw, self.physicalh),
											  self.flags)
		pygame.display.set_caption('framebuf')

		if init:
			# initialize OpenGL subsystem
			ogl.glOrtho(0.0, self.physicalw, 0.0, self.physicalh, 0.0, 1.0)
			ogl.glScale(1. / self.xscale, 1. / self.yscale, 1.0)
			# in theory -- can put any static, global transformations you
			# want here -- say to invert the stimuli or scale it, eg:
			#	 ogl.glScale(0.5, 0.5, 1.0)
			# or
			#	 ogl.glOrtho(-self.w, 2*self.w, -self.h, 2*self.h, 0.0, 1.0)
			ogl.glEnable(ogl.GL_LINE_SMOOTH)
			ogl.glEnable(ogl.GL_BLEND)
			ogl.glBlendFunc(ogl.GL_SRC_ALPHA, ogl.GL_ONE_MINUS_SRC_ALPHA)
			ogl.glEnable(ogl.GL_TEXTURE_2D)
			ogl.glEnable(ogl.GL_COLOR_MATERIAL)
			bpp = pygame.display.gl_get_attribute(GL_DEPTH_SIZE)

	def screen_close(self):
		# hide screen by making it tiny (homebrew iconify)
		self.screen = pygame.display.set_mode((1,1), self.flags)

	def __del__(self):
		"""FrameBuffer cleanup.

		Delete held sprites and shut down pygame subsystem.
		"""
		try:
			del self._sync_low
			del self._sync_high
		except AttributeError:
			pass
		if pygame:
			pygame.display.quit()

	def calcfps(self, duration=250):
		"""Estimate frames per second.

		Try to determine the approximate frame rate automatically.
		X11R6 doesn't provide a way to set or query the current video
		frame rate. To circumvent this, we just flip the page a few
		times and compute the median inter-frame interval.

		*NB* This is always going to be a rought estimate, you
		should always adjust the /etc/X11/XFConfig-4 file to set the
		exact frame rate and keep track of in with your data.

		:param duration: period of time to flip/test (in ms)

		:return: float, current frame rate in Hz.

		"""
		# try to estimate current frame rate
		oldsync = self.sync_mode
		self.sync_mode = 0
		self.clear((1,1,1))
		self.flip()
		self.clear((2,2,2))
		self.flip()

		# page flip for up to a second..
		intervals = []
		self.flip()
		start = time.time()
		a = start
		while time.time()-start <= 1:
			self.flip()
			b = time.time()
			intervals.append(1000*(b-a))
			a = b

		self.sync_mode = oldsync

		if len(intervals) <= 1:
			Logger('sprite: failed to estimate frames per second, using 60Hz\n')
			return 60

		# compute estimated frame rate (Hz) based on median inter-frame
		# interval
		# this is ROUGH median - if len(intervals) is odd, then it's
		# not quite right, but it should be close enough..
		sd = np.std(intervals)
		m = np.mean(intervals)
		k = []
		for i in intervals:
			if sd == 0 or abs(i-m) < (2*sd):
				k.append(i)
		if len(k) < 1:
			Logger('sprite: calcfps - no photodiode? Assuming 60\n')
			return 60
		km = np.mean(k)
		if km > 0.0:
			return round(1000.0 / km)
		else:
			return -1.0

	def set_gamma(self, r, g=None, b=None):
		"""Set hardware gamma correction values (if possible).

		Set hardware display gammas using pygame/SDL gamma function.
		Not all hardware supports hardware gamma correction, so this
		may not always work.

		:param r: (Float) if this is the only argument supplied, then this is
				the simply luminance gamma value and all three guns
				are set to this value.

		:param g,b: (Float) green and blue gamma values. If you specify g,
				you'ld better specify b as well. Arguments are
				floating point numbers (1.0 is no gamma correction at
				all).

		:return: TRUE on success (ie., if the hardware supports gamma
				correction)

		"""
		if g is None: g = r
		if b is None: b = r
		self.gamma = (r,g,b)
		return pygame.display.set_gamma(r, g, b)

	def cursor(self, on=0):
		"""Turn display of the mouse cursor on or off.

		:param on: boolean; 1 to turn the cursor on, 0 to turn it off

		:return: nothing

		"""
		pygame.mouse.set_visible(on);

	def cursorpos(self):
		return pygame.mouse.get_pos()

	def togglefs(self, wait=0):
		pygame.event.clear()
		pygame.display.toggle_fullscreen()
		while 1:
			# wait for an expose event to indicate the switch has
			# completed (resync/redraw/etc)
			e = pygame.event.poll()
			if e.type == pygame.VIDEOEXPOSE:
				break

		self.fullscreen = not self.fullscreen

		if wait and self.fullscreen:
			self.clear()
			self.string(0, 0, '[hit key/button to clear]', (255,255,255))
			self.flip()
			while len(self.checkkeys()) == 0:
				if self.app and self.app.joybut(0):
					break
			self.clear()
			self.flip()
			pygame.event.clear()

	def sync(self, state, flip=None):
		"""Draw/set sync pulse sprite.

		Set the status of the sync pulse.

		:param state: (boolean) 1=light, 0=dark

		:param flip: (boolean) do a page flip afterwards?

		:return: nothing

		"""
		self._sync_state = state
		if flip:
			self.flip()

	def sync_toggle(self, flip=None):
		"""Toggle sync pulse state.

		Toggle the status of the sync pulse. Light->dark; dark->light.

		:param flip: (boolean) do a page flip afterwards?

		:return: nothing

		"""
		self.sync(not self._sync_state, flip=flip)

	def clear(self, color=None, flip=None):
		"""Clear framebuffer.

		Clear framebuffer to specified color (or default background
		color, if no color is specfied).

		:param color: color to fill with (scalar pixel value for solid
				grey; triple scalars for an rgb value - anything C()
				in this module understands is ok). If no color is
				specified, then self.bg is used (set in the __init__
				method).

		:param flip: (boolean) do a page flip afterwards?

		:return: nothing

		"""
		if color is None:
			color = self.bg

		ogl.glPushMatrix()
		ogl.glPushAttrib(ogl.GL_COLOR_BUFFER_BIT)

		apply(ogl.glClearColor, C(color, gl=1))
		ogl.glClear(ogl.GL_COLOR_BUFFER_BIT)

		ogl.glPopAttrib(ogl.GL_COLOR_BUFFER_BIT)
		ogl.glPopMatrix()

		if flip:
			self.flip()

	def flip(self, doflip=1):
		"""Flip framebuffer (sync'd to vert-retrace, if possible).

		Draw the syncpulse sprite (if enabled) with the appropriate
		polarity, blit to the screen and then perform a page flip.

		In general, this method should block until the flip occurs,
		however, not all video hardware until linux supports blocking
		on page flips. So be careful and check your hardware. You
		should be able to use the calcfps() method to get a rough
		idea of the framerate, if it's very fast (>100 Hz), chances
		are that the hardware doesn't support blocking on flips.

		"""
		if self.sync_mode:
			if self._sync_state == 1:
				self._sync_high.blit()
			elif self._sync_state == 0:
				self._sync_low.blit()

		if not doflip:
			# this is in case you just want to update the sync pulse
			# but not actually do the flip (ie, if you're using the
			# MpegMovie object, or something similar, that writes
			# directly to the frame buffer and does it's own flip..)
			return

		if self.eyefn:
			(x, y) = self.eyefn()
			self.rectangle(x, y, 3, 3, (255, 1, 1, 128))

		# make sure all stimuli are written to the surface.
		ogl.glFinish()

		if not self.screen is None:
			pygame.display.flip()
			if self.app:
				self.app.encode(MARKFLIP)

		if self.fliptimer is None:
			self.fliptimer = time.time()
		else:
			t = time.time()
			if self.maxfliptime:
				elapsed = t - self.fliptimer
				if elapsed > self.maxfliptime:
					Logger('warning: %dms flip\n' % elapsed)
			self.fliptimer = t

		if self.record:
			from pype import PypeApp
			recno = PypeApp().record_id
			fname = PypeApp().record_file
			if fname is None:
				return
			if fname.startswith('/dev/null'):
				fname = 'null'
			ms = int(round(1000.0*(time.time())))
			f = '%s_%04d_%020d.jpg' % (fname, recno, ms)
			self.snapshot(f)
			PypeApp().encode('SNAPSHOT ' + f)

	def recordtog(self, state=None):
		if state is None:
			self.record = not self.record
		else:
			self.record = state
		if self.record:
			os.system('/bin/rm -f /tmp/pype*.jpg')
			sys.stderr.write('[Recording is ON]\n')
		else:
			sys.stderr.write('[Recording is OFF]\n')

	def checklshift(self):
		"""LEFT Shift key down?"""
		pygame.event.pump()
		return KMOD_LSHIFT & pygame.key.get_mods()

	def checkrshift(self):
		"""RIGHT Shift key down?"""
		pygame.event.pump()
		return KMOD_RSHIFT & pygame.key.get_mods()

	def checklctrl(self):
		"""LEFT Ctrl key down?"""
		pygame.event.pump()
		return KMOD_LCTRL & pygame.key.get_mods()

	def checkrctrl(self):
		"""RIGHT Ctrl key down?"""
		pygame.event.pump()
		return KMOD_RCTL & pygame.key.get_mods()

	def waitkeys(self):
		"""Wait for keyboard to be clear (no pressed keys)."""
		while len(self.checkkeys()) > 0:
			pass

	def checkkeys(self):
		"""Get list of pressed keys."""
		pygame.event.pump()
		return map(pygame.key.name, np.where(pygame.key.get_pressed())[0])

	def checkmouse(self):
		"""Get list of pressed mouse buttons."""
		pygame.event.pump()
		return pygame.mouse.get_pressed()

	def clearkey(self):
		"""Clear keyboard input queue.

		Clear the keyboard buffer. The way things are currently setup
		any keystrokes coming into pype are pushed into a queue, the
		getkey() method below returns the next key in the queue

		"""
		while 1:
			if len(pygame.event.get()) == 0:
				return

	def mouseposition(self):
		"""Query mouse position.

		Returns (x,y) coords of mouse in frame buffer coordinates.
		
		"""
		pygame.event.pump()
		pos = pygame.mouse.get_pos()
		return (pos[0] - self.hw, -pos[1] + self.hh)
	
	def getkey(self, wait=None, down=1):
		"""Get next keystroke from queue.

		Return the next key in the keyboard input queue and pop
		the keystroke off the queue stack.

		:param wait: flag indicating whether or not to wait for a
				keystroke to occur.

		:param down: (boolean) boolean flag indicating whether to only
				accept downstrokes (default is true)

		:return: keystroke value; negative for key-up, positive for
				key-down, 0 if no keystrokes are available in the
				queue.

		"""
		c = 0
		if pygame.display.get_init():
			if len(self._keystack) > 0:
				c = self._keystack[0]
				self._keystack = self._keystack[1:]
			else:
				while not c:
					if not down:
						events = pygame.event.get([KEYUP,KEYDOWN])
					else:
						events = pygame.event.get([KEYDOWN])
					if len(events) > 0:
						if events[0] == KEYUP:
							c =	 -(events[0].key)
						else:
							c = events[0].key
					elif not wait:
						break
		return c

	def ungetkey(self, c):
		"""'unget' keystroke.

		Push a keystroke event back onto the keyboard queue. Keyboard queue
		is simulated in pype as a stack, see getkey() method for details.

		:param c: keystroke to push back (same syntax as getkey() method above.

		"""
		self._keystack.append(c)

	def snapshot(self, filename, size=None):
		"""Save screen snapshot to file.

		Take snapshot of the framebuffer and write it to the specified
		file.

		:param filename: name of output file; PIL is used to write the
				file and PIL automatically determines the filetype
				from filename's extension.

		:param size: optional size of the snapshot; PIL is used to
				rescale the image to this size. If size is left
				unspecified, then the snapshot is written at the
				screen's true resolution.

		:return: PIL Image structure containing the snapshot (can be
				converted th PhotoImage for display in
				Tkinter/Canvas..)

		"""
		pil = image2pil(self.screen)
		if filename:
			if size:
				pil.resize(size).save(filename)
				Logger("Wrote %s screen to: %s\n" % (size,filename))
			else:
				pil.save(filename)
				Logger("Wrote screen to: %s\n" % filename)
		return pil

	def string(self, x, y, s, color, flip=None, bg=None, size=30, rotation=0.0):
		"""Draw string on framebuffer.

		Write text string in default font on the framebuffer screen
		at the specified location. This is primarily useful for running
		psychophysical studies and debugging.

		*NB* Requires the SDL_ttf package

		:param x, y: coordinates of string *CENTER*

		:param s: string to write

		:param color: RGB or greyscale color (anything C() understands)

		:param flip: (boolean) flip after write

		:param bg: None or C()-compatible color spec

		:param size: (pixels) font size

		:return: nothing

		"""
		color = C(color)
		if self._font is None:
			pygame.font.init()
			self._font = {}

		# Try to use a cached copy of font if it's already been
		# loaded, otherwise load it and cache it. So, this can
		# be slow the first time it's called
		try:
			font = self._font[size]
		except KeyError:
			try:
				from pype import pypelib
				fontfile = pypelib('cour.ttf')
				self._font[size] = pygame.font.Font(fontfile, size)
			except ImportError:
				self._font[size] = pygame.font.Font(None, size)

		s = self._font[size].render(s, 0, color)
		if not bg is None:
			self.rectangle(x, y, s.get_width()*1.1, s.get_height*1.1,
						   bg, width=0)

		tex = _texture_create(pygame.image.tostring(s, 'RGBA', 1),
							  s.get_width(), s.get_height())
		_texture_blit(self, tex, x, y, rotation=rotation)
		_texture_del(tex)

		if flip:
			self.flip()

	def rectangle(self, cx, cy, w, h, color, width=0, flip=None):
		"""Draw rectangle directly on framebuffer.

		:param cx, cy: world coords of the rectangle's *CENTER*

		:param w, h: (pixels) width and height of the rectangle

		:param color: C() legal color specification

		:param width: 0 means fill the rectangle with the specfied
				color, anything else means draw the outline of the
				rectangle in the specified color with strokes of the
				specified width.

		:return: nothing

		"""

		cx = cx - (w/2)
		cy = cy - (h/2)
		oc = ((cx, cy), (cx+w, cy), (cx+w, cy+h), (cx, cy+h))
		self.lines([(cx, cy), (cx+w, cy), (cx+w, cy+h), (cx, cy+h)],
				   width=width, color=color, flip=flip, closed=1)

	def lines(self, pts, color, width=1, contig=1, closed=0, joins=0, flip=None):
		"""Draw line directly on framebuffer.

		Use pygame primitive to draw a straight line on the framebuffer

		:param pts: [(x,y)...] world coords of polyline points

		:param color: any color acceptable to C()

		:param width: (pixels) width of line (0 for filled polygon)

		:param contig: (bool) if true (default), contiguous sequence
				of lines. Otherwise, each pair of points as
				interpreted as single broken line.

		:param closed: (bool) closed polygon?

		:param joins: (in) fake joins with circles? (circle r ~ joins*width)

		:param flip: (boolean) flip after write

		:return: nothing

		"""
		ogl.glPushMatrix()
		ogl.glPushAttrib(ogl.GL_CURRENT_BIT)
		if width == 0:
			ogl.glBegin(ogl.GL_POLYGON)
		else:
			ogl.glLineWidth(width)
			if closed:
				ogl.glBegin(ogl.GL_LINE_LOOP)
			elif contig:
				ogl.glBegin(ogl.GL_LINE_STRIP)
			else:
				ogl.glBegin(ogl.GL_LINES)
		apply(ogl.glColor4f, C(color, gl=1))
		for (x, y) in pts:
			x = x + self.hw
			y = y + self.hh
			ogl.glVertex(x, y)
		ogl.glEnd()
		ogl.glPopAttrib(ogl.GL_CURRENT_BIT)
		ogl.glPopMatrix()

		if joins > 0:
			for (x,y) in pts:
				self.circle(x, y, joins*(width/2), color)

		if flip: self.flip()

	def line(self, start, stop, color, width=1, flip=None):
		"""Draw line directly on framebuffer.

		Use pygame primitive to draw a straight line on the framebuffer

		:param start: (x,y) world coords of line's starting point

		:param stop: (x,y) world coords of line's ending point

		:param color: any color acceptable to C()

		:param width: (pixels) width of line

		:param flip: (boolean) flip after write

		:return: nothing

		"""
		self.lines([start, stop], color, width=width, flip=flip)
		if flip: self.flip()

	def circle(self, cx, cy, r, color, width=0, flip=None):
		"""Draw circle directly on framebuffer.

		*NB* Tue Apr 25 10:14:33 2006 mazer - GL coords are
		different!!! circles were flipped/mirrored around the x-axis
		in GL-mode!!!!

		:param cx, cy: center coords of the circle

		:param r: (pixels) radius

		:param color: anything C() understands

		:param width: (pixels) width of circle. If width==0, then the
				circle gets filled instead of just drawing an outline

		:return: nothing

		"""

		t = np.linspace(0, 2*np.pi, num=100, endpoint=False)
		x = r * np.cos(t) + cx
		y = r * np.sin(t) + cy
		self.lines(zip(x,y), color, width=width, closed=1, flip=flip)

def genaxes(w, h, rw, rh, typecode=np.float64, inverty=0):
	"""Generate two arrays descripting sprite x- and y-coordinate axes
	(like Matlab MESHGRID).

	*NB* By default the coordinate system is matrix/matlab, which
	means that negative values are at the top of the sprite and
	increase going down the screen. This is fine if all you use the
	function for is to compute eccentricity to shaping envelopes, but
	wrong for most math. Use inverty=1 to get proper world coords..

	:param w, h: scalar values indicating the display width and
		height of the sprite in needing axes in pixels

	:param rw, rh: scalar values indicating the "real" width and
		height of the sprite (specifies actually array size)

	:param typecode: numpy-style typecode for the output array

	:param inverty: (boolean) if true, then axes are matlab-style with
		0th row at the top, y increasing in the downward direction

	:return: pair of vectors (xaxis, yaxis) where the dimensions of
		each vector are (w, 1) and (1, h) respectively.

	Mon Mar	 3 13:24:10 2014 mazer
	NOTE: there was a small fencpost error here (I think) -- linspace
	is right, arange is likely wrong:
	>> x = np.arange(0, w) - ((w - 1) / 2.0)
	>> y = np.arange(0, h) - ((h - 1) / 2.0)

	"""
	if h is None:
		(w, h) = w						# size supplied as pair/tuple
	x = np.linspace(-w/2.0, w/2.0, rw)
	y = np.linspace(-h/2.0, h/2.0, rh)
	if inverty:
		y = y[::-1]
	return x.astype(typecode)[:,np.newaxis],y.astype(typecode)[np.newaxis,:]

class ScaledSprite(object):
	_id = 0								  # unique id for each sprite

	def __init__(self, width=None, height=None, rwidth=None, rheight=None,
				 x=0, y=0, depth=0, dx=0, dy=0,
				 fname=None, name=None, fb=None, on=1, image=None,
				 icolor='black', ifill='yellow',
				 centerorigin=0, rotation=0.0, contrast=1.0):
		"""ScaledSprite Object -- pype's main tool for graphics generation.

		This is a basic sprite object. The improvement here is that the
		sprite has both a real size (rwidth x rheight) and a display size
		(dwidth x dheight). If these match, it's a standard
		Sprite object. If they don't match, the coordinate system for sprite
		makes it look like it's display size, so gratings etc are computed
		properly. But only rwidth x rheight pixels are kepts around, so
		you can use coarse sprites plus OpenGL scaling to get more speed.

		The standard Sprite class is now a subclass of ScaledSprite with
		rwidth==dwidth and rheight==dheight..

		:param width, height: (int) sprite size on display in pixels -- this
				is the physical size once the sprite gets drawn on the display

		:param rwidth, rheight: (int/float) virtual sprite size -- this is the one
				that actual computations get done on, so smaller is faster!
				Ff these are <1.0, then they're assumed to be x and y-scaling
				factors and applied to width and height

		:param x, y: (int) sprite position in pixels

		:param depth: (int; default 0) depth order for DisplayList (0=top)

		:param fb: (FrameBuffer object) associated FrameBuffer object

		:param on: (boolean) on/off (for DisplayList)

		:param image: (Sprite object) seed sprite to get data from

		:param dx, dy: (int) xy velocity (shift/blit)

		:param fname: (string) Filename of image to load sprite data from.

		:param name: (string) Sprite name/info

		:param icolor: (string) icon outline (for UserDisplay)
		
		:param ifill: (string) icon fille (for UserDisplay)

		:param centerorigin: (boolean; default=0) If 0, then the upper
				left corner of the sprite is 0,0 and increasing y goes
				DOWN, increase x goes RIGHT. If 1, then 0,0 is in the
				center of the sprite and increasing y goes UP and
				increase X goes RIGHT.

		:param rotation: (float degrees) GL-pipeline rotation
				factor. Very fast pre-blit rotation.

		:param contrast: (float 0-1.0) GL-pipeline contrast scaling
				factor. Very fast pre-blit scaling of all pixel
				values.

		"""

		self.x = x
		self.y = y
		self.dx = dx
		self.dy = dy
		self.depth = depth
		self.fb = fb
		self._on = on
		self.icolor = icolor
		self.ifill = ifill
		self.centerorigin = centerorigin
		self.rotation = rotation
		self.contrast = contrast
		self.texture = None

		# for backward compatibilty
		dwidth, dheight = width, height

		# if only height is provided, assume square
		if dheight is None:		dheight = dwidth
		if rheight is None:		rheight = rwidth

		# if only display size is specified, make real same (no scaling)
		if dwidth and not rwidth:
			rwidth, rheight = dwidth, dheight
			
		# if only real size is specified, make display same (again, no scaling)
		if rwidth and not dwidth:
			dwidth, dheight = rwidth, rheight

		if not image and not fname and rwidth < 1.0:
			rwidth = int(round(dwidth * rwidth))
		if not image and not fname and rheight < 1.0:
			rheight = int(round(dheight * rheight))
			
		if rwidth > dwidth:
			rwidth = dwidth
		if rheight > dheight:
			rheight = dheight
			
		if fname:
			# load image data from file; if a real size is specififed,
			# resize image to the specified real size. display size
			# can be use to scale it back up...
			self.im = pygame.image.load(fname).convert(32, pygame.SRCALPHA)
			if rwidth:
				# if virtual size is specified, image is downscaled to
				# the virtual size for speed
				self.im = pygame.transform.scale(self.im, (rwidth, rheight))
			self.userdict = {}
			setalpha = 0
		elif image:
			import copy
			# make a copy of the source sprite/image; like image data,
			# if a real size is specified, resize image to the
			# specified real size. display size can be use to scale it
			# back up...
			try:
				# pype Image object
				self.im = image.im.convert(32, pygame.SRCALPHA)
				self.userdict = copy.copy(image.userdict)
			except:
				# pygame image/surface
				self.im = image.convert(32, pygame.SRCALPHA)
				self.userdict = {}
			if rwidth:
				self.im = pygame.transform.scale(self.im, (rwidth, rheight))
			setalpha = 0
		else:
			# new image from scratch of specified real size
			self.im = pygame.Surface((rwidth, rheight), \
									 flags=pygame.SRCALPHA, depth=32)
			self.userdict = {}
			setalpha = 1

		if rwidth is None:
			rwidth = self.im.get_width()
			rheight = self.im.get_height()
		if dheight is None:
			dwidth = rwidth
			dheight = rheight

		self.xscale = float(dwidth) / float(rwidth)
		self.yscale = float(dheight) / float(rheight)

		self.im.set_colorkey((0,0,0,0))

		# make sure every sprite gets a name for debugging
		# purposes..
		if name:
			self.name = name
		elif fname:
			self.name = "file:%s" % fname
		else:
			self.name = "#%d" % Sprite._id

		# do not mess with _id!!!
		self._id = Sprite._id
		Sprite._id = Sprite._id + 1

		self.refresh()
		
		# this is to fix a Lucid problem, not tracked down now..
		if setalpha:
			self.alpha[::] = 255

	def refresh(self):
		# this should be called each time the size or surface
		# data for a sprite gets changed

		self.w = self.im.get_width()
		self.h = self.im.get_height()
		self.dw = int(round(self.xscale * self.w))
		self.dh = int(round(self.yscale * self.h))
		
		self.ax, self.ay = genaxes(self.dw, self.dh, self.w, self.h,
								   inverty=0)
		self.xx, self.yy = genaxes(self.dw, self.dh, self.w, self.h,
								   inverty=1)
		self.array = pygame.surfarray.pixels3d(self.im)
		self.alpha = pygame.surfarray.pixels_alpha(self.im)
		self.im.set_colorkey((0,0,0,0))

	def __del__(self):
		"""Sprite clean up.

		Remove the name of the sprite from the global
		list of sprites to facilitate detection of un-garbage
		collected sprites

		"""
		self.render(clear=1)

	def __repr__(self):
		return ('<ScaledSprite "%s"@(%d,%d) V%dx%d D%dx%d depth=%d on=%d>' %
				(self.name, self.x, self.y,
				 self.w, self.h, self.dw, self.dh, self.depth, self._on,))

	def XY(self, xy):
		"""Correct for centerorigin flag"""
		return (self.X(xy[0]), self.Y(xy[1]))

	def X(self, x):
		"""Correct for centerorigin flag"""
		if self.centerorigin:
			return (self.w / 2) + x
		else:
			return x

	def Y(self, y):
		"""Correct for centerorigin flag"""
		if self.centerorigin:
			return (self.h / 2) - y
		else:
			return y
	

	def set_rotation(self, deg):
		"""
		Sets GL-pipeline rotation term (FAST!)

		"""
		self.rotation = deg

	def set_contrast(self, percent):
		"""
		Sets GL-pipeline rotation term (FAST!)

		"""
		self.contrast = percent / 100.0

	def asPhotoImage(self, alpha=None, xscale=None, yscale=None):
		"""Convert sprite to a Tkinter displayable PhotoImage.

		This depends on the python imaging library (PIL)

		:param alpha: (optional) alpha value for the PhotoImage

		:param xscale,yscale: (optional) x and y scale factor for
				resizing image. If you specify one, you must specify
				both!

		:return: PhotoImage represenation of the sprite's pixels.

		"""

		import PIL.ImageTk, PIL.ImageFilter
		
		pil = self.asImage(xscale=xscale, yscale=yscale)
		pil = pil.resize((self.dw, self.dh))
		pil = pil.rotate(self.rotation, expand=1)
		if not alpha is None:
			pil.putalpha(alpha)
		self.pim = PIL.ImageTk.PhotoImage(pil)

		# NOTE: hanging pim off sprite prevents garbage collection
		return self.pim

	def asImage(self, xscale=None, yscale=None):
		"""Convert sprite to a PIL Image.

		This depends on the python imaging library (PIL)

		:param xscale,yscale: (optional) x and y scale factor for
				resizing image. If you specify one, you must specify
				both!

		:return: Image represenation of the sprite's pixels.

		"""

		pil = image2pil(self.im)
		pil = pil.resize((self.dw, self.dh))
		if xscale or yscale:
			(w, h) = pil.size
			pil = pil.resize((int(round(w*xscale)), int(round(h*yscale))))
		pil = pil.rotate(self.rotation, expand=1)
		return pil

	def set_alpha(self, a):
		"""Set global alpha value.

		Set transparency of the *entire* sprite to this value.

		:param a: alpha value (0-255; 0 is fully transparent, 255 is
				fully opaque).

		:return: nothing
		"""
		self.alpha[::] = a

	def line(self, x1, y1, x2, y2, color, width=1):
		"""Draw line of specified color in sprite.

		*NB* not the same syntax as the FrameBuffer.line() method!!

		:param x1,y1: starting coords of line in world coords

		:param x2,y2: ending coords of line in world coords

		:param color: line color in C() parseable format

		:param width: (pixels) line width

		:return: nothing

		"""
		start = (self.X(x1),self.Y(y1))
		stop = (self.X(x2),self.Y(y2))
		pygame.draw.line(self.im, C(color), start, stop, width)

	def fill(self, color):
		"""Fill sprite with specficied color.

		Like clear method above, but requires color to be specified

		:param color: C() parseable color specification

		:return: nothing

		"""
		color = C(color)
		for n in range(3): self.array[:,:,n] = color[n]
		self.alpha[::] = color[3]

	def clear(self, color=(1,1,1)):
		"""Clear sprite to specified color.

		Set's all pixels in the sprite to the indicated color, or black
		if no color is specified.

		:param color: C() parseable color specification

		:return: nothing

		"""
		self.fill(color)

	def noise(self, thresh=0.5):
		"""Fill sprite with white noise.

		Fill sprite with binary white noise. Threshold can be used
		to specified the DC level of the noise.

		:param thresh: threshold value [0-1] for binarizing the noise
				signal. Default's to 0.5 (half black/half white)

		:return: nothing

		"""
		for n in range(3):
			if n == 0:
				m = np.random.uniform(1, 255, size=(self.w, self.h))
				if thresh:
					m = np.where(np.greater(m, thresh*255),
								 255, 1).astype(np.uint8)
			self.array[:,:,n] = m[::].astype(np.uint8)
		# for some reason starting with lucid (10.04LTS) you need
		# to explicitly set alpha here. This means you need to make
		# sure to apply alpha masks AFTER you do a noise fill!
		self.alpha[::] = 255

	def circlefill(self, color, r=None, x=0, y=0, width=0):
		"""Draw filled circle in sprite.

		Only pixels inside the circle are affected.

		:param color: C() parseable color spec

		:param r: (pixels) circle radius

		:param x, y: circle center position in world coords (defaults to 0,0)

		:param width: (pixels) pen width; if 0, then draw a filled circle

		:return: nothing

		"""
		if r is None:	r = self.w / 2
		x = self.X(x)
		y = self.Y(y)

		color = C(color)
		h = np.hypot(self.xx-x, self.yy-y)
		if width == 0:
			for n in range(3):
				self.array[np.less_equal(h, r),n] = color[n]
			self.alpha[np.less_equal(h, r)] = color[3]
		else:
			for n in range(3):
				self.array[np.less_equal(abs(h-r), width)] = color[n]
			self.alpha[np.less_equal(abs(h-r), width)] = color[3]


	def circle(self, color, r=None, x=0, y=0):
		"""Draw circlular mask into sprite.

		Pixels inside the circle are filled, rest of the sprite
		is make 100% transparent.

		:param color: C() parseable color spec

		:param r: radius of circular mask

		:param x, y: (pixels) center coords of circular mask (world
				coordinates)

		:return: nothing

		"""
		self.fill((0,0,0,0))
		self.circlefill(color, r=r, x=x, y=y)

	def rect(self, x, y, w, h, color):
		"""Draw a *filled* rectangle of the specifed color on a sprite.

		*NB*
		- parameter sequence is not the same order as circlefill()

		:param x, y: world coords for rectangle's center

		:param w, h: (pixels) width and height of rectangle

		:param color: C() parseable color spec

		:return: nothing

		"""
		color = C(color)
		x = self.w/2 + x - w/2
		y = self.h/2 - y - h/2
		mx = max(0,x)
		my = max(0,y)

		for n in range(3): self.array[mx:(x+w),my:(y+h),n] = color[n]
		self.alpha[mx:(x+w),my:(y+h)] = color[3]

	def rotateCCW(self, angle, preserve_size=1):
		self.rotate(-angle, preserve_size=preserve_size)

	def rotateCW(self, angle, preserve_size=1):
		self.rotate(angle, preserve_size=preserve_size)

	def rotate(self, angle, preserve_size=1):
		"""Lossy rotation of spite image data

		Rotate sprite image about the sprite's center.
		Uses pygame.transform primitives.

		- this is NOT invertable! Multiple rotations will accumulate
		  errors, so keep an original and only rotate copies. Ideal
		  only rotate things once!

		- 03/07/2006: note rotation direction is CW!!

		:param angle: angle of rotation in degrees

		:param preserve_size: (boolean) if true, the rotated sprite is
				clipped back down to the size of the original image.

		:return: nothing

		"""
		if self.xscale != 1.0 or self.yscale != 1.0:
			Logger("rotate only works for unscaled sprites!\n")
			
		new = pygame.transform.rotate(self.im, -angle)
		if preserve_size:
			w = new.get_width()
			h = new.get_height()
			x = (w/2) - (self.w/2)
			y = (h/2) - (self.h/2)
			new = new.subsurface(x, y, self.w, self.h)
		self.im = new
		self.refresh()
		
		
	def scale(self, new_width, new_height):
		"""Resize this sprite (fast).

		Resize a sprite using pygame/rotozoom to a new size. Can
		scale up or down equally well. Changes the data within
		the sprite, so it's not really invertable. If you want
		to save the original image data, first clone() and then
		scale().

		*NB* NOT invertable! Scaling down and unscaling will *not*
		restore the original sprite!!

		:param new_width: (pixels) new width

		:param new_height: (pixels) new height

		:return: nothing

		Warning: in general, this is obsolete -- you should use
		xscale/yscale to do scaling through the GL pipeline

		"""

		nw = int(round(self.w * new_width / float(self.dw)))
		nh = int(round(self.h * new_height / float(self.dh)))
		self.im = pygame.transform.scale(self.im, (nw, nh))
		self.refresh()
		

	def circmask(self, x, y, r):
		"""hard vignette in place - was image_circmask"""
		mask = np.where(np.less(np.hypot(self.ax-x,self.ay+y), r), 1, 0)
		a = pygame.surfarray.pixels2d(self.im)
		a[::] = mask * a

	def alpha_aperture(self, r, x=0, y=0):
		"""Add hard-edged aperture (vignette)

		Vignette the sprite using a hard, circular aperture into the
		alpha channel. This draws a hard circular mask of the
		specified radius, at the specified offset ([0,0] is center)
		into the sprite's alpha channel, so when it's blitted the
		region outside the aperture is masked out.

		:param r: (pixels) radius

		:param x,y: (pixels) optional aperture center (0,0 is center)

		:return: nothing

		"""
		d = np.where(np.less(np.hypot(self.ax-x, self.ay+y), r),
					 255, 0).astype(np.uint8)
		self.alpha[::] = d

	def alpha_gradient(self, r1, r2, x=0, y=0):
		"""Add soft-edged apperature (gradient vignette)

		Vignette the sprite using a soft, linear, circular aperture.
		This draws a linearly ramped mask of the specified size into
		the alpha channel.

		:param r1,r2: (pixels) inner,outer radii of ramp

		:param x,y: (pixels) optional aperture center (0,0 is center)

		:return: nothing

		"""
		d = 255 - (255 * (np.hypot(self.ax-x,self.ay+y)-r1) / (r2-r1))
		d = np.where(np.less(d, 0), 0,
					 np.where(np.greater(d, 255), 255, d)).astype(np.uint8)
		self.alpha[::] = d

	def alpha_gradient2(self, r1, r2, bg, x=0, y=0):
		"""Add soft-edged apperature (gradient vignette)

		Like alpha_gradient() above, but mask is applied **directly to
		the image data** (under the assumption that the background is a
		solid fill of 'bg').

		:param r1,r2: (pixels) inner,outer radii

		:param bg: background color in C() compatible format

		:param x,y: (pixels) coords of mask center in world coords

		:return: nothing

		"""
		d = 1.0 - ((np.hypot(self.ax-x, self.ay+y) - r1) / (r2 - r1))
		alpha = clip(d, 0.0, 1.0)
		i = pygame.surfarray.pixels3d(self.im)
		alpha = np.transpose(np.array((alpha,alpha,alpha)), axes=[1,2,0])
		if is_sequence(bg):
			bgi = np.zeros(i.shape)
			for n in range(3):
				bgi[:,:,n] = bg[n]
		else:
			bgi = bg
		i[::] = ((alpha * i.astype(np.float)) +
				((1.0-alpha) * bgi)).astype(np.uint8)
		self.alpha[::] = 255;

	def dim(self, mult, meanval=128.0):
		"""Reduce sprite contrast

		Reduce sprite's contrast. Modifies sprite's image data.
		v = (1-mult)*(v-mean), where v is the pixel values.

		*NB* This assumes the mean value of the image data is
		'meanval', which is not always the case. If it's not, then you
		need to compute and pass in the mean value explicitly.

		:param mult: scale factor

		:param meanval: assumed mean pixel value [0-255]

		:return: nothing

		"""
		pixs = pygame.surfarray.pixels3d(self.im)
		pixs[::] = (float(meanval) + ((1.0-mult) *
			   (pixs.astype(np.float)-float(meanval)))).astype(np.uint8)

	def thresh(self, threshval):
		"""Threshold sprite image data

		Threshold (binarize) sprite's image data
		v =	 (v > thresh) ? 255 : 1, where v is pixel value

		:param threshval: threshold (0-255)

		:return: nothing

		"""
		pixs = pygame.surfarray.pixels3d(self.im)
		pixs[::] = np.where(np.less(pixs, threshval), 1, 255).astype(np.uint8)

	def on(self):
		"""Turn sprite on

		Sprite will get blitted.

		"""
		self._on = 1

	def off(self):
		""" Turn sprite off.

		Sprite won't be drawn, even when blit method is called.

		"""
		self._on = 0

	def toggle(self):
		"""Flip on/off flag.

		:return: current state of flag.

		"""
		self._on = not self._on
		return self._on

	def state(self):
		"""Get current on/off flag state.

		:return: boolean on/off flag

		"""
		return self._on

	def moveto(self, x, y):
		"""Move sprite to new location

		:param x,y: (pixels) framebuffer coords of new location

		:return: nothing

		"""
		self.x = x
		self.y = y

	def rmove(self, dx=0, dy=0):
		"""Relative move.

		Shifts sprite by dx,dy pixels relative to current position.

		:param dx,dy: (pixels) framebuffer coords of new location

		:return: nothing

		"""
		self.x = self.x + dx
		self.y = self.y + dy

	def blit(self, x=None, y=None, fb=None, flip=None, force=0,
			 textureonly=None):
		"""Copy sprite to screen (block transfer).

		1. x,y,fb etc are all internal properties of each sprite. You
		   don't need to supply them here unless you want to change
		   them at the same time you blit

		2. Don't forget to *flip* the framebuffer after blitting!

		:param x,y: (pixels) optional new screen location

		:param fb: frame buffer

		:param flip: (boolean) flip after blit?

		:param force: (boolean) override on/off flag?

		"""
		if not force and not self._on:
			return

		if fb is None:
			fb = self.fb

		if fb is None:
			# dummy sprite -- no associated frame buffer..
			return 1

		# save position, if specified, else used saved position
		if x is None:	x = self.x
		else:			self.x = x

		if y is None:	y = self.y
		else:			self.y = y

		if self.texture:
			# pre-rendered texture -- just blit it
			_texture_blit(self.fb, self.texture, x, y,
						  rotation=self.rotation,
						  contrast=self.contrast,
						  xscale=self.xscale, yscale=self.yscale)
		else:
			rgba = pygame.image.tostring(self.im, 'RGBA', 1)
			#im = self.array[:,::-1,:]
			#alpha = self.alpha[:][:,:,np.newaxis]
			#rgba = np.concatenate((im, alpha), axis=2)
			#rgba = np.transpose(rgba, axes=[1,0,2]).tostring()	 <-- killer!
			tex = _texture_create(rgba, self.w, self.h)
			_texture_blit(self.fb, tex, x, y,
						  rotation=self.rotation,
						  contrast=self.contrast,
						  xscale=self.xscale, yscale=self.yscale)
			_texture_del(tex)

		if flip:
			fb.flip()

		# if moving sprite, move to next position..
		self.x = self.x + self.dx
		self.y = self.y + self.dy
		return 1

	def fastblit(self):
		"""NOP -- passes through to blit() method with no args

		"""
		return self.blit()

	def render(self, clear=False):
		"""Render image data into GL texture memory for speed.

		"""
		if self.texture:
			_texture_del(self.texture)
		if not clear:
			s = pygame.image.tostring(self.im, 'RGBA', 1)
			self.texture = _texture_create(s, self.w, self.h)

	def subimage(self, x, y, w, h, center=None):
		"""Extract sub-region of sprite into new sprite

		Generates a *new* sprite from the specified sub-region of
		current sprite.

		*NB* (Wed Apr 19 14:32:03 2006 mazer)
		Despite what the pygame docs say about subsurface(), this
		function COPIES the image data. Changes to the subimage will
		*NOT* affect the parent!

		:param x,y: (pixels) coordinates of subregion (0,0) is upper
				left corner of parent/src sprite

		:param w,h: (pixels) width and height of subregion

		:param center: (boolean) Does (x,y) refer to the center or
				upper left corner of sprite?

		:return: new sprite

		"""
		if self.xscale != 1.0 or self.yscale != 1.0:
			Logger("Can't subimage scaled sprites yet!\n")
			return None

		if center:
			x = self.X(x) - (w/2)
			y = self.Y(y) - (h/2)

		return ScaledSprite(image=self.im.subsurface((x, y, w, h)),
							rwidth=int(round(w)), rheight=int(round(h)),
							x=self.x, y=self.y, dx=self.dx, dy=self.dy,
							depth=self.depth, fb=self.fb, on=self._on)

	def clone(self):
		"""Duplicate sprite

		Clone this sprite by making a new instance with all
		data, including image and alpha, duplicated.

		*NB* Wed Apr 19 14:32:03 2006 mazer - Despite what the pygame
		docs say about subsurface(), this function COPIES the image
		data. Changes to the clone will *NOT* affect the parent!
		
		"""
		import copy

		s = ScaledSprite(width=self.dw, height=self.dh,
						 rwidth=self.w, rheight=self.h,
						 image=self,
						 x=self.x, y=self.y, dx=self.dx, dy=self.dy,
						 on=self._on, depth=self.depth,
						 rotation=self.rotation, contrast=self.contrast,
						 name='clone of '+self.name,
						 fb=self.fb)
		s.alpha[::] = self.alpha[::]	   # copy the alpha mask too..
		s.userdict = copy.copy(self.userdict)
		return s

	def setdir(self, angle, vel):
		"""Set direction of motion

		:param angle: (deg)

		:param vel: (pix/sec)

		:return: nothing

		"""
		angle = np.pi * angle / 180.0
		self.dx = vel * np.cos(angle)
		self.dy = vel * np.sin(angle)

	def displayim(self):
		return pygame.transform.scale(self.im, (self.dw, self.dh))

	def save(self, fname, mode='w'):
		"""Save sprite using pygame builtins

		Image is saved at the DISPLAYED size, not the memory/real size

		"""
		# use pygame's save function to write image to file (PNG, JPG)
		return pygame.image.save(self.displayim(), fname)

	def save_ppm(self, fname, mode='w'):
		"""Save sprite as PPM file (local implementation)

		Alpha channel is not saved.
		Saved WITHOUT rescaling

		"""
		try:
			file = open(fname, mode)
			file.write('P6\n# pype save_ppm\n%d %d\n255\n' % (self.w, self.h))
			file.write(pygame.image.tostring(self.im, 'RGB'))
			file.close()
		except IOError:
			Logger("Can't write %s.\n" % fname)
			return None

	def save_alpha_pgm(self, fname, mode='w'):
		"""Save sprite alpha channel as PGM file (local implementation)

		Alpha only -- no RGB data.
		Saved WITHOUT rescaling

		"""
		try:
			file = open(fname, mode)
			file.write('P5\n# pype save_ppm\n%d %d\n255\n' % (self.w, self.h))
			a = self.alpha[::]
			file.write(a.tostring())
			file.close()
		except IOError:
			Logger("Can't write %s.\n" % fname)
			return None
		
class Sprite(ScaledSprite):
	"""Sprite object (wrapper for pygame surface class).

	Note about .centerorigin: If centerorigin is False (default condition),
	the origin is the UPPER LEFT corner of the sprite, positive x values
	to the right, positive y-values running down. If center origin is True,
	then it's normal cartesian coords with (0,0) in the center of the sprite
	postive x-values to the right, positive y-values up.

	"""

	def __init__(self, width=100, height=100, x=0, y=0, depth=0,
				 fb=None, on=1, image=None, dx=0, dy=0, fname=None,
				 name=None, icolor='black', ifill='yellow',
				 centerorigin=0, rotation=0.0, contrast=1.0, scale=1.0):
		"""Sprite Object -- pype's main tool for graphics generation.

		:param width, height: (int) sprite size in pixels

		:param x, y: (int) sprite position in pixels

		:param depth: (int; default 0) sprite stacking order for
				DisplayList (0 is on top)


		:param fb: (FrameBuffer object) associated FrameBuffer object

		:param on: (boolean) on/off (for DisplayList)

		:param image: (Sprite object) seed sprite to get data from

		:param dx, dy: (int) xy velocity (shift/blit)

		:param fname: (string) Filename of image to load sprite data from.

		:param name: (string) Sprite name/info

		:param icolor: (string) icon color (for UserDisplay)
		
		:param ifill: (string) icon fill (for UserDisplay)

		:param centerorigin: (boolean; default=0) If 0, then the upper
				left corner of the sprite is 0,0 and increasing y goes
				DOWN, increase x goes RIGHT. If 1, then 0,0 is in the
				center of the sprite and increasing y goes UP and
				increase X goes RIGHT.

		:param rotation: (float degrees) GL-pipeline rotation
				factor. Very fast pre-blit rotation.

		:param contrast: (float 0-1.0) GL-pipeline contrast scaling
				factor. Very fast pre-blit scaling of all pixel
				values.

		:param scale: (float) GL-pipeline spatial scaling
				factor. Very fast pre-blit scaling of all pixel
				values.

		"""

		if fname:
			width, height = None, None
		else:
			width, height = width*scale, height*scale
			
		ScaledSprite.__init__(self,
							  width=width, height=height,
							  rwidth=width, rheight=height,
							  x=x, y=y, depth=depth,
							  fb=fb, on=on, image=image,
							  dx=dx, dy=dy,
							  fname=fname, name=name,
							  icolor=icolor, ifill=ifill,
							  centerorigin=centerorigin,
							  rotation=rotation, contrast=contrast)

class PolySprite(object):
	"""Polygon Sprite

	This is a special sprite that doesn't have image data. Instead
	it contains a bunch of points that define a polygon. I don't
	think anybody's really using this, it's something I was playing
	with.

	"""

	_id = 0

	def __init__(self, points, color, fb,
				 closed=0, width=1, joins=1, line=0, contig=1,
				 on=1, depth=0, name=None, x=0, y=0):
		"""PolySprite instantiation method

		:param points: (pixels) polygon vertices. List of (x,y) pairs,
				where (0,0) is screen center, positive y is up,
				positive x is to the right.

		:param color: line color

		:param fb: framebuffer

		:param closed: (boolean) open or closed polygon?

		:param width: (pixels) line width

		:param line: (bool) if true, draw lines, else filled polygon

		:param contig: (bool) if true (default), contiguous sequence
				of lines. Otherwise, each pair of points as
				interpreted as single broken line.

		:param joins: (boolean) join lines and use end-caps

		:param on: (boolean) just like regular Sprite class

		:param depth: depth of sprite (for DisplayList below). The
				DisplayList class draws sprites in depth order, with
				large depths being draw first (ie, 0 is the top-most
				layer of sprites)

		:param name: debugging name (string) of the sprite; if not
				set, then either the filename or a unique random name
				is used instead.

		"""

		if name:
			self.name = name
		else:
			self.name = "PolySprite%d" % PolySprite._id

		self._id = PolySprite._id
		PolySprite._id = PolySprite._id + 1

		self.fb = fb
		self.points = []
		self.color = color
		self.closed = closed
		self.width = width
		self.line = line
		self.joins = joins
		self.contig = contig
		self._on = on
		self.depth = depth
		self.x0 = x
		self.y0 = y
		self.points = np.array(points)

	def __repr__(self):
		return ('<PolySprite "%s"@(%d,%d) #%d depth=%d on=%d>' %
				(self.name, self.x0, self.y0, self._id, self.depth, self._on))

	def clone(self):
		return PolySprite(
			self.points, self.color, self.fb,
			closed=self.closed, width=self.width, line=self.line,
			joins=self.joins, on=self.on, depth=self.depth,
			name='clone of '+self.name, x=self.x0, y=self.y0)

	def moveto(self, x, y):
		"""Absolute move.

		"""
		self.x0 = x
		self.y0 = y

	def rmove(self, dx, dy):
		"""Relative move.

		"""
		self.x0 = self.x0 + dx
		self.y0 = self.y0 + dy

	def blit(self, flip=None, force=None):
		"""Draw PolySprite.

		"""
		if not self._on and not force:
			return

		if self.line:
			w = self.width
		else:
			w = 0

		self.fb.lines(self.points+[self.x0, self.y0],
					  color=self.color, width=w,
					  joins=self.joins,
					  contig=self.contig,
					  closed=self.closed,
					  flip=flip)

	def on(self):
		"""Turn PolySprite on.

		"""
		self._on = 1

	def off(self):
		"""Turn PolySprite off.

		"""
		self._on = 0

	def toggle(self):
		"""Toggle PolySprite (off->on or on->off)

		"""
		self._on = not self._on
		return self._on

class MovieDecoder(object):
	def __init__(self, filename):
		"""MPEG movie decoder.

		:param filename: (string) specifies filename of movie

		"""
		self.mov = pygame.movie.Movie(filename)
		(self.w, self.h) = self.mov.get_size()
		self.surf = pygame.Surface((self.w, self.h))
		self.mov.set_display(self.surf)

	def getframe(self, n, sprite=None):
		"""get nth frame from movie.

		:param n: (int) Frame number. If beyond length of movie, return's None

		:param sprite: (Sprite obj) optional sprite to render into

		:return: None for failure of past end of movie. If sprite is specified,
				returns 1, else rendered frame as numpy array.

		"""
		if self.mov.render_frame(n) == n:
			a = pygame.surfarray.array3d(self.surf)
			if sprite:
				sprite.array[:] = a
				return 1
			else:
				return a
		else:
			return None

class DisplayList(object):
	"""Sprite-list manager.

	DisplayList collects and manages a set of Sprites so you can worry
	about other things.

	Each sprite is assigned a priority or stacking order. Low
	numbers on top, high numbers on the bottom. When you ask the
	display list to update, the list is sorted and blitted bottom
	to top (the order of two sprites with the same priority is
	undefined).

	The other useful thing is that the UserDisplay class (see
	userdpy.py) has a display() method that takes a display list
	and draws simplified versions of each sprite on the user display
	so the user can see (approximately) what the monkeys is seeing.

	*NB* Sprites are only drawn when they are *on* (see on() and off()
	methods for Sprites).

	"""

	def __init__(self, fb, comedi=True):
		"""Instantiation method.

		:param fb: framebuffer associated with this list. This is sort
				of redundant, since each sprite knows which
				framebuffer it lives on too. It's currently only used
				for clearing and flipping the framebuffer after
				updates.

		"""

		if comedi:
			from pype import Timer
		else:
			from simpletimer import Timer

		self.sprites = []
		self.fb = fb
		self.bg = fb.bg
		self.timer = Timer()
		self.trigger = None
		self.action = None


	def __del__(self):
		"""Delete method.

		Called when the display list is deleted. Goes through and
		tries to delete all the member sprites. The idea is that if
		you delete the display list at the each of each trial, this
		function will clean up all your sprites automatically.

		"""
		for s in self.sprites:
			del s

	def add(self, s, timer=None,
			on=None, onev=None, off=None, offev=None):
		"""Add sprite to display list.

		Each time self.update is called, the timer will be
		checked and used to decide whether to turn this
		sprite on or off.

		:param s: (Sprite/list of Sprites) sprites are added in depth order
		:param timer: (Timer) Timer object to use as clock
		:param on: (ms) time to turn sprite on
		:param onev: (str) encode to store for on event
		:param off: (ms) time to turn sprite off
		:param offev: (str) encode to store for off event

		:return: nothing

		"""
		if is_sequence(s):
			for i in s:
				self.add(i, timer=timer,
						 on=on, onev=onev, off=off, offev=offev)
		else:
			s._timer = timer
			s._ontime = on
			s._onev = onev
			s._offtime = off
			s._offev = offev
			for ix in range(0, len(self.sprites)):
				if s.depth > self.sprites[ix].depth:
					self.sprites.insert(ix, s)
					return
			self.sprites.append(s)

	def delete(self, s=None):
		"""Delete single or multiple sprites from display list.

		*NB* Same as clear() and delete_all() methods if called with
		no arguments.

		:param s: (sprite) sprite (or list of sprites) to delete, or
				None for delete all sprites.

		:return: nothing

		"""
		if s is None:
			self.sprites = []
		elif is_sequence(s):
			for i in s:
				self.delete(i)
		else:
			self.sprites.remove(s)

	def clear(self):
		"""Delete all sprites from the display list.

		Same as delete_all().

		"""
		self.delete()

	def delete_all(self):
		"""Delete all sprites from display list.

		Same as clear().

		"""
		self.delete(None)

	def after(self, time=None, action=None, args=None):
		"""Set up an action to be called in the future.

		After 'time' ms, the action function will be called
		with three arguments: requested elapsed time, actual
		elapsed time and the user-specfied args.

		:param time: (ms) ms on the timer

		:param action: (fn) function to call

		:param args: (anything) passed as third arg to 'action' function

		:return: nothing

		"""

		if time:
			self.timer.reset()
		self.trigger = time
		self.action = action
		self.args = args

	def update(self, flip=None, preclear=1):
		"""Draw sprites on framebuffer

		1. Clear screen to background color (if specified)
		2. Draw all sprites (that are 'on') from bottom to top
		3. Optionally do a page flip.

		:param flip: (boolean) flip after?

		:param preclear: (boolean) clear first?

		:return: list of encodes (from timer-triggered sprites)

		"""

		# before we do anything, see if a trigger time's been reached
		if self.action and self.trigger and self.timer.ms() >= self.trigger:
			et = self.timer.ms()		# actual elapsed time
			ret = self.trigger			# requested elapsed time
			fn = self.action			# function to call
			args = self.args			# args to pass to fn
			self.after()				# clear trigger

			fn(ret, et, args)			# run action

		# clear screen to background..
		if preclear:
			if self.bg:
				self.fb.clear(color=self.bg)
			else:
				self.fb.clear()

		# draw sprites in depth order
		encodes = []
		for s in self.sprites:
			if (not s._ontime is None) and s._timer.ms() > s._ontime:
				# turn sprite on and clear on trigger
				s._ontime = None
				s.on()
				encodes.append(s._onev)
			elif (not s._offtime is None) and s._timer.ms() > s._offtime:
				# turn sprite off and clear off trigger
				s._offtime = None
				s.off()
				encodes.append(s._offev)
			s.blit()

		# possibly flip screen..
		if flip:
			self.fb.flip()
		return encodes

def _texture_del(texture):
	"""Delete existing GL texture on video card.

	:note: INTERNAL USE ONLY

	"""

	if 0:
		#
		# THIS IS NOT CORRECT - NEED TO TRACK DOWN SOURCE!!!!
		#
		# I think this changed with 3.1.0 release... not sure!
		if OpenGL.version.__version__ > "3.0.0":
			(textureid, w, h) = texture
			ogl.glDeleteTextures(np.array([textureid]))
		else:
			ogl.glDeleteTextures(texture[0])
	ogl.glDeleteTextures(texture[0])
    
    
def _texture_create(rgbastr, w, h):
    """Create GL texture on video card.

	:note: INTERNAL USE ONLY

	"""
	ogl.glPushAttrib(ogl.GL_TEXTURE_BIT)
	textureid = ogl.glGenTextures(1)
	ogl.glBindTexture(ogl.GL_TEXTURE_2D, textureid)
	ogl.glTexParameteri(ogl.GL_TEXTURE_2D,
						ogl.GL_TEXTURE_MAG_FILTER, ogl.GL_LINEAR)
	ogl.glTexParameteri(ogl.GL_TEXTURE_2D,
						ogl.GL_TEXTURE_MIN_FILTER, ogl.GL_LINEAR)
	ogl.glTexImage2D(ogl.GL_TEXTURE_2D, 0, ogl.GL_RGBA,
					 w, h, 0, ogl.GL_RGBA, ogl.GL_UNSIGNED_BYTE, rgbastr)
	ogl.glPopAttrib(ogl.GL_TEXTURE_BIT)
	return (textureid, w, h)

def _texture_blit(fb, texture, x, y,
				  rotation=0, draw=1, contrast=1.0, xscale=1.0, yscale=1.0):
	"""Transfer (BLIT) GL texture to display.

	(x, y) are center coords, where (0,0) is screen center.

	The default settings for scaling of texture mapps are for
	linear interoplation for both scale up and scale down. These
	can be set/changed using glTexParameteri() to set
	GL_TEXTURE_MIN_FILTER (default is GL_NEAREST_MIPMAP_LINEAR)
	and/or GL_TEXTURE_MAG_FILTER (default is GL_LINEAR). First is
	for scaling down, second scaling up.

	:note: INTERNAL USE ONLY

	"""

	(texture, w, h) = texture
	nw = w * xscale
	nh = h * yscale
	x = (x + fb.hw)
	y = (y + fb.hh)
	cx = x - (nw/2)
	cy = y - (nh/2)

	ogl.glPushMatrix()
	ogl.glPushAttrib(ogl.GL_TEXTURE_BIT)

	ogl.glBindTexture(ogl.GL_TEXTURE_2D, texture)

	# use the GL pipeline to rotate the texture
	if not rotation == 0:
		ogl.glTranslate(x, y, 0)
		ogl.glRotate(rotation, 0, 0, 1.0)
		ogl.glTranslate(-x, -y, 0)

	ic = ((0,0), (1,0), (1,1), (0,1))
	oc = ((cx, cy), (cx+nw, cy), (cx+nw, cy+nh), (cx, cy+nh))

	ogl.glBegin(ogl.GL_QUADS)
	#ogl.glColor4f(contrast, contrast, contrast, 1.0)
	ogl.glColor4f(1.0, 1.0, 1.0, contrast)
	for n in range(4):
		ogl.glTexCoord2f(ic[n][0], ic[n][1])
		ogl.glVertex(oc[n][0], oc[n][1])
	ogl.glEnd()

	# restore GL state
	ogl.glPopAttrib(ogl.GL_TEXTURE_BIT)
	ogl.glPopMatrix()

def is_sequence(x):
	"""Is arg a sequence-type?

	"""
	return (type(x) is types.ListType) or (type(x) is types.TupleType)

def colr(*args, **kwargs):
	"""Improved C() -- converts argument to RGBA color in useful way.
	   By default generates values 0-255, but normal keyword is True,
	   colors are assumed to be specified/generated on the range [0-1].

	   Handled cases:
		  colr() -> transparent color key (0,0,0,0)
		  colr(r,g,b)
		  colr((r,g,b))
		  colr(lum) --> (lum,lum,lum)
		  colr(r,g,b,a)
		  colr((r,g,b,a))
		  colr(lum) --> (lum,lum,lum, 255)
		  colr('name') --> simple named color
		  colr('r,g,b') --> color as string
		  colr('r,g,b,a') --> color with alpha as string
	
	"""
	normal = kwargs.has_key('normal') and kwargs['normal']
	if normal:
		max = 1.0
	else:
		max = 255

	if len(args) == 0:
		c = np.array((0,0,0,0))			  # transparent
	elif len(args) == 1:
		if type(args[0]) is types.StringType:
			if args[0].lower() == 'black' or args[0].lower() == 'k':
				c = np.array((1,1,1,max))
			elif args[0].lower() == 'white' or args[0].lower() == 'w':
				c = np.array((max,max,max,max))
			elif args[0].lower() == 'red' or args[0].lower() == 'r':
				c = np.array((max,0,0,max))
			elif args[0].lower() == 'green' or args[0].lower() == 'g':
				c = np.array((0,max,0,max))
			elif args[0].lower() == 'blue' or args[0].lower() == 'b':
				c = np.array((0,0,max,max))
			else:
				c = np.array(map(float, string.split(args[0], ',')))
		else:
			try:
				l = len(args[0])
				if l > 1:
					c = np.array(args[0])
				else:
					c = np.array((args[0][0], args[0][0], args[0][0],))
			except TypeError:
				c = np.array((args[0], args[0], args[0],))
	else:
		c = np.array(args)
	if len(c) < 4:
		if not normal:
			c = np.concatenate((c, [255],))
		else:
			c = np.concatenate((c, [1.0],))

	if not normal:
		c = np.round(c)
			
	return c



def C(color, gl=0):
	"""Color specification/normalization

	Takes number of similar color specifications and tries to convert
	them all into a common format compatible with pygame, that is a
	length 4 tuple: (red, green, blue, alpha) where the values vary
	[0-255], where: 0=off/transparent and 255=on/opaque.

	:param gl: (boolean) if true, then values range [0-1], else [0-255]

	"""
	try:
		n = len(color)
		if n == 1:
			color = (color, color, color, 255) # scalar grayscale value
		elif n == 3:
			color = color + (255,)		# RGB triple, add A
		elif n == 4:
			color = color				# RGBA quad
	except TypeError:
		color = (color, color, color, 255) # non-sequence, assume scalar gray

	if gl:
		color = np.round(np.array(color)/255., 3)
	return color

def barsprite(w, h, angle, color, **kw):
	"""Make a bar (creates new sprite).

	Front end for the Sprite instantiation method. This makes a sprite
	of the specificed width and hight, fills with the specified color
	(or noise) and rotates the sprite to the specified angle.

	This *really* should be a class that inherits from Sprite().

	:return: (sprite) requested bar

	"""
	s = apply(Sprite, (w, h), kw)
	if color == (0,0,0):
		s.noise(0.50)
	else:
		s.fill(color)
	s.rotate(angle, 0)
	return s

def barspriteCW(w, h, angle, color, **kw):
	return apply(barsprite, (w, h, angle, color), kw)

def barspriteCCW(w, h, angle, color, **kw):
	return apply(barsprite, (w, h, -angle, color), kw)

def fixsprite(x, y, fb, fix_size, color, bg):
	"""Fixation target sprite generator.

	Generates a simple sprite containing an "industry standard"
	fixation target :-) Target is a solid filled circle of the
	specified color.

	:param x,y: (pixels) location of target (center)

	:param fb: frame buffer

	:param fix_size: (pixels) radius of target (use _ZERO_ for single
		pixel target)

	:param color: fill color

	:param bg: background color

	:return: new sprite containing the target

	"""
	if fix_size > 0:
		d = 1 + 2 * fix_size			# make it odd
		fixspot = Sprite(d, d, x, y, fb=fb, depth=0, on=0)
		fixspot.fill(bg)
		fixspot.circle(color=color, r=fix_size)
	else:
		fixspot = Sprite(1, 1, x, y, fb=fb, depth=0, on=0)
		fixspot.fill(color)
	return fixspot

def fixsprite2(x, y, fb, fix_size, fix_ring, color, bg):
	"""fancy fixation target sprite generator

	Generates a sprite containing a circular fixation target
	surrounded by an annulus of black (to increase detectability).

	:param x,y: (pixels) location of target (center)

	:param fb: frame buffer

	:param fix_size: (pixels) radius of target (use _ZERO_ for single
		pixel target)

	:param fix_ring: (pixels) radius of annulus

	:param color: fill color

	:param bg: background color

	:return: new sprite containing the target

	"""

	d = 1 + 2 * fix_size
	ringd = 1 + 2 * fix_ring

	fixspot = Sprite(ringd, ringd, x, y, fb=fb, depth=0, on=0)
	fixspot.fill(bg)

	fixspot.circle(color=(1,1,1), r=fix_ring)
	if fix_size > 0:
		fixspot.circle(color=color, r=fix_size)
	else:
		fixspot.pix(fixspot.w/2, fixspot.h/2, color)

	return fixspot

def quickinit(dpy=":0.0", w=100, h=100, fullscreen=0, mouse=0):
	"""Quickly setup and initialize framebuffer

	:param dpy: (string) display string

	:param w,h: (pixels) width and height of display

	:param fullscreen: (boolean) full screen mode (default is no)

	:param mouse: (boolean) now mouse cursor? (default is no)

	:return: live frame buffer

	"""
	if dpy is None:
		dpy = os.environ['DISPLAY']
	return FrameBuffer(dpy, w, h, fullscreen,
					   sync=None, mouse=mouse)

def quickfb(w, h, fullscreen=0):
	"""Get a quick (windowed) FrameBuffer for scripts and testing.

	:param w,h: (pixels) width and height of display

	:return: live frame buffer

	"""
	return FrameBuffer(os.environ['DISPLAY'],
					   w, h, fullscreen=fullscreen,
					   sync=None, mouse=1)


def ppflag(flags):
	flagd = {
		'DOUBLEBUF':	DOUBLEBUF,
		'HWSURFACE':	HWSURFACE,
		'FULLSCREEN':	FULLSCREEN,
		'OPENGL':		OPENGL,
		'FULLSCREEN':	FULLSCREEN,
		}

	s = None
	for k in flagd.keys():
		if flags & flagd[k]:
			if s: s = s + '|' + k
			else: s = k
	return s

def drawtest(fb, s):
	"""Draw standard test pattern.
	"""

	import pypeversion

	fb.clear((1,1,1))
	if s: s.blit(force=1)

	# draw fixed 10 cycles/display vert grating
	dy = -100
	gr = Sprite(fb.w, fb.w, 0, dy, fb=fb)
	singrat(gr, 10.0, 90.0, 0.0)
	gr = gr.subimage(0, 0, gr.w, 50)
	gr.alpha[:] = 250
	gr.blit(force=1)
	fb.string(0, dy, '< 10 cycles >', (255, 0, 0))
	
	if 1:
		# alpha tests
		s = Sprite(x=50, y=50, width=150, height=150,
				   fb=fb, on=1)
		s.fill((255,1,1))
		s.alpha[::]=128
		s.blit()
		s = Sprite(x=-50, y=-50,  width=150, height=150,
				   fb=fb, on=1)
		s.fill((1,255,1))
		s.alpha[::]=128
		s.blit()

		s = Sprite(x=-fb.w/2, y=-fb.h/2,
				   width=150, height=150, fb=fb, on=1)
		s.fill((255,255,1))
		s.alpha[::]=128
		s.blit()

		s = Sprite(x=-100, y=100,
				   width=100, height=100, fb=fb, on=1)
		s.array[:] = 128
		s.array[1:25,:,0] = 255
		s.array[:,1:25,1] = 1
		s.array[1:25,1:25,2] = 1
		s.alpha[:] = 128
		s.blit()

		s = Sprite(x=200, y=55, width=50, height=50,
				   fb=fb, on=1, centerorigin=0)
		s.fill((255,1,255))
		s.line(0, 0, 0, 25, (255,255,255), 5)
		s.line(0, 0, 25, 25, (255,255,255), 5)
		s.blit()

	if 1:
		# sprite line drawing
		s = Sprite(x=200, y=-55, width=50, height=50,
				   fb=fb, on=1, centerorigin=1)
		s.fill((255,1,255))
		s.line(0, 0, 0, 25, (255,255,255), 5)
		s.line(0, 0, 25, 25, (255,255,255), 5)
		s.blit()

	if 1:
		# sprite fills/rectangles
		s = Sprite(x=-200, y=55, width=50, height=50,
				   fb=fb, on=1, centerorigin=1)
		s.fill((255,255,255))

		s.rect(0, 0, 25, 25, (255,0,0))
		s.rect(10, 10, 25, 25, (255,255,0))
		s.rect(-10, -10, 25, 25, (0,255,0))
		s.rect(0, 0, 5, 5, (1,1,1))

		s.line(0,-25,0,25, (128,128,128), width=1)
		s.line(-25,0,25,0, (128,128,128), width=1)
		s.blit()

	if 1:
		# direct draws to framebuffer w/o sprite
		fb.rectangle(200, 200, 30, 30, (255,255,255,128))
		fb.circle(-200, 200, 20, (1,1,1, 128))
		fb.line((0, 0), (-100,-100), width=5,
					 color=(128,128,128))
		fb.line((0, 0), (-100,-100), width=1,
					 color=(0,0,255))

		fb.lines([(0,0),(0,100),(100,0)], closed=1,
					 width=0, color=(255,0,255))

		fb.circle(150, -150, 50, (255,255,1,128), 0)
		fb.circle(150, -150, 40, (255,1,1,255), 10)
		fb.string(0, 0, '[pype%s]' % pypeversion.PypeVersion,
					   (0, 255, 255))

	if 1:
		# test PolySprite
		pts = [(100,0), (25,25), (0,100), (-25,25), (-100,0)]
		s = PolySprite(pts, (255,255,1), fb, line=1, width=3)
		s.blit()

		s = Sprite(50,50,100,100, fb=fb)
		s.fill((128,255,128,128))
		s.blit()

		s = tickbox(100, 100, 50, 50, 3, (1,1,1), fb)
		s.blit()


	fb.sync(0)
	fb.flip()


def tickbox(x, y, width, height, lwidth, color, fb):
	fs = 1.50
	pts = np.array(( (0, 1), (0, fs), (0, -1), (0, -fs),
					 (1, 0), (fs, 0), (-1, 0), (-fs, 0) ))
	pts[:,0] = pts[:,0] * width / 2.0 + x
	pts[:,1] = pts[:,1] * height / 2.0 + y
	s = PolySprite(pts, color=color, fb=fb, joins=0, line=1,
				   contig=0, width=lwidth)
	return s

if __name__ == '__main__':
	from simpletimer import Timer

	def drawtest2(fb):
		s1 = Sprite(100, 100, -100, 0, fb=fb)
		s2 = Sprite(100, 100, 100, 0, fb=fb, scale=1)
		s2.alpha_gradient(r1=40, r2=50)
		for n in range(0,2*360,10):
			fb.clear()
			alphabar(s1, 10, 100, n, WHITE)
			s1.blit()
			s2.moveto(0, 0)
			singrat(s2, 1, 0.0, n, WHITE)
			s2.blit()
			s2.moveto(100, 0)
			s2.thresh(127)
			s2.blit()
			fb.flip()


	def drawtest3(fb):
		x = -200
		w = 100
		ss = []
		for n in range(5):
			ss.append(ScaledSprite(width=100, height=w, x=x, y=-100, fb=fb,
								   fname='lib/testpat.png'))
			ss.append(ss[-1].clone())
			singrat(ss[-1], 1, 0.0, n, WHITE)
			ss[-1].moveto(x,100)
			
			x = x + 100
			w = int(w/2)
			
		for n in range(0,2*360,10):
			fb.clear()
			for s in ss:
				#singrat(s, 1, 0.0, n, WHITE)
				s.set_rotation(-n)
				s.blit()
				print s.rotation,
			print
			fb.flip()
			sys.stdin.readline()
	
	def drawtest4(fb):
		x = -200
		w = 100
		ss = []

		sig = 20
		s = ScaledSprite(width=sig*6, x=0, y=0, fb=fb)
		for n in range(0,2*360,10):
			fb.clear()
			gabor(s, 3, n, 45., sig, WHITE)
			#singrat(s, 1, 0.0, n, WHITE)
			#s.set_rotation(n)
			s.blit()
			fb.flip()

	fb=quickfb(500,500)

	if 1:
		#drawtest4(fb)
		drawtest3(fb)
		#drawtest2(fb)
		#sys.stdout.write('>>>'); sys.stdout.flush()
		#sys.stdin.readline()

	if 0:
		s1 = Sprite(100, 100, -100, 0, fb=fb, on=0)
		s1.fill((255,255,255))
		s2 = Sprite(100, 100, 100, 0, fb=fb, on=0)
		s2.fill((255,255,1))
		dlist = DisplayList(fb, comedi=False)

		ti = Timer(on=False)
		fdur = int(round(1000/fb.calcfps()))
		dlist.add(s1, ti, 1100, 's1_on', 1200, 's1_off')
		dlist.add(s2, ti, 1150, 's2_on', 1250, 's2_off')

		# start the timer going
		dlist.update(flip=1)
		ti.reset()
		last = ti.ms()
		print last
		while ti.ms() < 5000:
			fb.clear()
			elist = dlist.update(flip=1)
			if len(elist):
				x = ti.ms()
				print x, x-last, elist
				last = x

