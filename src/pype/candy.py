# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""Eye Candy interface

Routines to generate nice pictures on the monkey display to
entertain the animal during breaks etc.

Author -- James A. Mazer (mazerj@gmail.com)

"""

import posixpath
from tkinter import *

import pype
import pype_aux
from sprite import *

def list_():
	return (
		('bounce', _bounce),
		('slides', _slideshow),
		('lines', _lines),
		)

def _startstop(app, start):
	if start:
		for w in app.disable_on_start:
			w.config(state=DISABLED)
		if app.psych:
			app.fb.screen_open()
		app.info()
		app.info('')
		app.info('***********************', color='red')
		app.info('**** CANDY RUNNING ****', color='red')
		app.info('***********************', color='red')
		app.info('')
		app.info(' Select again to stop! ', color='black')
	else:
		if app.taskmodule:
			for w in app.disable_on_start:
				w.config(state=NORMAL)
		app.info()
		if app.psych:
			app.fb.screen_close()

def _bounce(app):
	if app.running or not app.fb:
		return
	elif app._candyon:
		_startstop(app, 0)
		app._candyon = 0
		app.udpy_note('')
		return
	else:
		_startstop(app, 1)
		app._candyon = 1

	x, y, n = 0, 0, 0
	slist = []
	sync = 0
	while app._candyon:
		if n == 0:
			dx = pype_aux.urand(10, 20)
			dy = pype_aux.urand(10, 20)
			sync = not sync
		n = (n + 1) % 50
		c = (int(pype_aux.urand(1, 255)),
			 int(pype_aux.urand(1, 255)),
			 int(pype_aux.urand(1, 255)))
		s = Sprite(20, 20, x, y, fb=app.fb)
		s.fill(color=c)
		slist.append(s)
		app.fb.clear(color=(128,128,128))
		app.udpy.icon()
		for s in slist:
			s.blit()
			app.udpy.icon(s.x,s.y,s.w,s.h)

		app.fb.sync(sync)
		app.fb.flip()
		if len(slist) > 10:
			slist = slist[1:]
		app.idlefn()

		x = x + dx
		y = y + dy
		if (x > (app.fb.w/3)) or (x < -(app.fb.w/3)):
			dx = -dx
			x = x + dx
		if (y > (app.fb.h/3)) or (y < -(app.fb.h/3)):
			dy = -dy
			y = y + dy

	app.udpy.icon()
	for s in slist:
		del s


def _slideshow(app):
	if app.running or not app.fb:
		return
	elif app._candyon:
		_startstop(app, 0)
		app._candyon = 0
		app.udpy_note('')
		return
	else:
		_startstop(app, 1)
	app._candyon = 1

	try:
		f = open(pype.pyperc('candy.lst'), 'r')
		l = f.readlines()
		f.close()
	except IOError:
		warn('candy:_slideshow',
			 'make %s to use this feature.' % pype.pyperc('candy.lst'))
		return

	itag = None
	bg = Sprite(x=0, y=0, fb=app.fb,
				width=app.fb.w, height=app.fb.h)
	if app.sub_common.queryv('show_noise'):
		bg.noise(0.50)

	while app._candyon:
		x = pype_aux.urand(-200,200)
		y = pype_aux.urand(-200,200)
		while 1:
			inum = int(pype_aux.urand(0,len(l)))
			fname = l[inum][:-1]
			if not posixpath.exists(fname):
				continue
			try:
				s = Sprite(fname=fname, fb=app.fb, x=x, y=x)
				if s.w > 10 and s.h > 10:
					break
			except FileNotFoundError:
				print('dud file: %s\n' % fname)
		maxd = 512.0
		if s.w > maxd:
			m = maxd / s.w
			s.scale(int(m * s.w), int(m * s.h))
		elif s.h > maxd:
			m = maxd / s.h
			s.scale(int(m * s.w), int(m * s.h))

		app.fb.clear(color=(1, 1, 1), flip=0)
		bg.blit()
		s.blit()
		app.fb.flip()
		if not itag is None:
			app.udpy.icon(itag)
		itag = app.udpy.icon(x, y, s.w, s.h, color='blue')
		app.idlefn(ms=5000)
		del s
	try:
		del s
	except NameError:
		pass

	app.udpy.icon()

	if not itag is None:
		app.udpy.icon(itag)


def _lines(app):
	if app.running or not app.fb:
		return
	elif app._candyon:
		_startstop(app, 0)
		app.udpy_note('')
		app._candyon = 0
		return
	else:
		_startstop(app, 1)
		app._candyon = 1

	app.fb.clear((1,1,1))
	n = 0
	while app._candyon:
		if n == 0:
			app.fb.clear((1,1,1))
			v = 250*(2*np.random.random(4)-1)
		n = (n + 1) % 100
		v += 15*(2*np.random.random(4)-1.0)
		vv = list(map(int, list(map(round, np.clip(v, -250.0, 250.0)))))
		c = tuple(map(int, 1+254*np.random.random(3)))
		app.fb.line(vv[:2], vv[2:], c, width=3)
		app.fb.flip()
		app.idlefn(ms=16)
