#!/usr/bin/env pypenv
# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""
Mon Aug 28 16:56:21 2000 mazer
 dump first record info..
"""

import sys, types, string
from Numeric import *
from pype import *
from events import *
from pypedata import *

if __name__ == '__main__':
	try:
		pf = PypeFile(sys.argv[1], filter=None)
	except IndexError:
		sys.stderr.write('usage: showpypefile pypefile [recno]\n')
		sys.exit(1)

	if len(sys.argv) > 2:
		n = int(sys.argv[2])
	else:
		n = 0
	d = pf.nth(n)
	pf.close()
	if d is None:
		sys.stderr.write('error: <%d trial(s) in file\n' % n)
		sys.exit(1)
	d.compute()

	print 70*'-'
	ks = d.params.keys()
	ks.sort()
	n = int(0.5+len(ks)/2.0)
	for ix in range(n):
		k = ks[ix]
		s = "%s" % (d.params[k],)
		if len(s) > 20:
			s = s[1:20] + "..."
		s = "%s: %s" % (k, s)
		s = "%-35s" % s
		print s,

		ix = ix + n
		if ix >= len(ks):
			print
			break
		k = ks[ix]
		s = "%s" % (d.params[k],)
		if len(s) > 20:
			s = s[1:20] + "..."
		s = "%s: %s" % (k, s)
		s = "%-35s" % s
		print s

	print 70*'-'
	print "d.compute() already called!"
	print "d.__dict__.keys() is useful..."
	keyboard()
