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

Tue Aug  8 14:04:36 2006 mazer

- added alphabar() function - generates a bar stimulus from a sprite
  by filling the sprite with the specified color and then setting the
  alpha channel to let the specified bar stimulus show through.

Wed Aug  9 13:15:34 2006 mazer

- Added _unpack_rgb() to make all the stimulus generators use a common
  color specification. And documented all the grating generators.

Fri Jun 13 15:24:57 2008 mazer

- added ppd=, meanlum=, moddepth= and color=  options to sin, cos,
  polar, logpolar and hyper grating functions

Wed Jun 18 13:54:46 2008 mazer

- removed old grating generator functions: Make_2D_XXXX()

Mon Jan  5 14:49:56 2009 mazer

- moved gen{axes,d,rad,theta} axes generator from sprite.py to this
  file (spritetools.py) - gend() function is now officially obsolete..

Fri May 22 15:27:42 2009 mazer

- added simple_rdp() function for Random Dot Patterns

"""

import numpy as np
import pygame.surfarray
from pygame.constants import *

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

def genaxes(w, h=None, typecode=np.float64, inverty=0):
	"""Generate two arrays descripting spirte x- and y-coordinate axes
	(like Matlab MESHGRID).

	*NB* By default the coordinate system is matrix/matlab, which
	means that negative values are at the top of the sprite and
	increase going down the screen. This is fine if all you use the
	function for is to compute eccentricity to shaping envelopes, but
	wrong for most math. Use inverty=1 to get proper world coords..

	:param w, h: scalar values indicating the width and height of the
		sprite in needing axes in pixels

	:param typecode: Numeric-style typecode for the output array

	:param inverty: (boolean) if true, then axes are matlab-style with
		0th row at the top, y increasing in the downward direction

	:return: pair of vectors (xaxis, yaxis) where the dimensions of
		each vector are (w, 1) and (1, h) respectively.

	"""
	if h is None:
		(w, h) = w						# size supplied as pair/tuple
	x = np.arange(0, w) - ((w - 1) / 2.0)
	if inverty:
		y = np.arange(h-1, 0-1, -1) - ((h - 1) / 2.0)
	else:
		y = np.arange(0, h) - ((h - 1) / 2.0)
	return x.astype(typecode)[:,np.newaxis],y.astype(typecode)[np.newaxis,:]

def genrad(w, h=None, typecode=np.float64):
	"""Generate numeric array of distance-from-center values (like
	a circular MESHGRID)

	:param w, h: width and height of sprite (height defaults to width)

	typecode: output type, defaults to Flaot65 ('d')

	:return: 2d matrix of dimension (w, h) containg a map of pixel
		eccentricity values.

	"""
	x, y = genaxes(w, h)
	return np.hypot(x,y).astype(typecode)

def gentheta(w, h=None, typecode=np.float64, degrees=None):
	"""Generate numeric array of polar angle values relative to sprite center
	(like a circular MESHGRID)

	*NB* Be careful, if you request an integer typecode and radians,
	the values will range from -3 to 3 .. not very useful!

	:param w, h: width and height of sprite (height defaults to width)

	:param typecode: output type, defaults to Flaot65 ('d')

	:param degrees: optionally convert to degrees (default is radians)

	:return: 2d matrix of dimension (w, h) containg a map of pixel
		theta values (polar coords). 0deg/0rad is 3:00 position,
		increasing values CCW, decreasing values CW.

	"""
	x, y = genaxes(w, h)
	t = np.arctan2(y, x)
	if degrees:
		t = 180.0 * t / np.pi
	return t.astype(typecode)

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

def singrat2(s, frequency, phase_deg, ori_deg, R=1.0, G=1.0, B=1.0,
			meanlum=0.5, moddepth=1.0, ppd=None, color=None, xcache=None):

	""" See singrat. This returns and caches the coordinate system, which
	    may help speed things up.
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
	if xcache is None or not(xcache.has_key(ori_deg)):
		r = np.hypot(s.xx/s.w, s.yy/s.h)
		t = np.arctan2(s.yy, s.xx)
		t = t - (np.pi * ori_deg) / 180.
		x = r * np.cos(t)
		if(xcache is None):
			xcache = dict()

		xcache[ori_deg] = x
	else: #Or, just use the orientation to decache it
		x=xcache[ori_deg]

	# This stuff still takes about 500ms/fullscreen sprite
	i = moddepth * np.sin((2.0 * np.pi * frequency * x) -
						  (np.pi * phase_deg / 180.0))
	s.array[::] = np.transpose((np.array((R*i,G*i,B*i)) +
								meanlum).astype(np.uint8),
							   axes=[1,2,0])
	return xcache



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

