#!/usr/bin/env pypenv
# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""
Fri Mar  7 15:38:19 2008 mazer
 - single dump of pypefile record to stdout
"""

import sys, types, string
from pype import *

if __name__ == '__main__':
	if len(sys.argv) < 2 or len(sys.argv) > 3:
		sys.stderr.write('usage: %s pypefile [rec#]\n' % (sys.argv[0],))
		sys.exit(1)
	elif len(sys.argv) == 2:
		n = 0
	else:
		n = int(sys.argv[2])
		
	pf = PypeFile(sys.argv[1], filter=None)
	d = pf.nth(n)
	pf.close()
	if d is None:
		sys.stderr.write('less than %d records in file\n' % (n,))
		sys.exit(1)
		
	d.compute()

	# 2to3: keys returns iterator, not list. need to listify it:
	ks = list(d.params.keys())
	ks.sort()
	sys.stdout.write('PARAMETER TABLE\n')
	sys.stdout.write('------------------------------------\n')
	for k in ks:
		s = "%s" % (d.params[k],)
		if len(s) > 50:
			s = s[1:50] + "..."
		sys.stdout.write('%20s: %s\n' % (k, s))
	sys.stdout.write('\n')
	sys.stdout.write('ENCODE TABLE\n')
	sys.stdout.write('------------------------------------\n')
	t0 = None
	for (t, ev) in d.events:
		if t0 is None:
			sys.stdout.write('%6s %6d ms %s\n' % ('dt', t, ev,))
		else:
			sys.stdout.write('(%4d) %6d ms %s\n' % (t-t0, t, ev,))
		t0 = t
