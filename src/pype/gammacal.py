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

class Calibrater():
    def __init__(self):
        self.dtp = optix.Optix()

    def run(self, app, rgb=True, lcd=1, filename=None):
        if rgb:
            masks = ((0,1,1,1), (1,1,0,0), (2,0,1,0), (3,0,0,1),)
        else:
            masks = ((0,1,1,1),)

        if filename is None:
            filename = '%s.gammacal' % app._gethostname()
            
        if ask('gamma cal', 'Calibrate offsets?', ['Yes', 'No']) == 0:
            ask('gamma cal', 'Place device on opaque surface.', ['Ok'])
            app.idlefn()
            self.dtp.selfcalibrate()

        ask('gamma cal', 'Place device on framebuffer.', ['Ok'])
        app.idlefn()
        
        # save current gamma
        gamma = app.fb.gamma
        try:
            app.fb.set_gamma(1.0, 1.0, 1.0)
            outfile = open(filename, 'w')
            outfile.write("%% lcd=%s\n" % lcd)
            outfile.write("%% columns: chan|r|g|b|Y|x|y|\n")
            outfile.write("%% chan=0 for lum; 1-3 for R,G,B\n")

            d = []
            app.con("RGB -> Yxy", color='red')
            for l in range(255, 0, -10):
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
            # estimate and save gamma value(s)
            g = estimateGamma(data=np.array(d), plot=False)
            outfile.write("%% gamma: %s\n" % (g,))
            outfile.close()

            # restore old gamma
        finally:
            app.fb.set_gamma(gamma[0], gamma[1], gamma[2]);
        app.idlefn()
        app.con('gamma(Lrgb): %s' % (g,), color='red')
        return g

def estimateGamma(data=None, calfile=None, plot=False):
    """Fit gamma function to calibration data.

    data: matrix of calibration results, each row should be:
                0-3 r g b Y x y
          where 0 indicates luminance sample, 1-3 R,G and B samples
          respectively
    calfile: saved calibration file
    plot: show plot?
    """
    import numpy as np
    from scipy.optimize import curve_fit
    import matplotlib.pyplot as pyplot

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
                l = pyplot.plot(x, y, c[n]+'o', xx, yy, c[n]+'-')
                lines.append(l[1])
                pyplot.hold(1)
    if plot:
        pyplot.hold(0)
        pyplot.xlabel('computer output [0-255]')
        pyplot.ylabel('luminance [cd/m^2]')
        pyplot.legend(lines, map(lambda x:'%s'%x, g), loc=0)
        if calfile:
            pyplot.title(calfile)
    return g

def calibrate(app):
    try:
        import usb
        Calibrater().run(app)
        app.showtestpat()
    except ImportError:
        app.showtestpat()
        warn(MYNAME(), 'Missing python usb library')
    except optix.OptixMissingDevice:
        app.showtestpat()
        warn(MYNAME(), 'Is DTP94 attached?')
    

if __name__ == '__main__':
    print estimateGamma(calfile=sys.argv[1], plot=1)
    import matplotlib.pyplot as pyplot
    pyplot.show()
