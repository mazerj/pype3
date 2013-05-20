#!/usr/bin/env python
# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""
Thu Dec	 9 09:38:38 2010 mazer

Simple setup.py file for building SWIG interface for dacq module. This
basically links psems.o, dacq.o and the swig-generated dacq_wrap.o
to make _dacq.so, which is a properly compiled python extension that
should have no 32/64 bit problems etc..

"""

from distutils.core import setup, Extension

dacq_module = Extension('_dacq',
						sources=['dacq_wrap.c', 'dacq.c', 'psems.c'],
						)

setup(name		  = 'dacq',
	  version	  = '4.x',
	  author	  = "Jamie Mazer",
	  description = """wrapper for dacq module""",
	  ext_modules = [dacq_module],
	  py_modules  = ["dacq"],
	  )