def polargrat(s, cfreq, rfreq, phase_deg, polarity,
			  R=1.0, G=1.0, B=1.0, logpolar=0,
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
		z = (np.log(np.hypot(x,y)) * cfreq) + \
			(np.arctan2(y,x) * rfreq / (2.0 * np.pi))
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

def simple_rdp(s, dir=None, vel=None, fraction=0.25,
			   fgcolor=(255,255,255), bgcolor=(128,128,128), rseed=None):
	"""Random dot pattern (RDP) generator.

	This is really just used by the handmap function -- not particularly
	robust or numerically accurate.

	:return: nothing (works in place)

	"""

	if rseed:
		old_seed = np.random.get_state()
		np.random.set_state(rseed)

	if dir is None:
		for n in range(3):
			if n == 0:
				try:
					m = np.random.uniform(0.0, 1.0, size=(s.w, s.h))
				except TypeError:
					m = np.random.uniform(0.0, 1.0, size=(s.w, s.h))

			mc = np.where(np.greater(m, fraction), bgcolor[n], fgcolor[n])
			s.array[:,:,n] = mc[::].astype(np.uint8)
	else:
		dx = -int(round(vel * np.cos(np.pi * dir / 180.0)))
		dy = int(round(vel * np.sin(np.pi * dir / 180.0)))
		a = s.array[:,:,:]
		a = np.concatenate((a[dx:,:,:],a[:dx,:,:]), axis=0)
		a = np.concatenate((a[:,dy:,:],a[:,:dy,:]), axis=1)
		s.array[:,:,:] = a[::]

	if rseed:
		np.random.set_state(old_seed)


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
	r = genrad(s.w, s.h)
	t = gentheta(s.w, s.h) + (np.pi * ori_deg / 180.0)
	x = r * np.cos(t)
	y = r * np.sin(t)
	s.fill((R,G,B))
	mask = np.where(np.less(abs(x), (bw/2.0)) * np.less(np.abs(y), (bh/2.0)),
					255, 0)
	s.alpha[::] = mask[::].astype(np.uint8)

def alphaGaussian(s, sigma):
	"""Put symmetric Gaussian envelope into sprite's alpha channel.

	*NB* alpha's have peak value of fully visible (255), low end
	depends on sigma

	:param s: (Sprite)

	:param sigma: (pixels) standard deviation

	:return: nothing (works in place)

	"""
	r = np.hypot(s.xx, s.yy)
	i = 255.0 * np.exp(-((r) ** 2) / (2 * sigma**2))
	s.alpha[::] = i[::].astype(np.uint8)

def alphaGaussian2(s, xsigma, ysigma, ori_deg):
	"""Put non-symmetric Gaussian envelope into sprite's alpha channel.

	*NB* alpha's have peak value of fully visible (255), low end
	depends on sigma

	:param s: (Sprite)

	:param xsigma, ysigma: (pixels) standard dev (think of this as the
		Gaussian's generated with ori=0 and then rotated)

	:param ori_deg: (degrees) orientation of Gaussian

	:return: nothing (works in place)

	"""
	r = np.hypot(s.xx, s.yy)
	t = np.arctan2(s.yy, s.xx) - (np.pi * ori_deg) / 180.0
	x, y = (r * np.cos(t), r * np.sin(t))
	i = 255.0 * np.exp(-(x**2) / (2*xsigma**2)) * np.exp(-(y**2) / (2*ysigma**2))
	s.alpha[::] = i[::].astype(np.uint8)

def gaussianEnvelope(s, sigma):
	"""Add Gaussian envelope to sprite.

	Gaussian envelope is inserted into the sprite's alpha channel.

	:param s: (Sprite)

	:param sigma: (pixels) standard deviation.

	:return: nothing (works in place)

	"""
	r = np.hypot(s.xx, s.yy)
	g = np.exp(-((r) ** 2) / (2 * sigma**2)) / np.sqrt(2 * np.pi * sigma**2);

	# note: normalize so sum(g[::]) = 1.0
	gmax = max(np.reshape(g, [multiply.reduce(g.shape), 1]))
	g = np.array(255.0 * g / gmax).astype(np.uint8)
	pygame.surfarray.pixels_alpha(s.im)[::] = g

if __name__ == '__main__':
	sys.stderr.write('%s should never be loaded as main.\n' % __file__)
	sys.exit(1)
