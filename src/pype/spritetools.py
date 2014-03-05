# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""Supplemental sprite functions.

These are mostly generator functions that fill sprites with
useful pixel patterns: gratings of various times, Gaussian
envelopes etc. It extends the basic functionality provided
by the sprite module and most functions work on existing
Sprite objects by modding the underlying image data.

Author -- James A. Mazer (james.mazer@yale.edu)

"""

"""Revision History

Tue Aug 23 11:01:19 2005 mazer

- changed ori in singrat,cosgrat etc, such that 0deg -> vertical; convention
  is that motion to left is 0deg, motion up is 90deg, orientation follow
  along orthogonally. Not sure alphaGaussian2() is correct now!!

Tue Mar 7 09:28:03 2006 mazer

- change noted above was not correct. I changed the arctan2() calls::

	>> t = arctan2(s.yy, s.xx) - (pi * (90-ori_deg)) / 180.0

  to::

	>> t = arctan2(s.yy, s.xx) - (pi * ori_deg) / 180.0

  which should give the correct orientations now. Note that the
  real problem is that these functions have been broken from the
  very beginning, but handmap.py and spotmap.py (which uses the
  sprite rotate method) have corrected for this.

Tue Aug	 8 14:04:36 2006 mazer

- added alphabar() function - generates a bar stimulus from a sprite
  by filling the sprite with the specified color and then setting the
  alpha channel to let the specified bar stimulus show through.

Wed Aug	 9 13:15:34 2006 mazer

- Added _unpack_rgb() to make all the stimulus generators use a common
  color specification. And documented all the grating generators.

Fri Jun 13 15:24:57 2008 mazer

- added ppd=, meanlum=, moddepth= and color=  options to sin, cos,
  polar, logpolar and hyper grating functions

Wed Jun 18 13:54:46 2008 mazer

- removed old grating generator functions: Make_2D_XXXX()

Mon Jan	 5 14:49:56 2009 mazer

- moved gen{axes,d,rad,theta} axes generator from sprite.py to this
  file (spritetools.py) - gend() function is now officially obsolete..

Fri May 22 15:27:42 2009 mazer

- added simple_rdp() function for Random Dot Patterns

