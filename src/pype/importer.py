# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""Override standard import function for debugging.

Importing this module will override the standard definition of __import__
to print debugging information each time a module gets imported.

"""

"""Revision History
"""

import __builtin__
import sys
import imp
from guitools import Logger

_native_imp =  __builtin__.__import__

def _verbose_import(*args):
	try:
		fp, pathname, description = imp.find_module(args[0])
		if fp is not None:
			fp.close()
			# only report non-python stdlib imports (this isn't
            # really the right way to do it, but is reasonably close)
			if 'python' in pathname:
				Logger("importing '%s' from '%s'\n" % (args[0], pathname))
	except:
		# anything goes wrong, punt on error message and fall back
		# to native import routine..
		pass
	return apply(_native_imp, args)

def importer(report=1):
	if report:
		__builtin__.__import__ = _verbose_import
	else:
		__builtin__.__import__ = _native_imp


