#!/usr/bin/env python
# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

import sys, os, posixpath
import string

targs = []

for p in sys.argv[1:]:
	# rezip files after this is over?
	rezip_pype = 0
	rezip_p2m = 0
	
	# find pype file and unzip if necessary..
	p0 = p
	if string.find(p, '.gz') >= 0:
		print 'uncompressing: ' + p
		os.system('gunzip ' + p)
		rezip_pype = 1
		p = string.replace(p, '.gz', '')
	elif not posixpath.exists(p):
		p = p + '.gz'
		if posixpath.exists(p):
			print 'uncompressing: ' + p
			os.system('gunzip ' + p)
			rezip_pype = 1
			p = string.replace(p, '.gz', '')
		else:
			sys.stderr.write('missing: %s\n' % p0)
			sys.exit(1)
	

	# find matching p2m file and unzip if necessary..
	p2m = string.replace(p, '.gz', '') + '.p2m'
	if not posixpath.exists(p2m):
		p2m = p2m + '.gz'
		if posixpath.exists(p2m):
			print 'uncompressing ' + p2m
			os.system('gunzip ' + p2m)
			rezip_p2m = 1
			p2m = string.replace(p2m, '.gz', '')
		else:
			p2m = None

	try:
		f = os.popen('matlab -nodisplay -nojvm', 'w')
		if p2m:
			f.write("oldpf=p2mLoad('%s');\n" % p2m);
			f.write("PF=p2m('%s', oldpf);\n" % p);
		else:
			f.write("PF=p2m('%s');\n" % p);
			p2m = p + '.p2m';
		f.write("save('%s', 'PF', '-mat');\n" % p2m);
		f.write("quit\n");
	finally:
		f.close()

	if rezip_pype:
		print 'recompressing: ', p
		os.system('gzip ' + p)
	if rezip_p2m:
		print 'recompressing: ', p2m
		os.system('gzip ' + p2m)
