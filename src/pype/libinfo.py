# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""Information about library versions

"""

"""Revision History
Wed Feb	 1 09:41:40 2006 mazer
- Print useful info about installed versions of dependent libraries

"""

import string

def libinfo():
	v = {}
	try:
		import Pmw
		v['pmw'] = Pmw.version()
	except ImportError:
		v['pmw'] = None

	try:
		import PIL.Image
		v['pil'] = PIL.Image.VERSION
	except ImportError:
		v['pil'] = None

	try:
		import numpy
		v['numpy'] = numpy.__version__
	except ImportError:
		v['numpy'] = None

	try:
		import pygame
		v['pygame'] = pygame.ver
		try:
			v['sdl'] = string.join(map(str,pygame.get_sdl_version()), '.')
		except AttributeError:
			v['sdl'] = None
	except ImportError:
		v['pygame'] = None
		v['sdl'] = None

	try:
		import OpenGL
		v['opengl'] = OpenGL.__version__
	except ImportError:
		v['opengl'] = None

	return v

def print_version_info():
	import sys

	v = libinfo()
	for k in v.keys():
		sys.stdout.write("%s\tv%s\n" % (k, v[k],))

if __name__ == '__main__':
	print_version_info()
