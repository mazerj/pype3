# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""Numeric-based sprite object

This is not tested and not 100% complete -- don't use yet.

Author -- James A. Mazer (james.mazer@yale.edu)

"""

__author__   = '$Author: mazer $'
__date__     = '$Date: 2010-12-10 11:40:31 -0500 (Fri, 10 Dec 2010) $'
__revision__ = '$Revision: 2 $'
__id__       = '$Id: numsprite.py 2 2010-12-10 16:40:31Z mazer $'
__HeadURL__  = '$HeadURL$'


"""Revision History

Tue Apr  7 10:34:35 2009 mazer

- started work..

"""

from numpy import *
from numpy.random import uniform

try:
	from OpenGL.GL import *
	from OpenGL.GLU import *
	from OpenGL.GLUT import *
except ImportError:
	sys.stderr.write('Warning: numsprite required OpenGL module\n')
	sys.exit(1)
	
from PIL import Image
from sprite import _C, genaxes

from pypedebug import keyboard
import time

class NumSprite:
	"""Pure Numeric-based Sprite object.
	"""
	_count = 0
	
	def __init__(self, width=100, height=100, x=0, y=0, depth=0, \
				 fb=None, on=1, image=None, dx=0, dy=0, fname=None, \
				 name=None, icolor='black', centerorigin=0):
		self.x = x
		self.y = y
		self.dx = dx
		self.dy = dy
		self.depth = depth
		self.fb = fb
		self._on = on
		self.icolor = icolor
		self.centerorigin = centerorigin
		self.array = None
		self.alpha = None
		
		if fname:
			# load image data from file using pygame tools
			self.fromPIL(Image.open(fname))
		elif image:
			raise Error
		else:
			# new RGBA image from scratch
			self.array = zeros((width, height, 3), uint8)
			self.alpha = zeros((width, height), uint8)
			self.alpha[::] = 255

		# set dimensions automatically based on shape of instantiated
		# Numeric arrays
		self._setdims()

		if name:
			self.name = name
		elif fname:
			self.name = "file:%s" % fname
		else:
			self.name = "NumSprite-%d" % NumSprite._count
		NumSprite._count = NumSprite._count + 1

	def _setdims(self):
		(self.w, self.h) = self.alpha.shape
		(self.iw, self.ih) = (self.w, self.h)

		self.ax, self.ay = genaxes(self.w, self.h, inverty=0)
		self.xx, self.yy = genaxes(self.w, self.h, inverty=1)

	def __repr__(self):
		return '<NumSprite "%s"@(%d,%d) %x%x depth=%d>' % \
			   (self.name, self.x, self.y, self.w, self.h, self.depth)

	def clone(self):
		import copy
		new = NumSprite(x=self.x, y=self.y,
						width=self.w,height=self.h,
						dx=self.dx, dy=self.dy, depth=self.depth,
						fb=self.fb, on=self._on, icolor=self.icolor,
						centerorigin=self.centerorigin)
		new.array = copy.copy(self.array)
		new.alpha = copy.copy(self.alpha)
		new._setdims()
		new.name = 'Clone of %s' % self.name
		return new

	def asPhotoImage(self, alpha=None):
		# save handles to prevent garbage collection..
		self.pil_im = self.toPIL()
		self.pim = PIL.ImageTk.PhotoImage(self.pil_im)
		return self.pim

	def set_alpha(self, alpha):
		self.alpha[::] = alpha

	def clear(self, color=(1,1,1)):
		rgba = _C(color)
		for n in range(3):
			self.array[:,:,n] = rgba[n]
		self.alpha[::] = rgba[3]

	def fill(self, color):
		self.clear(color=color)

	def noise(self, thresh=0.5, color=None):
		for n in range(3):
			if color or n == 0:
				m = uniform(1, 255, size=self.array.shape[0:2])
				if not thresh is None:
					m = where(greater(m, thresh*255), 255, 1)
			self.array[:,:,n] = m[::].astype(uint8)

	def circlefill(self, color, r, x=0, y=0, width=0):
		ar = (((self.ax-x)**2)+((self.ay+y)**2))**0.5
		mask = less_equal(ar, r)
		rgba = _C(color)
		for n in range(3):
			self.array[:,:,n] = where(mask, rgba[n], self.array[:,:,n])
		self.alpha[::] = rgba[3]

	def circle(self, color, r, x=0, y=0, width=1):
		ar = abs((((self.ax-x)**2)+((self.ay+y)**2))**0.5 - r)
		mask = less_equal(ar, width)
		rgba = _C(color)
		for n in range(3):
			self.array[:,:,n] = where(mask, rgba[n], self.array[:,:,n])		
		self.alpha[::] = rgba[3]

	def axisflip(self, xaxis, yaxis):
		if xaxis:
			self.array = self.array[::-1,:,:]
			self.alpha = self.alpha[::-1,:]
		if yaxis:
			self.array = self.array[:,::-1,:]
			self.alpha = self.alpha[:,::-1]

	def toPIL(self):
		m = concatenate((self.array, self.alpha[:,:,newaxis]), axis=2)
		m = transpose(m, axes=[1,0,2])
		return Image.fromarray(m, 'RGBA')

	def fromPIL(self, i):
		a = transpose(asarray(i), axes=[1,0,2])
		if a.shape[2] == 3:
			# RGB
			self.array = a[:,:,0:3].astype(uint8)
			self.alpha = zeros(self.array.shape[0:2], uint8)
			self.alpha[::] = 255
		elif a.shape[2] == 4:
			# RGBA
			self.array = a[:,:,0:3].astype(uint8)
			self.alpha = a[:,:,3].astype(uint8)
		else:
			raise Error

	def rotate(self, angle, preserve_size=1, trim=0):
		self.fromPIL(self.toPIL().rotate(-angle, expand=(not preserve_size)))
		self._setdims()

	def rotateCCW(self, angle, preserve_size=1, trim=0):
		self.rotate(angle=-angle, preserve_size=preserve_size, trim=trim)

	def rotateCW(self, angle, preserve_size=1, trim=0):
		self.rotate(angle=angle, preserve_size=preserve_size, trim=trim)

	def scale(self, new_width, new_height):
		self.fromPIL(self.toPIL().resize((new_width, new_height),
										 Image.NEAREST))
		self._setdims()

	def circmask(self, r, x=0, y=0):
		d = (((self.ax-x)**2)+((self.ay+y)**2))**0.5
		mask = where(less(d, r), 1, 0)
		for n in range(3):
			self.array[:,:,n] = self.array[:,:,n] * mask

	def alpha_aperture(self, r, x=0, y=0):
		mask = where(less(((((self.ax-x)**2)+\
							((self.ay+y)**2)))**0.5, r), 255, 0)
		self.alpha[:,:] = mask[:,:].astype(uint8)

	def alpha_gradient(self, r1, r2, x=0, y=0):
		d = 255 - (255 * (((((self.ax-x)**2)+\
							((self.ay+y)**2))**0.5)-r1) / (r2-r1))
		d = where(less(d, 0), 0, where(greater(d, 255), 255, d))
		self.alpha[:,:] = d[:,:].astype(uint8)

	def alpha_gradient2(self, r1, r2, bg, x=0, y=0):
		d = 1.0 - ((hypot(self.ax-x, self.ay+y) - r1) / (r2 - r1))
		alpha = clip(d, 0.0, 1.0)
		bgi = zeros((alpha.shape[0],alpha.shape[1],3))
		try:
			for n in range(len(bg)):
				bgi[:,:,n] = bg[n]
		except TypeError:
			bgi[::] = bg
		for n in range(3):
			self.array[:,:,n] = ((alpha * self.array[:,:,n]).astype(Float) + \
								((1.0-alpha) * bgi[:,:,n])).astype(uint8)
		self.alpha[::] = 255;

	def dim(self, mult, meanval=128.0):
		self.array = meanval + \
					 ((1.0-mult) * (self.array-meanval)).astype(uint8)

	def thresh(self, threshval):
		self.array = where(less(self.array, threshval), \
						   1, 255).astype(uint8)

	def on(self):
		self._on = 1

	def off(self):
		self._on = 0

	def toggle(self):
		self._on = not self._on
		return self._on

	def state(self):
		return self._on

	def moveto(self, x, y):
		self.x = x
		self.y = y

	def rmove(self, dx=0, dy=0):
		self.x = self.x + dx
		self.y = self.y + dy

	def save(self, fname):
		"""Use PIL to save image."""
		self.toPIL().save(fname)

	def fastblit(self):
		self.blit(fast=1)

	def render(self, clear=None):
		m = concatenate((self.array, self.alpha[:,:,newaxis]), axis=2)
		self._rendered = transpose(m, axes=[1,0,2])[::-1,:,:].tostring()

	def blit(self, x=None, y=None, fb=None, flip=None, force=0, fast=None):
		if not force and not self._on:
			return

		if fb is None:
			fb = self.fb
		if fb is None:
			Logger("No fb associated with sprite on blit\n")
			return None

		# use specified position OR saved position
		# and update saved position to actual position.
		self.x = x or self.x
		self.y = y or self.y

		# x,y coords specify destination of sprite CENTER.
		# Convert to FB coords (place (0,0) corner in (0,0)@UL coords)
		scx = fb.hw + self.x - (self.w / 2)
		scy = fb.hh + self.y - (self.h / 2)

		if not fast:
			self.render()
			
		# 24-jan-2006 shinji (was in _pygl_setxy)
		# A trick for the OpenGL position setting to let us blit
		# image even if the part of sprite is outside the screen.
		glRasterPos2i(0,0)
		glBitmap(0, 0, 0, 0, scx, scy, '\0')
		glDrawPixels(self.w, self.h, GL_RGBA, GL_UNSIGNED_BYTE, self._rendered)
		
		if flip:
			fb.flip()

		# if moving sprite, move to next position..
		self.x = self.x + self.dx
		self.y = self.y + self.dy
		return 1

	def setdir(self, angle, vel):
		angle = pi * angle / 180.0
		self.dx = vel * cos(angle)
		self.dy = vel * sin(angle)

	def subimage(self, x, y, w, h, center=None):
		raise Error

	def line(self, x1, y1, x2, y2, color, width=1):
		raise Error

	def rect(self, x, y, w, h, color):
		raise Error

	def rotozoom(self, scale=1.0, angle=0.0):
		raise Error


def testset():
	fb = quickinit(dpy=":0.0", w=512, h=512, bpp=32, fullscreen=0, opengl=1)
	fb.clear((128,128,128))

	if 1:
		N = 200
		for num in [1, 0]:
			start = time.time()
			for n in range(N):
				if num:
					s = NumSprite(x=0, y=0, width=25, height=25, fb=fb)
				else:
					s = Sprite(x=0, y=0, width=25, height=25, fb=fb)
				s.noise(color=1)
				s.scale(100,100)
				s.blit()
				fb.flip()
			stop = time.time()
			print 'num=%d' % num, N/(stop-start), 'fps'

	if 0:
		s = NumSprite(x=0, y=0, fname='testpat.png', fb=fb)
		s.alpha_gradient(100,200)
		#s.save('foo.jpg')
		#s.scale(50,50)
		s.rotateCW(45, preserve_size=0)
		s.blit(flip=1)
		keyboard()

	if 0:
		s = NumSprite(x=0, y=0, width=200, height=100, fb=fb)
		s.fill((128,128,128,255))
		s.array[:,0:30,0]=255
		s.array[:,30:60,1]=255
		s.array[:,60:,2]=255

		s2 = s.clone()
		s2.moveto(-100,-100)

		#s.circmask(25)
		#s.alpha_aperture(25)
		#s.alpha_gradient(25,45)
		s.alpha_gradient2(25,45, (255,0,0))	
		#s.dim(0.50)

		s2.blit(flip=0)
		s.blit(flip=1)
		keyboard()

	if 0:
		s = NumSprite(x=-100, y=-100, width=200, height=200, fb=fb, on=1)
		cosgrat(s, 5, 0, -45)
		alphaGaussian(s, 20)
		s.blit()

		o = Sprite(x=100, y=100, width=200, height=200, fb=fb, on=1)
		cosgrat(o, 5, 90, -45)
		alphaGaussian(o, 20)
		o.blit()
		fb.flip()
		keyboard()

	if 0:
		print 'starting'
		for i in [1, 0]:
			for b in [1, 0]:
				for f in [1, 0]:
					if i:
						s = NumSprite(x=0, y=0, width=200, height=200, fb=fb)
						print 'numsprite', 'blit=%d' % b, 'flip=%d' % f
					else:
						s = Sprite(x=0, y=0, width=200, height=200, fb=fb)
						print 'sprite', 'blit=%d' % b, 'flip=%d' % f
					nf = 100
					phi = 0
					cosgrat(s, 5, phi, 45)
					start = time.time()
					for n in range(nf):
						cosgrat(s, 5, phi, 45)
						alphaGaussian(s, 25)
						if b:
							fb.clear((0,0,0))
							s.blit()
						if f:
							fb.flip()
						phi = (phi + 10) % 360
					stop = time.time()
					print ' ', nf/(stop-start), 'fps'
		keyboard()


if __name__ == '__main__':
	if 0:
		import cProfile,pstats
		f = '/tmp/testset.prof'
		cProfile.run('testset()', f)
		#p = pstats.Stats(f)
		#p.strip_dirs().sort_stats('time').print_stats()

	if 1:
		testset()
