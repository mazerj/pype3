# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""Root access tools

This stuff's for accessing the hardware from a running
pype process. Not really for general use.

"""

"""Revision History

- Sat Jul  9 12:48:58 2005 mazer

 - separated from pype.py
"""

import pwd
import os
import sys

def _realuid():
	"""Get real/effective UID.

	Figure out the real or effective user id based on the
	current (inherited) environment. This is part of the
	whole take/drop root access stuff.

	:return: (int) best guess at uid
	"""
	try:
		uid = pwd.getpwnam(os.environ['SUDO_USER'])[2]
	except KeyError:
		uid = pwd.getpwnam(os.environ['USER'])[2]
	return uid

def root_take():
	"""Attempt to gain root access.

	If pype is started suid-root, then this can be used to enable
	root access.

	**this is a dangerous toy; use with caution**

	:return: (boolean) now root?

	"""
	try:
		os.seteuid(0)
		return True
	except OSError:
		return False

def root_drop():
	"""Give of root access.

	This is used to give up root access after the framebuffer
	and DACQ code has been initialized (these typically require
	root acces). Root access is given up by setting the effective
	UID back to the user's original UID.

	:return: (boolean) error releasing root access?

	"""
	try:
		os.seteuid(_realuid())
		return True
	except OSError:
		return False
