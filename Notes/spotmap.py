#!/usr/bin/python
# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-
#pypeinfo; task; owner:mazer; for:all; descr:RF spotmapping

# Tue Jun 24 16:44:46 2008 mazer
#  -- if 'dur' < 0, then pick random duration on each frame between 0-(-dur)ms
#
# Mon Apr 15 12:54:10 EDT 2013 amarino
#  -- fixed negative dur param -- now, each duration is picked independently, allowing multiple durations in one trial.
#
# Tue Apr 16 11:15:54 EDT 2013 amarino
#  -- added 'min_dur' param (useful when picking frame duration from uniform distrib by setting spot_dur to neg value)


import sys
from pype import *
from Tkinter import *
from events import *
import pype_aux

try:
	reload(fixmaster)
except NameError:
	import fixmaster

class Task(fixmaster.Task):
	
	def task_params(self):
		return (
			("spotmap params", None),
			("radius",		"-1",			is_int, "use grid if <=0"),
			("spot_length",	"20",			is_int),
			("spot_width",	"20",			is_int),
			("spot_dir",	"0",			is_float),
			("spot_on",		"(255,255,255)", is_color),
			("spot_off",	"(1,1,1)",		is_color),
			("spot_dur",	"200",			is_int),
			("min_dur",     "1",            is_int),
			("n_x",			"10",			is_int),
			("n_y",			"10",			is_int),
			("fov_avoid",	"0",			is_int),
			)
	
	def pre_start(self, app, P):
		if len(app.udpy.markstack) < 2:
			warn('Spotmap', 'Need at least two points for rectangle!')
			return 0

		if P['radius'] < 1:
			# get bound marks in RETINAL coords
			x1 = float(min(app.udpy.markstack[0][0], app.udpy.markstack[1][0]))
			x2 = float(max(app.udpy.markstack[0][0], app.udpy.markstack[1][0]))
			y1 = float(min(app.udpy.markstack[0][1], app.udpy.markstack[1][1]))
			y2 = float(max(app.udpy.markstack[0][1], app.udpy.markstack[1][1]))
		else:
			x1 = P['x'] - P['radius']
			x2 = P['x'] + P['radius']
			y1 = P['y'] - P['radius']
			y2 = P['y'] + P['radius']

		fx = P['fix_x']
		fy = P['fix_y']
		nx = P['n_x']
		ny = P['n_y']
		dx = float(x2 - x1) / float(nx-1)
		dy = float(y2 - y1) / float(ny-1)

		# s_grid is always in RETINAL coords!
		# this was 'grid', but conflicts with the new eyecal feature in
		# fixmaster, so it's been renamed to s_grid (for 'spotmap_grid').
		#   -- JM 5-oct-2006
		s_grid = []
		markers = []
		for x in frange(x1, x2, dx, inclusive=1):
			for y in frange(y1, y2, dy, inclusive=1):
				xx = int(round(x))
				yy = int(round(y))
				ecc = ((xx**2)+(yy**2))**0.5
				if ecc >= P['fov_avoid']:
					s_grid.append((xx, yy, 0))
					s_grid.append((xx, yy, 1))
					markers.append(app.udpy.icon(xx+fx, yy+fy, 3, 3,
												 color='red'))

		if not ask('Confirm', 'Grid ok?', ('Yes', 'No')) == 0:
			for tag in markers:
				app.udpy.icon(tag)
			return 0

		for tag in markers:
			app.udpy.icon(tag)

		self.s_grid = s_grid
		self.s_gridavail = None
		self.nblocks = -1;
		
		return 1

	def pre_run_trial(self, app, P):
		# calculate exact number and percentage of blocks done..
		x = max(0, self.nblocks)
		if self.s_gridavail is not None:
			x = x + (1.0 - (float(sum(self.s_gridavail)) /
							float(len(self.s_gridavail))))
		app.repinfo('%d trials; %.2f blks done' % (app.query_ntrials(), x))
		
		app.fb.sync(0)
		sl = P['spot_length']
		sw = P['spot_width']
		ori = P['spot_dir']

		# Tue Mar  7 16:26:27 2006 mazer 
		# this code used to correct for the fact that the
		# sprite rotate method rotated in the CW instead
		# of CCW:
		#   dir = P['spot_dir']
		#   ori = (-dir + 90.0)
		#   if ori < 0:
		#	   ori = ori + 360.
		# this is no longer needed, since we're going to
		# call barspriteCCW() from now on; this also involved
		# swaping the w/l arguements, which were backwards..

		if sw <= 0:
			self.spot_on = Sprite(sl * 3, sl * 3, 0, 0,
								  fb=app.fb, depth=99, on=0,
								  name="on", icolor='white')
			if P['spot_on'] == (0,0,0):
				self.spot_on.noise(0.50)
			else:
				self.spot_on.fill(0)
				self.spot_on.circle(color=P['spot_on'], r=sl)
			self.spot_off = Sprite(sl * 3, sl * 3,
								   0, 0, fb=app.fb, depth=99, on=0,
								   name="off", icolor='black')
			if P['spot_off'] == (0,0,0):
				self.spot_off.noise(0.50)
			else:
				self.spot_off.fill((P['bg'], P['bg'], P['bg']))
				self.spot_off.circle(color=P['spot_off'], r=sl)
		else:
			self.spot_on = barspriteCCW(sw, sl, ori, P['spot_on'],
										fb=app.fb, depth=99, on=0)
			self.spot_off = barspriteCCW(sw, sl, ori, P['spot_off'],
										 fb=app.fb, depth=99, on=0)
		self.dlist.add(self.spot_on)
		self.dlist.add(self.spot_off)

		return P

	def post_run_trial(self, app, P):
		del self.spot_on
		del self.spot_off
		return P
	
	def stimulate(self, app, P, timer, duration):
		self.dlist.update()
		app.fb.flip()

		fx = P['fix_x']
		fy = P['fix_y']

		gix = None
		on_at = None
		spot_last = None
		
		sync = None
		spot_dur = None
		while timer.ms() < duration:
			if spot_dur is None:
				if P['spot_dur'] < 0:				
					spot_dur = pype_aux.urand(P['min_dur'], -P['spot_dur'], integer=1)
				else:
					spot_dur = P['spot_dur']
			if on_at is None or (app.ts() - on_at) > spot_dur:
				spot_dur = None
				sync = not sync
				if spot_last is None:
					e = None
					spot_last = 0
				elif spot_last:
					self.spot_on.off()
					self.spot_off.off()
					spot_last = 0
					e = 'spot off'
				else:
					if gix is not None:
						self.s_gridavail[gix] = 0
					if self.s_gridavail is not None:
						gix = pick_one(self.s_grid, self.s_gridavail)
					if gix is None:
						self.s_gridavail = [1] * len(self.s_grid)
						self.nblocks = self.nblocks + 1
						gix = pick_one(self.s_grid, self.s_gridavail)
					(rx, ry, which) = self.s_grid[gix]
					
					# convert fixation relative position to absolute screen:
					x = fx + rx
					y = fy + ry
					if which == 1:
						self.spot_on.moveto(x, y)
						self.spot_on.on()
					elif which == 0:
						self.spot_off.moveto(x, y)
						self.spot_off.on()
					spot_last = 1
					# save the fixation RELATIVE position (ie, retinal coords):
					e = 'spot on %d %d %d' % (rx, ry, which)
				self.dlist.update()
				app.fb.sync(sync)
				app.fb.flip()
				on_at = app.ts()
				# slow:
				app.udpy.display(self.dlist)
				if e:
					app.encode(e)
				app.idlefn(fast=1)
			else:
				app.idlefn()
		
	def post_fixation(self, app):
		# OVERRIDE ME
		# called after fixation break or early bar touch
		# or at the end of a correct fixation etc -- really just
		# for cleaning up the handmap stimuli during ITI..
		pass
		
def main(app):
	t = Task(app)
	app.set_startfn(lambda app,task=t: task.start_run(app))

def cleanup(app):
	pass

if not __name__ == '__main__':
	loadwarn(__name__)
else:
	sys.stderr.write("not a runable program!\n");
	sys.exit(1)