"""

import numpy as np
import pygame.surfarray
from pygame.constants import *
import sprite

##########################################################################
# new, faster, clean support functions added 04-mar-2004 JAM .. stop
# using the old versions..
##########################################################################

def unpack_rgb(color, R, G, B):
	# 1. if color is given, assume it's a [0-1] RGB triple as list
	# 2. if R is an array assume it's an [0-255] RGB triple
	# 3. fallback to R, G and B as individual [0-255] RGB values
	# inputs: [0-255]
	# outputs: [0-1.0]

	if color:
		R, G, B = color
	else:
		try:
			R, G, B = np.array(R) / 255.0
		except TypeError:
			pass
		except ValueError:
			pass
	return R, G, B

def g2rgb(a):
	"""Convert an [WxHx1] grayscale image into a [WxHx3] RGB array.

	:param a: (array) monochrome input image

	:return: (array) RGB output image

	"""
	return np.transpose(np.array([a, a, a]), axes=[1,2,0])

def pixelize(a, rgb=None, norm=1):
	"""Convert a floating point array into an np.uint8 array.

	:param a: (array) array to be converted

	:param rgb: if true, then promote from 1 plane to 3 planes using g2rgb

	:param norm: (boolean) if true, scale min-max into range 1-255

	:return: pixelized version of input array; result is suitable for
		assigning to <sprite>.alpha or <sprite>.array.

	"""
	if norm:
		amin = min(ravel(a))
		amax = max(ravel(a))
		a = (1.0 + 254.0 * ((a - amin) / (amax - amin))).astype(np.uint8)
	else:
		a = a.astype(np.uint8)
	if rgb is None:
		return a
	else:
		return g2rgb(a)

def genpolar(w, h=None, typecode=np.float64, degrees=False):
	"""Generate polar axes (like polar meshgrid)

	:param w, h: width and height of sprite (height defaults to width)

	:param typecode: output type, defaults to float64 ('d')

	:param degrees: True/False

	:return: (array) r and theta arrays

	"""
	x, y = sprite.genaxes(w, h, w, h)
	r = np.hypot(x,y).astype(typecode)
	if degrees:
		t = (180.0 * np.arctan2(y, x) / np.pi).astype(typecode)
	else:
		t = np.arctan2(y, x).astype(typecode)
	return r, t

def gray2rgb8(g, inrange=(-1.0, 1.0)):
	"""Convert grayscale image array to 8bit integer array.

	:param g: (numpy array) gray scale image array

	:param inrange: (float pair) min/max values for input image

	:return: (numpy array) uint8 RGB array

	"""

	minval, maxval = inrange
	a = 255.0 * (g - minval) / (maxval - minval)
	return np.transpose(np.array((a,a,a,)).astype(np.uint8), axes=[1,2,0])

def rgb2rgb8(r, g, b, inrange=(-1.0, 1.0)):
	"""Convert rgb image data to 8bit integer array.

	:param r,g,b: (numpy arrays) red, green and blue image planes

	:param inrange: (float pair) min/max values for input image

	:return: (numpy array) uint8 RGB array

	"""

	minval, maxval = inrange
	a = np.array((r, g, b,))
	a = 255.0 * (a - minval) / (maxval - minval)
	return np.transpose(a.astype(np.uint8), axes=[1,2,0])

def singrat(s, frequency, phase_deg, ori_deg, R=1.0, G=1.0, B=1.0,
			meanlum=0.5, moddepth=1.0, ppd=None, color=None):
	"""2D sine grating generator (odd symmetric).

	*NB* Verified frequency is really cycles/sprite JM 17-sep-2006.

	:param s: (Sprite) target sprite

	:param frequency: frequency in cycles/sprite (or cyc/deg, if ppd
		is given)

	:param phase_deg: (degrees) (nb: 0deg phase centers the sine
		function at sprite ctr)

	:param ori_deg: (degrees) grating orientation

	:param R,G,B: (either R is colortriple or R,G,B are 0-1 values)

	:param ppd: (pixels/degree) if specified, then it means that freq
		is being specified in cycles/degree

	:param meanlum: mean (DC) value of grating (0-1); default is 0.5

	:param moddepth: modulation depth (0-1)

	:param color: RGB triple (alternative specification of color vector)

	:return: nothing (works in place)

	"""

	if not ppd is None:
		# c/deg -> c/sprite
		frequency = np.mean([s.w, s.h]) / ppd * frequency
	meanlum = 256.0 * meanlum
	moddepth = 127.0 * moddepth

	R, G, B = unpack_rgb(color, R, G, B)
	r = np.hypot(s.xx/s.w, s.yy/s.h)
	t = np.arctan2(s.yy, s.xx)
	t = t - (np.pi * ori_deg) / 180.
	x, y = (r * np.cos(t), r * np.sin(t))

	i = moddepth * np.sin((2.0 * np.pi * frequency * x) -
						  (np.pi * phase_deg / 180.0))
	s.array[::] = np.transpose((np.array((R*i,G*i,B*i)) +
								meanlum).astype(np.uint8),
								axes=[1,2,0])

def cosgrat(s, frequency, phase_deg, ori_deg, R=1.0, G=1.0, B=1.0,
			meanlum=0.5, moddepth=1.0, ppd=None, color=None):
	"""2D cosine grating generator (even symmetric).

	*NB* Verified frequency is really cycles/sprite JM 17-sep-2006.

	:param s: (Sprite) target sprite

	:param frequency: frequency in cycles/sprite

	:param phase_deg: (degrees) (nb: 0deg phase centers the cosine
		function at sprite ctr)

	:param ori_deg: (degrees) grating orientation

	:param R,G,B: (either R is colortriple or R,G,B are 0-1 values)

	:param ppd: (pixels/degree) if specified, then it means that freq
		is being specified in cycles/degree

	:param meanlum: mean (DC) value of grating (0-1); default is 0.5

	:param moddepth: modulation depth (0-1)

	:param color: RGB triple (alternative specification of color vector)

	:return: nothing (works in place)

	"""
	return singrat(s, frequency, phase_deg - 90.0, ori_deg,
				   R=R, G=G, B=B, meanlum=meanlum, moddepth=moddepth,
				   ppd=ppd, color=color)

def singrat2(s, frequency, phase_deg, ori_deg, R=1.0, G=1.0, B=1.0,
			 meanlum=0.5, moddepth=1.0, ppd=None, color=None, xcache=None):
	"""CACHING version of singrat

	This is identical to singrat(), but will cache the coordinate
	system (based on ori_deg) in a dictionary for fast retrival. This
	can really speed things up when generating a large number of
	gratings that differ only in phase or sf.

	If you don't need caching, don't use this!

	:param xcache: (dict) the actual cache

	:return: (dict) updated cache

	"""

	if not ppd is None:
		# c/deg -> c/sprite
		frequency = np.mean([s.w, s.h]) / ppd * frequency
	meanlum = 256.0 * meanlum
	moddepth = 127.0 * moddepth

	R, G, B = unpack_rgb(color, R, G, B)

	# Generating the coordinate system is about 200ms/sprite. We can
	# cache the orientation used for each one and speed things up
	# considerably. Here's the full calculation:
	if (xcache is None) or (ori_deg not in xcache):
		r = np.hypot(s.xx/s.w, s.yy/s.h)
		t = np.arctan2(s.yy, s.xx)
		t = t - (np.pi * ori_deg) / 180.
		x = r * np.cos(t)
		if xcache is None:
			xcache = dict()
		xcache[ori_deg] = x
	else:
		x = xcache[ori_deg]

	# This stuff still takes about 500ms/fullscreen sprite
	i = moddepth * np.sin((2.0 * np.pi * frequency * x) -
						  (np.pi * phase_deg / 180.0))
	s.array[::] = np.transpose((np.array((R*i,G*i,B*i)) +
								meanlum).astype(np.uint8),
							   axes=[1,2,0])
	return xcache

def cosgrat2(s, frequency, phase_deg, ori_deg, R=1.0, G=1.0, B=1.0,
			 meanlum=0.5, moddepth=1.0, ppd=None, color=None, xcache=None):
	"""CACHING version of cosgrat

	This is identical to cosgrat(), but will cache the coordinate
	system (based on ori_deg) in a dictionary for fast retrival. This
	can really speed things up when generating a large number of
	gratings that differ only in phase or sf.

	If you don't need caching, don't use this!

	:param xcache: (dict) the actual cache

	:return: (dict) updated cache

	"""

	return singrat2(s, frequency, phase_deg - 90.0, ori_deg,
					R=R, G=G, B=B, meanlum=meanlum, moddepth=moddepth,
					ppd=ppd, color=color)

def polargrat(s, cfreq, rfreq, phase_deg, polarity,
			  R=1.0, G=1.0, B=1.0, logpolar=False,
			  meanlum=0.5, moddepth=1.0, ppd=None, color=None):
	"""2D polar (non-Cartesian) grating generator.

	*NB* Verified frequencies are really cycles/sprite JM 17-sep-2006.

	:param s: (Sprite) target sprite

	:param cfreq: concentric frequency (cycles/sprite or cyc/deg - see ppd)

	:param rfreq: concentric frequency (cycles/360deg)

	:param phase_deg: (degrees)

	:param polarity: 0 or 1 -> really just a 180 deg phase shift

	:param R,G,B: (either R is colortriple or R,G,B are 0-1 values)

	:param ppd: (pixels/degree); if specified, then it means that freq
		is being specified in cycles/degree - for cfreq only

	:param meanlum: mean (DC) value of grating (0-1); default is 0.5

	:param moddepth: modulation depth (0-1)

	:param color: RGB triple (alternative specification of color vector)

	"""

	if not ppd is None:
		# c/deg -> c/sprite
		cfreq = np.mean([s.w, s.h]) / ppd * cfreq
	meanlum = 256.0 * meanlum
	moddepth = 127.0 * moddepth

	R, G, B = unpack_rgb(color, R, G, B)
	if polarity < 0:
		polarity = -1.0
	else:
		polarity = 1.0
	x, y = (polarity * s.xx/s.w, s.yy/s.h)

	if logpolar:
		z = (np.log(np.hypot(x,y)) * cfreq) + (np.arctan2(y,x) * rfreq /
											   (2.0 * np.pi))
	else:
		z = (np.hypot(y,x) * cfreq) + (np.arctan2(y,x) * rfreq / (2.0 * np.pi))
	i = moddepth * np.cos((2.0 * np.pi * z) - (np.pi * phase_deg / 180.0))
	s.array[::] = np.transpose((np.array((R*i,G*i,B*i)) +
								meanlum).astype(np.uint8),
							   axes=[1,2,0])

def logpolargrat(s, cfreq, rfreq, phase_deg, polarity,
				 R=1.0, G=1.0, B=1.0,
				 meanlum=0.5, moddepth=1.0, ppd=None, color=None):
	"""2D log polar (non-Cartesian) grating generator

	*NB* Frequencies are in cycles/sprite or cycles/360deg

	*NB* Verified frequenies are really cycles/sprite JM 17-sep-2006.

	:param s: (Sprite) target sprite

	:param cfreq: concentric frequency (cycles/sprite or cycles/deg see ppd)

	:param rfreq: concentric frequency (cycles/360deg)

	:param phase_deg: (degrees)

	:param polarity: 0 or 1 -> really just a 180 deg phase shift

	:param R,G,B: (either R is colortriple or R,G,B are 0-1 values)

	:param ppd: (pixels/degree) if specfied, then it means that freq
		is being specified in cycles/degree

	:param meanlum: meanlum (DC) value of grating (0-1); default is 0.5

	:param moddepth: modulation depth (0-1)

	:param color: RGB triple (alternative specification of color vector)

	:return: nothing (works in place)

	"""
	polargrat(s, cfreq, rfreq, phase_deg, polarity,
			  R=R, G=G, B=B, logpolar=1,
			  meanlum=meanlum, moddepth=moddepth, ppd=ppd)

def hypergrat(s, freq, phase_deg, ori_deg,
			  R=1.0, G=1.0, B=1.0,
			  meanlum=0.5, moddepth=1.0, ppd=None, color=None):
	"""2D hyperbolic (non-Cartesian) grating generator.

	*NB* frequencies are in cycles/sprite or cycles/360deg

	*NB* verified frequencies are really cycles/sprite JM 17-sep-2006

	:param s: (Sprite) target sprite

	:param freq: frequency (cycles/sprite or cyc/deg - see ppd)

	:param phase_deg: (degrees)

	:param ori_deg: (degrees) orientation

	:param R,G,B: (either R is colortriple or R,G,B are 0-1 values)

	:param ppd: (pixels/deg) if specified, then it means that freq is
		being specified in cycles/degreee

	:param meanlum: mean (DC) value of grating (0-1); default is 0.5

	:param moddepth: modulation depth (0-1)

	:param color: RGB triple (alternative specification of color vector)

	:return: nothing (works in place)

	"""
	if not ppd is None:
		# c/deg -> c/sprite
		freq = np.mean([s.w, s.h]) / ppd * freq
	meanlum = 256.0 * meanlum
	moddepth = 127.0 * moddepth

	R, G, B = unpack_rgb(color, R, G, B)
	r = np.hypot(s.xx / s.w, s.yy / s.h)
	t = np.arctan2(s.yy, s.xx) - (np.pi * ori_deg) / 180.0
	x, y = (r * np.cos(t), r * np.sin(t))

	z = np.sqrt(np.fabs((x * freq) ** 2 - (y * freq) ** 2))
	i = moddepth * np.cos((2.0 * np.pi * z) - (np.pi * phase_deg / 180.0))
	s.array[::] = np.transpose((np.array((R*i,G*i,B*i)) +
								meanlum).astype(np.uint8), axes=[1,2,0])


def uniformnoise(s, binary=False,
				 R=1.0, G=1.0, B=1.0, meanlum=0.5, moddepth=1.0, color=None):
	"""Fill sprite with uniform white noise

	:param s: (Sprite) target sprite

	:param binary: (boolean) binary noise? (default=False)

	:param R,G,B: (either R is colortriple or R,G,B are 0-1 values)

	:param meanlum: mean (DC) value of grating (0-1); default is 0.5

	:param moddepth: modulation depth (0-1)

	:param color: RGB triple (alternative specification of color vector)

	:return: nothing (works in place)

	"""


	R, G, B = unpack_rgb(color, R, G, B)
	lmin = meanlum - (modepth/2.0)
	lmax = meanlum + (modepth/2.0)
	i = np.random.uniform(lmin, lmax, size=(s.w, s.h))
	if binary:
		i = np.where(np.less(i, meanlum), lmin, lmax)
	i = (255.0 * i).astype(np.uint8)
	s.array[::] = np.transpose(np.array((R*i,G*i,B*i)), axes=[1,2,0])

def gaussiannoise(s, R=1.0, G=1.0, B=1.0, meanlum=0.5, stddev=1.0, color=None):
	"""Fill sprite with Gaussian white noise

	:param s: (Sprite) target sprite

	:param R,G,B: (either R is colortriple or R,G,B are 0-1 values)

	:param meanlum: mean (DC) value of grating (0-1); default is 0.5

	:param stddev: std of gaussian distribution (0-1)

	:param color: RGB triple (alternative specification of color vector)

	:return: nothing (works in place)

	"""


	R, G, B = unpack_rgb(color, R, G, B)
	i = np.random.normal(meanlum, stddev, size=(s.w, s.h))
	i = (255.0 * i).astype(np.uint8)
	s.array[::] = np.transpose(np.array((R*i,G*i,B*i)), axes=[1,2,0])


def alphabar(s, bw, bh, ori_deg, R=1.0, G=1.0, B=1.0):
	"""Generate a bar into existing sprite using the alpha channel.

	This fills the sprite with 'color' and then puts a [bw x bh] transparent
	bar of the specified orientation in the alpha channel.

	:param s: Sprite()

	:param bw,bh: (pixels) bar width and height

	:param ori_deg: (degrees) bar orientation

	:param R,G,B: (either R is colortriple or R,G,B are 0-1 values)

	:return: nothing (works in place)

	"""
	R, G, B = (np.array(unpack_rgb(None, R, G, B)) * 255.0).astype(np.int)
	r, t = sprite.genpolar(s.w, s.h, degrees=True)
	t += ori_deg
	x = r * np.cos(t)
	y = r * np.sin(t)
	s.fill((R,G,B))
	mask = np.where(np.less(abs(x), (bw/2.0)) * np.less(np.abs(y), (bh/2.0)),
					255, 0)
	s.alpha[::] = mask[::].astype(np.uint8)

def alpha_gaussian(s, xsigma, ysigma=None, ori_deg=0.0):
	"""Generate symmetric and asymmetric Gaussian envelopes
	into the alpha channel.

	*NB* alpha's have peak value of fully visible (255), low end
	depends on sigma

	:param s: (Sprite)

	:param xsigma: (pixels) standard dev (think of this as the
		Gaussian's generated with ori=0 and then rotated)

	:param ysigma: (pixels) if None, then use xsigma (symmatric)

	:param ori_deg: (degrees) orientation of Gaussian

	:return: nothing (works in place)

	"""
	if ysigma is None:
		ysigma = xsigma
	r = np.hypot(s.xx, s.yy)
	t = np.arctan2(s.yy, s.xx) - (np.pi * ori_deg) / 180.0
	x, y = (r * np.cos(t), r * np.sin(t))
	i = 255.0 * np.exp(-(x**2) / (2*xsigma**2)) * np.exp(-(y**2) / (2*ysigma**2))
	s.alpha[::] = i[::].astype(np.uint8)

# Thu Jun 20 13:49:46 2013 mazer -- for backward compatibility
#  alpha_gaussian replaces all of these function with the same
#  calling sequence...
from pypeerrors import obsolete_fn
alphaGaussian = alpha_gaussian
alphaGaussian2 = obsolete_fn
alphaGaussian2 = obsolete_fn
gaussianEnvelope = obsolete_fn


def benchmark(fb):
	import time
	from sprite import Sprite
	s = Sprite(250, 250, 0, 0, fb=fb, on=1)
	s2 = Sprite(250, 250, 0, 0, fb=fb, on=1)
	nmax = 100

	t0 = time.time()
	for n in range(nmax):
		singrat(s, 10, 0.0, n, R=1.0, G=1.0, B=1.0,
				meanlum=0.5, moddepth=1.0)
		s.blit(flip=1)
	time.time()
	print 'all', float(nmax) / (time.time() - t0), 'fps'

	t0 = time.time()
	for n in range(nmax):
		singrat(s, 10, 0.0, n, R=1.0, G=1.0, B=1.0,
				meanlum=0.5, moddepth=1.0)
	time.time()
	print 'compute only', float(nmax) / (time.time() - t0), 'fps'

	s2 = Sprite(250, 250, 0, 0, fb=fb, on=1)
	singrat(s2, 10, 0.0, 0, R=1.0, G=1.0, B=1.0,
			meanlum=0.5, moddepth=1.0)
	foo = s2.array[::]
	bar = s2.array[::]
	t0 = time.time()
	for n in range(nmax):
		foo[::] = bar[::]
		s.blit(flip=1)
	time.time()
	print 'copy+blit', float(nmax) / (time.time() - t0), 'fps'

	t0 = time.time()
	for n in range(nmax):
		s.blit(flip=1)
	time.time()
	print 'blit only', float(nmax) / (time.time() - t0), 'fps'



if __name__ == '__main__':
	sys.stderr.write('%s should never be loaded as main.\n' % __file__)
	sys.exit(1)

