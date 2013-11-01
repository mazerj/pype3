#!/usr/bin/python
# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-
#pypeinfo; task; owner:mazer; for:all; descr:basic fixation/handmap task

#
# Tue Apr 19 09:19:00 2011 mazer (actually mattk)
#  - WARNING: because the handmap update function is sync'd to
#    the video refresh signal, all RT data collected using fixation
#    will be quantized at the frame rate. This is not a bug, it's
#    just the way things are.
#

import sys, random, string
from pype import *
from Tkinter import *
from events import *

try:
	reload(fixmaster)
except NameError:
	import fixmaster

try:
	hmap = reload(hmap)
except NameError:
	import handmap as hmap

class Task(fixmaster.Task):

	TaskRev = "$Id: fixation.py 787 2013-07-11 13:32:22Z mazer $"

	def task_params(self):
		return ()

	def pre_start(self, app, P):
		# called before run starts (after file is selected)
		# MUST return 1 or 0
		return 1


	def post_start(self, app, P):
		# OVERRIDE ME
		# called at the end of run to cleanup sprites etc..
		pass

	def stimulate(self, app, P, timer, duration):
		# called duration fixation
		# your function **MUST** yeild control at the end of
		# duration ms. 'timer' is already running!
		try:
			hmap.hmap_show(app)
			while timer.ms() < duration:
				app.idlefn()
		finally:
			# make sure to hide the
			hmap.hmap_hide(app, update=1)


	def post_fixation(self, app):
		# called after fixation break or early bar touch
		# use for cleanup...
		pass

def main(app):
	t = Task(app)
	app.set_startfn(lambda app,task=t: task.start_run(app))
	hmap.hmap_install(app)
	hmap.hmap_set_dlist(app, t.dlist)

def cleanup(app):
	hmap.hmap_set_dlist(app, None)
	hmap.hmap_uninstall(app)

if not __name__ == '__main__':
	loadwarn(__name__)
else:
	sys.stderr.write("not a runable program!\n");
	sys.exit(1)
