# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""Override standard import function for debugging.

Importing this module will override the standard definition of __import__
to print debugging information each time a module gets imported.

"""

import builtins,sys
import importlib
import guitools

_native_imp = builtins.__import__

def _verbose_import(*args, **kwargs):
	"""Really simple hook for reporting imports.
	"""
	guitools.Logger('importing %s\n' % args[0])
	return _native_imp(*args, **kwargs)	

def buggy_verbose_import(*args, **kwargs):
	try:
		spec = importlib.util.find_spec(args[0])
		if spec and spec.origin and 'python' not in spec.origin:
			# only report non-python stdlib imports (this isn't
			# really the right way to do it, but is reasonably close)
			 guitools.Logger("importing '%s' from '%s'\n" % \
							 (args[0], spec.origin))
	except NameError:
		guitools.Logger("importing '%s' from '??'\n" % \
						(args[0], ))
		# anything goes wrong, punt on error message and fall back
		# to native import routine..
		pass
	return _native_imp(*args, **kwargs)

def importer(report=1):
	if report:
		builtins.__import__ = _verbose_import
	else:
		builtins.__import__ = _native_imp


