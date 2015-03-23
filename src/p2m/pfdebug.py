#!/usr/bin/env pypenv
# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""
Open pypefile to specified record and let user poke around.
"""

import sys
from pypedata import PypeFile

from pypedebug import keyboard

n = 1
if len(sys.argv) < 2:
    sys.stderr.write('usage: pfdebug pypefile [recno]\n')
    sys.exit(1)
fname = sys.argv[1]

if len(sys.argv) < 3:
    n = 1
else:
    n = int(sys.argv[2])

pf = PypeFile(fname)
d = pf.nth(n)
sys.stdout.write("record is in `d`...\n")

keyboard()
