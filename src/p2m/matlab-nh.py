#!/usr/bin/env python
#
# Thu Mar 11 13:52:31 2010 mazer 
#
# run matlab and consume header for batch jobs.. command line args
# get passed to matlab as usual..
#

import sys, subprocess

args = sys.argv[:]
args[0] = 'matlab'

proc = subprocess.Popen(args, bufsize=0,
                        stdin=None,
                        stderr=None,
                        stdout=subprocess.PIPE)

# note: this reads one char at a time -- slow, but gives real
# time, unbuffered feedback
holdoutput = 1
last3 = ''
while 1:
    c = proc.stdout.read(1)
    if len(c) == 0: break
    if holdoutput:
        last3 = (last3 + c)[-3:]
        if last3 == '>> ':
            holdoutput = 0
    else:
        sys.stdout.write(c)
        sys.stdout.flush()
