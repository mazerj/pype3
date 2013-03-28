# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""Sprite-based movie classes

These classes provide bare-bones movie classes. Movies are stored as
individual frames in a directory. Each movie directory must contain an
indexfile (defaultname is INDEX) that lists each individual frame
mage file, **in playback order**.

These classes are primarily provided as examples for how to handle
large image sets in pype. There are probably more efficient ways to
anything you might be doing than using these classes unmodified.

**I can't remember what the difference between Movie and Movie2 is..**

Author -- James A. Mazer (james.mazer@yale.edu)

"""

"""Revision History

Mon Jul 16 12:07:03 2001 mazer

- extracted from imview4.py (task file) as a generally useful tool.

- only change at this time was "app" replaced by "fb"

"""

import sys, types, error, math, os, glob, string
from sprite import *
from guitools import *

class Movie(object):
	def __init__(self, fb, idir, bg, x=0, y=0,
				 smooth1=0, smooth2=0, index='INDEX'):
		self.frame = []
		self.seq = []
		self.bg = None

		try:
			f = open(idir+'/'+index)
			lines = f.readlines()
			f.close()

			ix = 0
			for l in lines:
				if l[0] == '%':
					continue
				l = string.split(l)
				fname = idir + '/' + l[0]
				try:
					s = Sprite(x=x, y=y, fb=fb, depth=0, on=0, fname=fname,
							   name="i%d"%ix)
					sys.stderr.write('o')
					sys.stderr.flush()
				except:
					warn('movie:Movie',
						 'bad movie frame: <%s>' % fname, wait=1)
					sys.stderr.write('x')
					sys.stderr.flush()
				r = round(min(s.w, s.h)/2.0)
				if smooth2 > 0:
					r = smooth2
				if smooth1 > 0:
					s.alpha_gradient2(smooth1, r, bg)
				if self.bg is None:
					self.bg = Sprite(x=x, y=y, width=s.w, height=s.h,
									 fb=fb, depth=0, on=0, fname=fname,
									 name="bg")
				self.frame.append(s)
				self.seq.append(l[0])
				ix = ix + 1
			self.length = ix;
			self.index = lines
			sys.stderr.write('\n')
			sys.stderr.flush()
		except IOError:
			sys.stderr.write('warning: %s missing -- using glob\n' % index);
			lines = []
			files = glob.glob(idir+'/*.ppm')
			if len(files) == 0:
				files = glob.glob(idir+'/*.pgm')
			ix = 0
			while ix < len(files):
				s = Sprite(x=x, y=y, fb=fb,
						   depth=0, on=0, fname=files[ix],
						   name="i%d"%ix)
				if self.bg is None:
					self.bg = Sprite(x=x, y=y, width=s.w, height=s.h,
									 fb=fb,
									 depth=0, on=0, fname=files[ix],
									 name="bg")
				r = round(min(s.w, s.h)/2.0)
				if smooth2 > 0:
					r = smooth2
				if smooth1 > 0:
					s.alpha_gradient(smooth1, r)
				self.frame.append(s)
				self.seq.append(files[ix])
				lines.append('%s\t%d\n' % (fname, ix))
				ix = ix + 1
				sys.stderr.write('-')
				sys.stderr.flush()
			self.length = ix;
			self.index = None
			sys.stderr.write('\n')

	def nth_frame(self, n):
		if n < self.length:
			return self.frame[n]
		return None

	def render(self, frag, render=1):
		pass

def _readindex(fb, x, y, idir, index):
	try:
		f = open(idir+'/'+indexfile)
		lines = f.readlines()
		f.close()
	except IOError:
		sys.stderr.write('warning: missing %s -- using glob *.p?m\n' % index);
		lines = glob.glob(idir+'/*.p?m')
		if len(lines) == 0:
			warn('movie:_readindex',
				 'empty movie dir: %s' % idir, wait=1)
			return (None, None)

	nbad = 0;
	framenum = 0
	framelist = [];
	seq = [];
	for l in lines:
		if l[0] == '%':
			continue
		l = string.split(l)
		fname = idir + '/' + l[0]
		try:
			s = Sprite(x=x, y=y, fb=fb, depth=0, on=0,
					   fname=fname, name="i%d" % framenum)
			sys.stderr.write('+')
			sys.stderr.flush()
			framelist.append(s)
			seq.append(l[0])
			framenum = framenum + 1
		except:
			nbad = nbad + 1
			sys.stderr.write('o')
			sys.stderr.flush()
	sys.stderr.write('\n')
	if nbad > 0:
		warn('movie:_readindex',
			 '%d bad movie frames' % nbad, wait=1)
	return (framelist, seq, lines)

class Movie2(object):
	def __init__(self, fb, x, y, idir, bg,
				 smooth1=None, smooth2=None, index='INDEX'):
		# keep framelist around to stop garbage collection of imagedata...
		(framelist, self.seq, self.index) = _readindex(fb, x, y, idir, index)

		self.length = len(framelist)
		self.fb = fb
		self.framelist = []

		fnum = 0
		maxw, maxh = None, None
		for s in framelist:
			if maxw is None or s.w > maxw:
				maxw = s.w
			if maxh is None or s.h > maxh:
				maxh = s.h
			r = round(min(s.w, s.h) / 2.0)
			if smooth2:
				r = smooth2
			if smooth1:
				s.alpha_gradient2(smooth1, r, bg)
			s.render()
			sys.stderr.write('.')
			sys.stderr.flush()

			# make sure to save sprite/image data so it doesn't get
			# garbage collected..
			self.framelist.append(s)

			# pre-calc position for fast-blit
			fnum = fnum + 1

		self.bgframe = Sprite(width=maxw, height=maxh,
							  x=x, y=y, fb=fb, on=0);
		self.bgframe.fill(bg)
		self.bgframe.render()
		sys.stderr.write('\n')


	def blit(self, n):
		if n is None:
			self.bgframe.fastblit()
		elif n < self.length:
			s = self.framelist[n]
			s.fastblit()


if __name__ == '__main__':
	sys.stderr.write('%s does nothing as main.\n' % __name__)
