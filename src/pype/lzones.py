# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""Pure python/pype landing zone (aka fixwin) implementation.

Not really for public consumption.

Author -- James A. Mazer (mazerj@gmail.com)

"""

import sys
import imp
import math

from pype import *

import filebox

class LandingZone(object):
	"""
	Circular Landing zone detector -- this is sort of like a FixWin,
	but all done in pype (vs comedi_server subproc). A landing
	zone is circular region located at (x,y) with a radius of size
	pixels.  Once the eyes enter the landing zone, a counter is
	started. If the eyes are still in the landing zone after fixtime,
	then it's considered a landing event the .inside() method returns
	one.

	This depends on the .inside() method being in some sort of
	tight loop and called over and over again until something
	happens, otherwise you might miss exit/entry events..

	Eyes must stay inside the zone for fixtime_ms before it's
	considered a fixation insize the zone. Use fixtime_ms=0 if
	you want to accept pass throughs w/o fixations.

	"""

	def __init__(self, x, y, size, fixtime, app):
		self.app = app
		self.icon = None
		self.x, self.y, self.size = x, y, size
		self.size2 = size**2
		self.fixtime = fixtime
		self.entered_at = None

	def __del__(self):
		self.clear()

	def inside(self, t=None, x=None, y=None):
		"""
		If you have multiple landing zones, you can sit in a loop, use
		app.eye_txy() to query time and eye position ONCE, and then apply
		it to multiple landing zones by passing in (x,y) values

		"""
		if t is None:
			(t, x, y) = self.app.eye_txy()
		if ((self.x-x)**2 + (self.y-y)**2) < self.size2:
			if self.entered_at is None:
				self.entered_at = t
			if (t - self.entered_at) >= self.fixtime:
				return 1
			return 0
		else:
			self.entered_at = None
			return 0

	def draw(self, color='grey', dash=None, text=None):
		self.clear()
		self.icon = self.app.udpy.icon(self.x, self.y,
									   2*self.size, 2*self.size*self.vbias,
									   color=color, type=2, dash=dash)

	def clear(self):
		if self.icon:
			self.app.udpy.icon(self.icon)
			self.icon = None

class SectorLandingZone(object):
	"""
	Sector-style Landing zone detector -- landing zone is defined
	as an angular sector of an annular zone around a fixation
	spot (xo, yo). Annular sector runs from inner_pix to outer_pix
	and has an angular subtense of angle_deg +- subtense_deg.

	Eyes must stay inside the zone for fixtime_ms before it's
	considered a fixation insize the zone. Use fixtime_ms=0 if
	you want to accept pass throughs w/o fixations.

	See LandingZone for additional details about usage.

	"""

	def __init__(self, xo, yo,
				 inner_pix, outer_pix, angle_deg, subtense_deg,
				 fixtime_ms, app):
		self.app = app
		self.icon = None
		self.xo, self.yo = xo, yo
		self.inner = inner_pix
		self.outer = outer_pix
		self.angle = math.pi * angle_deg / 180.0
		self.subtense = math.pi * subtense_deg / 180.0
		self.fixtime = fixtime_ms
		self.entered_at = None

	def __del__(self):
		self.clear()

	def inside(self, t=None, x=None, y=None):
		"""
		If you have multiple landing zones, you can sit in a loop, use
		app.eye_txy() to query time and eye position ONCE, and then apply
		it to multiple landing zones by passing in (x,y) values

		"""
		if t is None:
			(t, x, y) = self.app.eye_txy()

		x, y = x - self.xo, y - self.yo
		r = (x**2 + y**2)**0.5
		if (r > self.inner) and (r < self.outer):
			d = abs(math.pi * math.atan2(y, x) - self.angle)
			if d > pi:
				d = (2 * math.pi) - d
			if d < self.subtense:
				# inside sector
				if self.entered_at is None:
					self.entered_at = t
				if (t - self.entered_at) >= self.fixtime:
					return 1
			return 0
		else:
			self.entered_at = None
			return 0

	def draw(self, color='grey', dash=None, text=None):
		x = self.xo + (self.inner+self.outer)/2.0 + math.cos(self.angle)
		y = self.xo + (self.inner+self.outer)/2.0 + math.sin(self.angle)
		self.clear()
		self.icon = self.app.udpy.icon(x, y,
									   self.outer-self.inter,
									   self.outer-self.inter,
									   color=color, type=1, dash=dash)

	def clear(self):
		if self.icon:
			self.app.udpy.icon(self.icon)
			self.icon = None

