#!/usr/bin/env pypenv
# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""
Mon Aug 28 16:56:21 2000 mazer
 dump first record info..
"""

import sys, types, string
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

	ks = d.params.keys()
	ks.sort()
	for k in ks:
        if not k.endswith('_raw_'):
            pval = val = '%s' % (d.params[k],)
            if len(val) > 70:
                pval = val[:70] + '...'
                
            try:
                raw = d.params[k+'_raw_']
                if raw == val:
                    print '%20s: %s' % (k, pval)
                else:
                    print '%20s: %s    {%s}' % (k, pval, raw)
            except KeyError:
                print '%20s: %s' % (k, pval)
