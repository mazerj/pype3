#!/usr/bin/env pypenv
# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""
Tue May 10 10:35:20 2011 mazer
  just count # trials in pypefile
"""

from pype import *
from pypedata import *

def count(fname):
	pf = PypeFile(fname, filter=None)

	recno = 0
	while 1:
		d = pf.nth(recno)
		if d is None:
			break
		recno = recno + 1
	pf.close()
	sys.stdout.write('%d\n' % recno)
		
if __name__ == '__main__':
	if len(sys.argv) < 2:
		sys.stderr.write("Usage: %s pypefile\n" %
						 sys.argv[0])
		sys.exit(1)
		
	count(sys.argv[1])
	sys.exit(0)
