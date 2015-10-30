#!/usr/bin/env pypenv
# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

import os, string
from sys import *
from pype import *
from config import *
from pype_aux import *
from sprite import *
import guitools
import optix

# resolution (in units of 0-255)
STEPSIZE=10

class Calibrater():
	def __init__(self):
		self.dtp = optix.Optix()

	def run(self, app, rgb=True, lcd=1, filename=None, validate=False):
		# note: when not in full screen mode, the mouse must be in
		# the framebuffer window for gamma to take effect!
		if rgb:
			masks = ((0,1,1,1), (1,1,0,0), (2,0,1,0), (3,0,0,1),)
		else:
			masks = ((0,1,1,1),)

		if filename is None:
			# save calibration file in current directory
			filename = '%s.gammacal' % app._gethostname()
			if validate:
				filename = 'v-' + filename
			
		if ask('gamma cal', 'Calibrate offsets?', ['Yes', 'No']) == 0:
			ask('gamma cal', 'Place device on opaque surface.', ['Ok'])
			app.idlefn()
			self.dtp.selfcalibrate()

		ask('gamma cal', 'Place device on framebuffer.', ['Ok'])
		app.idlefn()
		
		# save current gamma
		gamma = app.fb.gamma
		try:
			if not validate:
				app.fb.set_gamma(1.0, 1.0, 1.0)
			else:
				warn('Calibrater',
					 'In windowed mode, mouse must stay in window!', wait=1)
				
			outfile = open(filename, 'w')
			outfile.write("%% lcd=%s\n" % lcd)
			outfile.write("%% columns: chan|r|g|b|Y|x|y|\n")
			outfile.write("%% chan=0 for lum; 1-3 for R,G,B\n")

			d = []
			app.con("RGB -> Yxy", color='red')
			for l in range(255, 0, -STEPSIZE):
				for (color,rw,gw,bw) in masks:
					r, g, b = rw*l, gw*l, bw*l
					app.fb.clear(color=(r, g, b))
					app.fb.flip()
					Y, x, y = self.dtp.Yxy()
					row = (color, r, g, b, Y, x, y)
					outfile.write('%d %d %d %d %f %f %f\n' % row)
					outfile.flush()
					d.append(row)
					app.con("%s -> %s" % ((r,g,b), (Y,x,y)))
					print "%s -> %s" % ((r,g,b), (Y,x,y))
			# estimate and save gamma value(s)
			g = estimateGamma(data=np.array(d), plot=True)
			outfile.write("%% gamma: %s\n" % (g,))
			outfile.close()

			# restore old gamma
		finally:
			if not validate:
				app.fb.set_gamma(gamma[0], gamma[1], gamma[2]);
		app.idlefn()
		app.con('gamma(Lrgb): %s' % (g,), color='red')
		return g

def estimateGamma(data=None, calfile=None, plot=False, wait=False):
	"""Fit gamma function to calibration data.

	- data: matrix of calibration results, rows: 0-3 r g b Y x y
	  where 0 indicates luminance sample, 1-3 R,G and B samples
	  respectively

	- calfile: saved calibration file

	- plot: show plot?

	"""
	import numpy as np
	from scipy.optimize import curve_fit

	if plot and not wait:
		import pylab as plt
	else:
		import matplotlib.pyplot as plt

	if data is None:
		data = []
		for l in open(calfile, 'r').readlines():
			if l[0] != '%':
				data.append(map(float, l.split()))
		data = np.array(data)

	c = 'krgb'
	g = []
	p0 = None
	lines = []
	if plot:
		if not wait:
			plt.ion()
		plt.subplot(1,2,1)
		
	for n in range(4):
		if n == 0:
			col = 1
		else:
			col = n
		x = data[np.nonzero(data[:,0] == n),col].squeeze()
		y = data[np.nonzero(data[:,0] == n),4].squeeze()
		if len(x) == 0:
			g.append(None)
		else:
			params, covar = curve_fit(lambda x,alpha,beta,gamma:\
									alpha*(x**gamma)+beta, x, y, p0=p0)
			p0 = params
			g.append(round(params[2], 3))
			if plot:
				xx = np.linspace(min(x),max(x), 100)
				yy = params[0]*(xx**params[2])+params[1]
				l = plt.plot(x, y, c[n]+'o', xx, yy, c[n]+'-')
				lines.append(l[1])
				plt.hold(1)
	if plot:
		plt.hold(0)
		plt.xlabel('computer output [0-255]')
		plt.ylabel('luminance [cd/m^2]')
		plt.legend(lines, map(lambda x:'%s'%x, g), loc=0)
		if calfile:
			plt.title(calfile)

		# plot color gamut
		plt.subplot(1,2,2)
		x = data[:,5].squeeze()
		y = data[:,6].squeeze()
		plt.plot(x, y, 'k.');
		plt.hold(1)
		a = np.nonzero(x == np.max(x))[0]
		b = np.nonzero(y == np.max(y))[0]
		plt.plot([x[a[0]], x[b[0]]], [y[a[0]], y[b[0]]], 'k-')
		a = np.nonzero(x == np.max(x))[0]
		b = np.nonzero(y == np.min(y))[0]
		plt.plot([x[a[0]], x[b[0]]], [y[a[0]], y[b[0]]], 'k-')
		a = np.nonzero(y == np.max(y))[0]
		b = np.nonzero(y == np.min(y))[0]
		plt.plot([x[a[0]], x[b[0]]], [y[a[0]], y[b[0]]], 'k-')
		plt.axis('equal')
		plt.xlabel('CIE x')
		plt.ylabel('CIE y')		   
		plt.title('gamut')
		
	if plot and not wait:
		plt.draw()
	elif plot:
		plt.show()
	return g

def calibrate(app, validate=False):
	try:
		import usb
		Calibrater().run(app, validate=validate)
		app.showtestpat()
	except ImportError:
		app.showtestpat()
		warn(MYNAME(), 'Missing python usb library')
	except optix.OptixMissingDevice:
		app.showtestpat()
		warn(MYNAME(), 'Is DTP94 attached?')
	

if __name__ == '__main__':
	import pylab
	if len(sys.argv) < 2:
		sys.stderr.write('usage: %s calibrationfile\n' % sys.argv[0])
		sys.exit(1)
	print estimateGamma(calfile=sys.argv[1], plot=True, wait=1)
