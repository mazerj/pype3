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

    def run(self, app, rgb=False, lcd=1):
        if rbg:
            masks = ((1,0,0), (0,1,0), (0,0,1), (1,1,1),)
        else:
            masks = ((1,1,1),)
            
        if ask('gamma cal', 'Calibrate offsets?', ['Yes', 'No']) == 0:
            ask('gamma cal', 'Place device on opaque surface.', ['Ok'])
            app.idlefn()
            self.dtp.selfcalibrate()

        ask('gamma cal', 'Place device on framebuffer.', ['Ok'])
        app.idlefn()
        
        # save current gamma
        gamma = app.fb.gamma
        app.fb.set_gamma(1.0, 1.0, 1.0)
        outfile = open('foo.gamma', 'w')
        outfile.write("%% lcd=%s\n" % lcd)
        outfile.write("%% columns: |r|g|b|Y|x|y|\n")

        for l in range(255, 0, -10):
            for (rw,gw,bw) in masks:
                r, g, b = rw*l, gw*l, bw*l
                app.fb.clear(color=(r, g, b))
                app.fb.flip()
                (Y, x, y) = self.dtp.Yxy()

                outfile.write('%d %d %d %f %f %f\n' % (r, g, b, Y, x, y))
                outfile.flush()

                sys.stdout.write("%s -> %s\n" % ((r,g,b), (Y,x,y)))
                sys.stdout.flush()

        outfile.close()
        # restore old gamma
        app.fb.set_gamma(gamma[0], gamma[1], gamma[2]);
        app.idlefn()
