# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""pype: python physiology environment

This is the main module for pype.  It gets imported by both data
collection and data analysis programs/tasks.  In general, any
pype-related program or task should probably import this module as
early on as possible.

Author -- James A. Mazer (james.mazer@yale.edu)

"""

"""Revision History

Thu Jun 16 15:20:45 2005 mazer

 - added ben willmore's changes for mac-support

- Thu Jul  7 15:19:43 2005 mazer

 - added support for ':' delimited PYPETASKPATH; all .py files
   in each of the indicated directories will be added to the menu
   bar, with the basename of each directory used as the text in
   the dropdown menu.

Sat Jul	 9 13:03:54 2005 mazer

 - moved the root take/drop stuff to a separate module & cleaned
   up the import structure for this module

 - removed eyegraph/tkplotcanvas stuff, replaced with iplot/grace

Sun Jul 24 15:46:07 2005 mazer

 - added SYNCLEVEL option to set intensity of on for syncpulse

 - added plotskip to rig menu -- if plotskip > 1, then it specifies
   the stride for plotting the eyetraces in the iplot window.

 - added plotall to rig menu to turn off plotting of s0, p0 and
   raster (for speed), if so desired..

 - full task dir and record_file are now shown when you mouse over
   the labels, instead of having long names in the GUI, which screws
   up the widths..

 - mouse-over balloons can be added to any widget using, eg::

	{app|self}.balloon.bind(widget, 'balloon message goes here...')

 - made DEBUG a Config file variable instead of an enviornment
   value (ie, use pypeconfig to add "DEBUG: 1" to enable debugging
   messages).

Sun Jul 24 21:48:44 2005 mazer

 - use fx,fy button deleted -- not needed any longer, it's automatic..

Thu Jul 28 18:40:56 2005 mazer

 - PypeApp.bar_genint() and FixWin.genint() should be thought of
   as allowing bar transitions and fixwin breaks to generate interupts,
   but not allowing pype to received them. When your task is ready to
   actually receive those interupts, you now have to tell pype by
   setting "app.allow_ints = 1" and then unsetting it when you're done.

Sun Aug 28 10:11:09 2005 mazer

- added safe_to_load() method to PypeApp -- there was problem with
  tasks getting loaded before they actually halted -- it's not
  sufficient to just check the running flag -- this get's cleared when
  you hit to the stop button, but it may take some time for the
  current trial to actually terminate and the task to halt.

Wed Aug 31 17:36:25 2005 mazer

- changed safe_to_load() to a state var, instead of method

Sat Sep	 2 ??:??:?? 2005 mazer

- removed safe_to_load and just disabled the load options in the
  main file menu..

Sat Sep	 3 16:59:49 2005 mazer

- Changed the whole FixBreak/BarTransition interupt handling scheme
  so that the actual interrupt handler only sets a flag indicating
  that an interupt occured. The next time app.idlefn() is called
  the appropriate exception will get raised. This shouldn't really
  have much of an affect on tasks, so long as they call idlefn()
  or idlefn(fast=1) regularly. However, it should prevent FixBreak
  and BarTransition exceptions from getting raised while the Tkinter
  handlers are running (which locks up parts of the pype gui).

Sat Nov	 5 20:01:02 2005 mazer

- got rid of heatbeat code.. who uses this?? also cleaned up the
  eyelink interface a bit to make it simpler and easier to understand

Thu Nov 10 15:35:13 2005 mazer

- modified PypeApp.encode() to optionally take tuple and encode each
  item of the tuple with the same timestamp.

Mon Jan 16 11:18:57 2006 mazer

- added marktime() method for debugging --> hitting '=' in userdpy
  window sticks a MARK event into the encode stream, if running..

Mon Jan 23 10:11:46 2006 mazer

- added vbias option to FixWin to turn the fixwin into an ellipse. See
  comments in the fixwin class for more details.

Thu Mar 23 11:45:11 2006 mazer

- changed candy1/candy2 -> bounce/slideshow and added rig parameter
  to disable the noise background during slideshows..

Thu Mar 30 10:18:18 2006 mazer

- deleted framebuffer arg to PypeApp() and added psych arg

Tue Apr	 4 11:47:37 2006 mazer

- added arguments to eyeset() to allow tasks to muck with the
  xgain,ygain,xoffset and yoffset values

Fri Apr 14 09:21:34 2006 mazer

- added LandingZone class -- see notes in class definition

Mon Apr 17 09:32:06 2006 mazer

- added SectorLandingZone and PypeApp method eye_txy() to
  query time, x and y position of last eye position sample.
  This is just like the eyepos() method, but also returns
  the sample time.

Tue Apr 25 14:13:14 2006 mazer

- set things up so environment var $(PYPERC) can override the default
  ~/.pyperc config files. This is for when multiple users want to share
  a common .pyperc directory for a single animal.

Mon May	 1 11:10:29 2006 mazer

- check permission on the config directory 1st thing when pype is
  fired up and exit if you don't have write access to save state.
  Again, this is really for shared config/pyperc dirs

Mon May 22 10:24:25 2006 mazer

- added train start button that writes to a "0000" datafile.

- added tally tab on notebook and started maintaining tallys
  across sessions and on a per-task basis. You can clear
  these with a button or programmatically using app.tally().
  Note that a lot of tasks have a app.clear(clear=1) at the
  start of each run, which will defeat this mechanism...

Thu Sep 28 10:16:02 2006 mazer

- 'final' modification to the runstats() code... the current system
  should be simple for most people. There are now three termination
  parameters:

  - max_trials -- maximum number of trials to run before stopping.
	only correct and error trials count.

  - max_correct -- maximum number of CORRECT trials to run before stopping.

  - max_ui -- maximum number of SEQUENTIAL ui trials before stopping.

  - uimax -- still exists and all the associated code, but this is
	really used only by the task -- user's responsible for coding
	up the handler. the max_* parameters are handled directly by
	pype and the run is terminated automatically when the stopping
	conditions are met.

  In all cases, setting these values to zero means they won't be used.
  Either max_trials should be set OR max_correct, but not both!

Mon Dec	 4 09:26:10 2006 mazer

- added set_alarm() method -- this provides a mechanism to generate
  an alarm signal after a fixed # of ms. Use in conjunction with
  app.allow_ints (must be true to alarm to get raised). When the
  alarm goes off an 'Alarm' exception is raised the next time idlefn()
  gets called, just like Bar events::

	usage: app.set_alarm(ms=##) or app.set_alarm(clear=1)

Tue Apr	 3 10:41:33 2007 mazer

- Added support for setting "EYETRACKERDEV: NONE" in config file to
  disable eyetracking in the comedi/das server. This is really to free
  up analog channels 0 and 1 for other things (ie, acute data)

Mon May 21 10:28:23 2007 mazer

- Added 'acute' parameter to the sub_common worksheet for experiments
  going in collaboration with the mccormick lab. Note that this is in
  a worksheet, instead of the Config file so that it's easy for tasks to
  be conditionalize based on the current setting!

Sun May 27 15:08:51 2007 mazer

- Added 'save_tmp' to sub_common worksheet -- this will let you write
  the temp files to /dev/null, which should massively accelerate
  handmappng with the acutes (long trials)

Wed Jun 27 11:01:12 2007 mazer

- Moved all the default Config.$HOST stuff to configvars.py; this should
  make it easier to keep track of the options and defaults for users.

Thu Jun 28 10:40:41 2007 mazer

- Converted almost everything over to using Logger() class for logging
  error message. This will put things in a scrollable console window,
  (if available) and also log to sys.stderr. The Logger class is in
  guitools.py

Wed Jul 18 08:20:22 2007 mazer

- Getting rid of the "train" button in favor a per animal "training"
  variable in the animal worksheet.

Mon Sep 10 15:48:27 2007 mazer

- loadwarn() was not correctly finding the source of the module
  based on filename (aka __file__). It turns out this isn't really
  possible, since tasks get loaded using an explicit combination
  of (dir,file). This means that the actual source of 'file' may
  NOT be the first one on the path, so loadwarn() was failing (ie,
  it always reported the 1st module named 'file' on the path).

Thu Sep 27 17:16:55 2007 mazer

- adding TDT support:

  - plexstate -> record_led (LED)

  - plexon_state() -> record_state()

Tue Dec 11 16:20:50 2007 mazer

- got rid of synctest() built in -- never used and problematic..

Mon Oct 27 12:57:50 2008 mazer

- added TOD_START and TOD_STOP events to store real time-of-day
  for these events to facilitate sync-checking in future

Mon Jan 26 13:44:01 2009 mazer

- added KEYBAR option for config file to allow leftshift key to
  generate BarTransition interupts like a regular bar input.. Mouse
  must be the display window!

Tue Jan 27 12:18:09 2009 mazer

- cleaned and simplified up audio initialization procedure

Fri Mar 13 16:25:24 2009 mazer

- clean up of code, function names (privatizing stuff) and docs

- removed the gui=1 arg for pype -- this is NEVER used..

Fri Mar 27 17:50:18 2009 mazer

- moved eye candy routines (bounce & slideshow) into separate module.

Tue Mar 31 12:48:08 2009 mazer

- new test pattern! automatically scaled to fit the display buffer

- added TESTPAT config-file option for user/rig-specific test pattern

Mon Apr 27 16:20:55 2009 mazer

- removed KEYBAR stuff. This was slightly problematic/deceptive -- it
  depended on calling idlefn() at the right times and the timing is
  completely deceptive.. if you want to debug plug in a joystick or
  joypad and do it the right way..

- likewise, also got rid of the lshiftsown/rshiftdown PypeApp methods

Mon May 25 17:02:17 2009 mazer

- settled on TASKPATH for adding things to the task search path. Again,
  this is a colon-deliminate list of directories. Each directory name
  (terminal node of path) must be unique!! (This is a PMW/Tkinter issue).
  You can specified as both a config var in ~/.pyperrc AND/OR using the
  enviornment var..

Thu Jun 25 16:01:42 2009 mazer

- changed 'dropvar' to really specify VARIANCE instead of STD!!

- got rid of trial_XXX functions and trialstats{}

Tue Jul	 7 10:25:03 2009 mazer

- got rid of BLOCKED -- automatically computed from sync info..

Thu Jan	 7 17:31:33 2010 mazer

- added explicit typeing for c0,c1..cN numeric arrays so they
  get properly saved/pickled by labeled_load.

- At the same time changed s0 (ttl spike channel) and p0 (photo diode
  channel) to be a list (should have been all along) to avoid problems
  in the future.

Mon Oct 11 17:26:32 2010 mazer

- eyebuf_t is now in US, now MS

Fri Oct 15 13:20:53 2010 mazer

- variety of changes to support the new command-line interface (vs.
  magic env vars) to comedi_server and the dacq() function

Tue Dec 21 17:03:11 2010 mazer

- removed iplot/grace dependencies in favor of matplotlib

Wed Apr 27 12:35:40 2011 mazer

- Affine calibration added -- eye cal has been completely
  revamped. Affine cal is performed first and then gain/offset.
  This allows for full affine PLUS on-the-fly offset corrections
  with F8..

- This required major reorganization of the GUI/eyeset interface.
  It's now much simpler, but it means that the pypestate.$HOST
  file is obsolete, so facility for automatic upgrade has been
  added. And the tally is now stored in it's own separate file.

Fri Aug 26 16:48:29 2011 mazer

- got rid of cmask for saving analog data.. basically the photo
  and spike data always get saved, exactly once. You can opt to
  save the raw uncalibrated eye data by setting 'save_raweye' in
  the rig param table, otherwise, no additional analog data will
  get saved..

Mon Jul 29 13:10:55 2013 mazer

- bye-bye record_led

"""

#####################################################################
#  external python dependencies
#####################################################################
import sys
import os
import posixpath
import posix
import time
import thread
import string
import re
import socket
import glob
import cPickle
import math
import numpy as np

# THIS IS REALLY UGLY -- THERE ARE TWO ISSUES:
#  1. matplotlib-0.9.9 uses some sort of cache file that's not compatible
#	  with later versions.
#  2. you don't want to initialize matplotlib as root -- doesn't work, so
#	  we need to drop root access and restore after init
#
euid = None
try:
	euid = os.geteuid()
	if euid == 0:
		os.seteuid(os.getuid())
	import matplotlib
	matplotlib.use('TkAgg')
	# force matplotlib to use a version-specific config file, otherwise
	# incompatiblities between cache files (0.9.9 vs 1.1.1) will cause
	# problems (ie, different ubuntu versions)
	os.environ['MPLCONFIGDIR'] = '%s-%s' % (matplotlib.get_configdir(),
											matplotlib.__version__)
	# make sure this dir exists (really only for 0.9.9..)
	try:
		os.mkdir(os.environ['MPLCONFIGDIR'])
	except OSError:
		pass
finally:
	if not euid is None:
		os.seteuid(euid)
	del euid

from types import *
from Tkinter import *
from Pmw import *

#####################################################################
#  pype internal modules
#####################################################################
from pypedebug import *
from rootperm import *
from pype_aux import *
from ptable import *
from beep import *
from sprite import *
from spritetools import *
from events import *
from guitools import *
from dacq import *
from pypeerrors import *
from pypedata import *

import pypeversion

import prand
prand.validate(exit=True)

def _pype_std_params():
	common = (
		ptitle('Session Data'),
		pyesno('warningbeeps', 0,
			   'use auditory cues for start/stop run?'),
		pslot('subject', '', is_any,
			  'subject id (prefix/partial)'),
		pslot('full_subject', '', is_any,
			  'full (unique) subject name'),
		pslot('owner', '', is_any,
			  'datafile owner'),
		pslot('cell', '', is_any,
			  'unique (per subj) cell id #'),
		pyesno('acute', 0,
			  'acute experiment'),
		pyesno('save_tmp', 1,
			  '0 to write to /dev/null'),
		pyesno('fast_tmp', 1,
			  'super fast tmp mode'),

		ptitle('Fixation Window Params'),	# global, but handled by task
		pslot('win_size', '50', is_int,
			  'fixwin radius (pix)'),
		pslot('win_scale', '0.0', is_float,
			  'additive ecc. adj for win_size (rad-pixels/ecc-pixels)'),
		pslot('vbias',	'1.0', is_float,
			  'fixwin vertical elongation factor (1.0=none)'),

		ptitle('Recording Info'),
		pslot('site.well', '',	is_any,
			  'well number'),
		pslot('site.probe', '', is_any,
			  'probe location'),
		pslot('site.depth', '', is_any,
			  'electrode depth (um)'),

		ptitle('Reward Params'),
		pslot('dropsize', '100', is_int,
			  'mean drop size in ms (for continuous flow systems)'),
		pslot('mldropsize', '0', is_float,
			  'estimated dropsize in ml (user enters!)'),
		pslot('dropvar', '10', is_int,
			  'reward variance (sigma^2)'),
		pslot('maxreward', '500', is_gteq_zero,
			  'maximum reward duration (hard limit)'),
		pslot('minreward', '0', is_gteq_zero,
			  'minimum reward duration (hard limit)'),

		ptitle('Pype Blocking Params'),		# global, but handled by pype itself
		pslot('max_trials', '0', is_int,
			  'trials before stopping (0 for no limit)'),
		pslot('max_correct', '0', is_int,
			  'correct trials before stopping (0 for no limit)'),
		pslot('max_ui', '0', is_int,
			  'sequential UIs before stopping (0 for no limit)'),

		ptitle('Fixspot/Screen Appearance'),
		pslot('fix_size', '2', is_int,
			  'fixspot radius (pix)'),
		pslot('fix_ring', '10', is_int,
			  'blank zone radius around fixspot (pix)'),
		pslot('fix_x', '0', is_int,
			  'default X pos of fixspot (pix)'),
		pslot('fix_y', '0', is_int,
			  'default Y pos of fixspot (pix)'),
		pslot('bg', '(128,128,128)', is_color,
			  'default screen background'),

		ptitle('Timing Params'),
		pslot('minrt', '0', is_int,
			  'minimum allowed manual RT (ms; 0 for none)'),
		pslot('maxrt', '600', is_int,
			  'maximum allowed manual RT (ms)'),
		pslot('iti', '4000+-20%', is_iparam,
			  'inter-trial interval (ms)'),
		pslot('timeout', '10000+-20%', is_iparam,
			  'penalty timeout for errors (ms)'),
		pslot('uitimeout', '20000+-20%', is_iparam,
			  'uninitiated trial timeout (ms)'),

		ptitle('Eye Candy Params'),
		pyesno('show_noise', 1,
			  'noise background during slides'),
		)

	rig = (
		ptitle('DACQ Params'),
		pslot('fixbreak_tau', '5', is_int,
			  '# samples before fixbreak counts;'
			  ' press EyeTracker:UPDATE to take effect'),
		pslot('eye_smooth', '3', is_int,
			  'smoothing length (DACQ ticks aka ms);'
			  ' press EyeTracker:UPDATE to take effect'),
		pslot('dacq_pri', '-10', is_int,
			  'priority of DACQ process pslot (<0 higher)'),
		pyesno('rt_sched', 0,
			  'try to use real time (rt) scheduler'),
		pslot('fb_pri', '-10', is_int,
			  'priority of the framebuffer process pslot (<0 higher)'),
		pslot('photo_thresh', '500',	is_int,
			  'threshold for photodiode detection'),
		pslot('photo_polarity', '1', is_int,
			  'sign of threshold for photodiode detection'),
		pslot('spike_thresh', '500', is_int,
			  'threshold for spike detection'),
		pslot('spike_polarity', '1', is_int,
			  'sign of threshold for spike detection'),
		pyesno('save_raweye', 1,
			   'save raw eye position data?'),

		ptitle('Monitor (read-only: set in Config file)'),
		pslot_ro('mon_id', '', is_any,
				 'monitor id string'),
		pslot_ro('viewdist', '0', is_float,
				 'viewing distance (cm)'),
		pslot_ro('mon_width', '0', is_float,
				 'monitor width (cm)'),
		pslot_ro('mon_height', '0', is_float,
				 'monitor height (cm)'),
		pslot_ro('mon_dpyw', '0', is_int,
				 'monitor width (pix)'),
		pslot_ro('mon_dpyh', '0', is_int,
				 'monitor height (pix)'),
		pslot_ro('mon_h_ppd', '0', is_float,
				 'horizontal pixels_per_deg'),
		pslot_ro('mon_v_ppd', '0', is_float,
				 'vertical pixels_per_deg'),
		pslot_ro('mon_ppd', '0', is_float,
				 'overall/mean pixels_per_deg'),
		pslot_ro('mon_fps', '0', is_float,
				 'monitor frame rate (verified)'),

		ptitle('Eye Tracker Info (Config file or automatic)'),
		pslot_ro('eyetracker', '', is_any,
				 'set Config::EYETRACKER -- tracker device'),
		pslot_ro('eyefreq', '', is_int,
				 'set Config::EYEFREQ -- tracker sampling frequency'),
		pslot_ro('eyelag', '0', is_int,
				 'eye tracker lag (if any -- set automatically)'),

		ptitle('Internal Only -- don\'t change'),
		pslot_ro('note_x', '0', is_int, 'userdpy'),
		pslot_ro('note_y', '0', is_int, 'userdpy'),
		)

	ical = (
		ptitle('Tracker Cal'),
		pslot('affinem_', '1,0,0,0,1,0,0,0,1', is_any, 'matrix'),
		pslot('xgain_', '1.0', is_float, 'mult scale'),
		pslot('ygain_', '1.0', is_float, 'mult scale'),
		pslot('xoff_', '0', is_int, 'pixels'),
		pslot('yoff_', '0', is_int, 'pixels'),
		pslot('rot_', '0', is_float, 'degrees'),
		)
	return (common, rig, ical)

def addicon(app, button, file):
	from PIL import Image, ImageTk
	p = ImageTk.PhotoImage(Image.open(os.path.join(app.pypedir,'lib', file)))
	button._image = p
	button.config(image=button._image)

class PypeApp(object):					# !SINGLETON CLASS!
	"""Pype Application Class.

	Toplevel class for all pype programs -- one instance of this
	class is instantiated when the pype control gui is loaded. More
	than one of these per system is a fatal error.

	The PypeApp class has methods & instance variables for just about
	everything a user would want to do.

	"""
	_instance = None

	def __new__(cls, *args, **kwargs):
		"""This ensure a single instantation.
		"""
		if cls._instance is None:
			cls._instance = super(PypeApp, cls).__new__(cls)
			cls._init = 1
		else:
			cls._init = 0
		return cls._instance

	def __init__(self, pypedir=None, psych=None, training=None, nogeo=None):
		"""Initialize a PypeApp instance, with side effects:

		- FrameBuffer instance is created, which means the hardware
		  screen will be opened automatically.	Right now, PypeApp
		  guesses about the size & depth of the display to simplify
		  things for the user.	This could change.

		- The DACQ hardware is opened, if possible.

		- PypeApp gui is built and opened on screen

		Don't initialize more than one instance of this class.	If you
		do an exception will be raised.	 An alternative (for later
		consideration) would be to allow multiple instances which share
		an underlying framebuffer & dacq hardware; however, this would
		really require some sort of underlying locking method to prevent
		collision.

		"""
		# from python stdlib:
		import signal

		# from pype libraries:
		import PlexNet, pype2tdt, tdt, candy, userdpy, configvars

		if not PypeApp._init:
			return

		self.pypedir = pypedir
		self.psych = psych
		self.training = training

		# no console window to start with..
		self.conwin = None

		# get uid for current EFFECTIVE user id -- at this point it
		# should be the user, not root..
		self.uname = pwd.getpwuid(os.getuid())[0]

		# Load user/host-specific config data and set appropriate
		# defaults for missing values.

		cfile = _hostconfigfile()
		if not posixpath.exists(cfile):
			Logger("pype: making new host config file '%s'\n" % cfile)
			configvars.mkconfig(cfile)

		self.config = configvars.defaults(cfile)
		Logger("pype: config loaded from '%s'\n" % cfile)

		try:
			root_take()
			self.init_dacq()
		finally:
			root_drop()

		if self.psych is None:
			self.psych = self.config.iget('PSYCH', 0)

		if self.psych:
			Logger("pype: psych mode")

		# FULLSCREEN's really shouldn't be used for anything except
		# dedicated xserver's for physiology. The following tried
		# to prevent you from locking up a single-headed machine
		# by starting in fullscreen mode:
		if (self.config.iget('FULLSCREEN') and
			   self.config.get('SDLDPY') == os.environ['DISPLAY']):
			self.config.set('FULLSCREEN', '0', override=1)
			Logger("pype: FULLSCREEN ignored -- single display mode")

		# you can set debug mode by:
		#	- running with --debug argument
		#	- setenv PYPEDEBUG=1
		#	- setting DEBUG: 1 in the Config.$HOST file
		if 'PYPEDEBUG' in os.environ:
			self.config.set('DEBUG', '1', override=1)

		debug(self.config.iget('DEBUG'))
		if debug():
			Logger("pype: running in debug mode")
			sys.stderr.write('config settings:\n')
			self.config.show(sys.stderr)

		# these MUST be set from now on..
		monw = self.config.fget('MONW', -1)
		monh = self.config.fget('MONH', -1)
		viewdist = self.config.fget('VIEWDIST', -1)
		self.config.set('MON_ID', 'notset')
		if sys.platform == 'darwin':
			self.config.set('AUDIODRIVER', 'sndmgr')

		if monw < 0 or monh < 0 or viewdist < 0:
			Logger('pype: set MONW, MONW & VIEWDIST in %s\n' % cfile)
			raise PypeStartupError

		self.tallycount = {}
		state = self._loadstate()

		self.terminate = 0
		self.running = 0
		self._startfn = None
		self._updatefn = None
		self._validatefn = None
		self.dropcount = 0
		self.record_id = 1
		self.record_buffer = []
		self.record_file = None
		self._last_eyepos = 0
		self._allowabort = 0
		self._rewardlock = thread.allocate_lock()
		self._eye_x = 0
		self._eye_y = 0
		self._eyetarg_x = 0
		self._eyetarg_y = 0
		self._eyetrace = 0
		self.taskidle = None

		if nogeo:
			self.setgeo(loadempty=1)
		else:
			self.setgeo(load=1)

		self.tk = Pmw.initialise(useTkOptionDb=1)
		self.tk.resizable(0, 0)
		self.tk.title('pype')
		self.tk.protocol("WM_DELETE_WINDOW", self._shutdown)
		self.setgeo(self.tk, default='+20+20', posonly=1)

		if self.config.iget('SPLASH'):
			self.about(1000)

		self.conwin = ConsoleWindow()
		self.conwin.showhide()

		# setup global log/console window (see guitools.py)
		# all queued (ie, old) Logger messages will get pushed
		# into the console window are this point..
		Logger(window=self.conwin)

		if self.config.iget('ONE_WINDOW'):
			leftpane = Frame(self.tk)
			leftpane.pack(side=LEFT, anchor=NW)
			rightpane = Frame(self.tk, border=3, relief=GROOVE)
			rightpane.pack(side=RIGHT, padx=10, anchor=CENTER)
		else:
			leftpane = Frame(self.tk)
			leftpane.pack(side=LEFT, anchor=NW)
			rightpane = None

		f1 = Frame(leftpane, borderwidth=1, relief=GROOVE)
		f1.pack(expand=0, fill=X)

		self.balloon = Pmw.Balloon(self.tk, master=1, relmouse='both')

		self._show_eyetrace_start = None
		self._show_eyetrace_stop = None
		self._show_eyetrace = IntVar()
		self._show_eyetrace.set(0)
		self._eyetrace_window = None
		self._show_xt_traces = IntVar()
		self._show_xt_traces.set(0)

		mb = Pmw.MenuBar(f1)

		mb.pack(side=LEFT, expand=0)

		mb.addmenu('File', '', '')
		mb.addmenuitem('File', 'command', label='Save state',
					   command=self._savestate)
		mb.addmenuitem('File', 'separator')
		if not self.config.iget('FULLSCREEN'):
			mb.addmenuitem('File', 'command', label='show display',
						   command=lambda s=self: s.fb.screen_open())
			mb.addmenuitem('File', 'command', label='hide display',
						   command=lambda s=self: s.fb.screen_close())
			mb.addmenuitem('File', 'separator')
		mb.addmenuitem('File', 'command', label='Show/hide log',
					   command=self.conwin.showhide)
		mb.addmenuitem('File', 'command', label='Keyboard',
					   command=self.keyboard)
		mb.addmenuitem('File', 'command', label='Remote Debug',
					   command=remotedebug)
		mb.addmenuitem('File', 'command', label='Record Movie',
					   command=lambda s=self: s.fb.recordtog())
		mb.addmenuitem('File', 'separator')
		mb.addmenuitem('File', 'command', label='Quit',
					   command=self._shutdown)

		mb.addmenuitem('File', 'command', label='benchmark',
					   command=lambda s=self: benchmark(s.fb))


		mb.addmenu('Misc', '', '')
		mb.addmenuitem('Misc', 'command', label='Find param',
					   command=self._findparam)
		mb.addmenuitem('Misc', 'separator')
		mb.addmenuitem('Misc', 'command', label='Drain juice',
					   command=self._drain)
		mb.addmenuitem('Misc', 'separator')
		mb.addmenuitem('Misc', 'command', label='start beep',
					   command=self.warn_run_start)
		mb.addmenuitem('Misc', 'command', label='stop beep',
					   command=self.warn_run_stop)
		mb.addmenuitem('Misc', 'command', label='correct beep',
					   command=self.warn_trial_correct)
		mb.addmenuitem('Misc', 'command', label='error beep',
					   command=self.warn_trial_incorrect)
		mb.addmenuitem('Misc', 'command', label='where am i?',
					   command=self._whereami)

		mb.addmenu('Set', '', '')
		mb.addmenuitem('Set', 'checkbutton', label='show trace window',
					   variable=self._show_eyetrace)
		mb.addmenuitem('Set', 'checkbutton', label='X-T eye traces',
					   variable=self._show_xt_traces)


		# make top-level menubar for task loaders that can be
		# disabled when it's not safe to load new tasks...
		self._loadmenu = Pmw.MenuBar(f1)
		self._loadmenu.pack(side=RIGHT, expand=1, fill=X)
		self.make_taskmenu(self._loadmenu)

		self._loadmenu.addmenu('Help', '', side=RIGHT)
		self._loadmenu.addmenuitem('Help', 'command',
								   label='About Pype',
								   command=self.about)

		f1b = Frame(leftpane, borderwidth=1, relief=GROOVE)
		f1b.pack(expand=0, fill=X)

		self.taskmodule = None
		tmp = Frame(f1b, borderwidth=1, relief=GROOVE)
		tmp.pack(expand=1, fill=X)

		self._tasknamew = Label(tmp)
		self._tasknamew.pack(side=LEFT)

		self.task_name = None
		self.task_dir = None
		self._taskname(None, None)

		# record state is the TTL line used to sync pype to
		# and external recording system (plexon, etc)

		if self.training:
			Label(tmp, text='train mode', relief=SUNKEN).pack(side=RIGHT)
		else:
			Label(tmp, text='record mode', relief=SUNKEN).pack(side=RIGHT)

		f = Frame(f1b, borderwidth=1, relief=GROOVE)
		f.pack(expand=1, fill=X)

		self._recfile = Label(f)
		self._recfile.pack(side=LEFT)
		self._set_recfile()
		self.balloon.bind(self._recfile, "current datafile (if any)")

		self._repinfo = Label(f, text=None)
		self._repinfo.pack(side=RIGHT)

		self._stateinfo = Label(f, text=None, font='Courier 10')
		self._stateinfo.pack(side=RIGHT)
		self.mldown = None
		self.balloon.bind(self._stateinfo, "state info: bar, juice etc")

		bb = Frame(f1b)
		bb.pack(expand=1, side=TOP, anchor=W)

		f2 = Frame(leftpane)				# entire lower section.. not visible!
		f2.pack(expand=1)

		f = Frame(f2)
		f.grid(row=0, column=0, sticky=N+S)

		c1pane = Frame(f, borderwidth=1, relief=RIDGE)
		c1pane.pack(expand=0, fill=X, side=TOP, pady=10)

		c2pane = Frame(f, borderwidth=1, relief=RIDGE)
		c2pane.pack(expand=0, fill=X, side=TOP, pady=5)

		c3pane = Frame(f, borderwidth=1, relief=RIDGE)
		c3pane.pack(expand=0, fill=X, side=TOP, pady=10)
		self._userbuttonframe = c3pane

		b = Button(c1pane, text='reload',
				   command=self.loadtask, state=DISABLED)
		b.pack(expand=0, fill=X, side=TOP)
		self.balloon.bind(b, "reload current task")
		self.reloadbut = b

		self._task_prevtaskname = None
		self._task_prevdir = None
		b = Button(c1pane, text='previous',
				   command=self.prevtask, state=DISABLED)
		b.pack(expand=0, fill=X, side=TOP)
		self.balloon.bind(b, "load previous task")
		self.prevtaskbut = b

		udpy_ = Button(c1pane, text='show disp')
		udpy_.pack(expand=0, fill=X, side=TOP)
		self.balloon.bind(udpy_, "show/hide user display window/pane")

		# reaction time plot window
		b = Checkbutton(c2pane, text='RT hist', relief=RAISED, anchor=W,
						background='lightblue')
		b.pack(expand=0, fill=X, side=TOP, pady=2)
		pw = DockWindow(checkbutton=b, title='Reaction Times')
		Button(pw, text='Clear',
			   command=self.update_rt).pack(side=TOP, expand=1, fill=X)
		self.rthist = EmbeddedFigure(pw)
		self.update_rt()

		if not self.training and not self.psych:
			# psth plot window -- only for recording sessions
			b = Checkbutton(c2pane, text='psth', relief=RAISED, anchor=W,
							background='lightblue')
			b.pack(expand=0, fill=X, side=TOP, pady=2)
			pw = DockWindow(checkbutton=b, title='psth')
			Button(pw, text='Clear',
				   command=self.update_psth).pack(side=TOP, expand=1, fill=X)
			self.psth = EmbeddedFigure(pw)
			self.update_psth()
		else:
			self.psth = None

		if self.config.iget('ELOG', 1) and ('ELOG' in os.environ):
			# ELOG should specify path to the elog module
			_addpath(os.environ['ELOG'])
			try:
				import elogapi
				self.use_elog = 1
				Logger("pype: connecting to ELOG database system.\n")
			except ImportError:
				Logger("pype: warning -- ELOG api not available.\n")
				self.use_elog = 0
		else:
			#Logger("pype: no ELOG setup -- using old-style cell counter.\n")
			self.use_elog = 0

		(commonp, rigp, icalp) = _pype_std_params()

		hostname = self._gethostname()
		b = Checkbutton(c2pane, text='subject', relief=RAISED, anchor=W)
		b.pack(expand=0, fill=X, side=TOP, pady=2)
		self.balloon.bind(b, "subject specific parameters")

		sub_common = DockWindow(checkbutton=b, title='Subject Params')
		self.sub_common = ParamTable(sub_common, commonp, file='subject.par')
		if self.use_elog:
			# 'cell' (exper in elog database) not changable in elog mode:
			self.sub_common.lockfield('cell')

		b = Checkbutton(c2pane, text='rig', relief=RAISED, anchor=W)
		b.pack(expand=0, fill=X, side=TOP, pady=2)
		self.balloon.bind(b, "rig/computer specific parameters")
		rig_common = DockWindow(checkbutton=b,
								title='Rig Params (%s)' % hostname)
		self.rig_common = ParamTable(rig_common,
									 rigp, file='rig-%s.par' % hostname)

		b = Checkbutton(c2pane, text='ical', relief=RAISED, anchor=W)
		b.pack(expand=0, fill=X, side=TOP, pady=2)
		self.balloon.bind(b, "eye calibration params")
		ical = DockWindow(checkbutton=b, title='ical')
		self.ical = ParamTable(ical, icalp,
							   file='%s-%s-ical.par' % (hostname, subject(),))

		# JAM 07-feb-2003: Compute ppd values based on current setup.
		# Then place these in the rig menu automatically.

		s = 180.0 * 2.0 * math.atan2(monw/2, viewdist) / np.pi
		xppd = self.config.fget("DPYW") / s;

		s = 180.0 * 2.0 * math.atan2(monh/2, viewdist) / np.pi
		yppd = self.config.fget("DPYH") / s;

		ppd = (xppd + yppd) / 2.0

		self.rig_common.set('mon_id', self.config.get('MON_ID', ''))
		self.rig_common.set('viewdist', '%g' % viewdist)
		self.rig_common.set('mon_width', '%g' % monw)
		self.rig_common.set('mon_height', '%g' % monh)
		self.rig_common.set('mon_dpyw', self.config.iget('DPYW'))
		self.rig_common.set('mon_dpyh', self.config.iget('DPYH'))
		self.rig_common.set('mon_h_ppd', '%g' % xppd)
		self.rig_common.set('mon_v_ppd', '%g' % yppd)
		self.rig_common.set('mon_ppd', '%g' % ppd)

		et = self.config.get('EYETRACKER', 'NONE')
		if et == 'ISCAN':
			self.rig_common.set('eyetracker', et)
			self.rig_common.set('eyelag', '16')
		elif et == 'EYELINK':
			self.rig_common.set('eyetracker', et)
			self.rig_common.set('eyelag', '0')
			mb.addmenuitem('Misc', 'separator')
			mb.addmenuitem('Misc', 'command', label='reconnect to eyelink',
						   command=self.elrestart)
		elif et == 'ANALOG' or et == 'NONE':
			self.rig_common.set('eyetracker', et)
			self.rig_common.set('eyelag', '0')
		elif et == 'MOUSE':
			self.rig_common.set('eyetracker', et)
			self.rig_common.set('eyelag', '0')
		else:
			Logger("pype: %s is not a valid EYETRACKER.\n" % et)
			raise PypeStartupError
		self.rig_common.set('eyefreq', self.config.get('EYEFREQ', '-1'))

		startstopf = Frame(f, borderwidth=3, relief=RIDGE)
		startstopf.pack(expand=0, fill=X, side=TOP)

		w = self._named_start = Button(bb, command=self._start)
		addicon(self, w, 'run.gif')
		self.balloon.bind(self._named_start, 'start, saving data')
		self._named_start.pack(expand=1, fill=Y, side=LEFT)
		self._named_start.config(state=DISABLED)

		w = self._temp_start = Button(bb, command=self._starttmp)
		addicon(self, w, 'runtemp.gif')
		self._temp_start.pack(expand=1, fill=Y, side=LEFT)
		self.balloon.bind(self._temp_start, "start w/o saving data")
		self._temp_start.config(state=DISABLED)

		w = self._stop = Button(bb, command=self._start_helper, state=DISABLED)
		addicon(self, w, 'Stop.gif')
		self._stop.pack(expand=1, fill=Y, side=LEFT)
		self.balloon.bind(self._stop, "stop run at end of trial")

		w = self._stopnow = Button(bb, command=self._stopabort, state=DISABLED)
		addicon(self, w, 'Cancel.gif')
		self._stopnow.pack(expand=1, fill=Y, side=LEFT)
		self.balloon.bind(self._stopnow, "stop run immediately")
		self._doabort = 0

		if not self.psych:
			w = b = Button(bb, command=self.reward)
			addicon(self, w, 'drop.gif')

			b.pack(expand=1, fill=Y, side=LEFT)
			self.balloon.bind(b, "deliver a reward (also F4)")

			if not self.use_elog and not self.training:
				w = b = Button(bb, command=self._new_cell)
				addicon(self, w, 'cell.gif')
				b.pack(expand=1, fill=Y, side=LEFT)
				self.balloon.bind(b, "increment 'cell' counter")

			if not self.psych:
				self._candyon = 0
				mb.addmenu('Candy', '', '')
				for (s, fn) in candy.list_():
					mb.addmenuitem('Candy', 'command', label=s,
								   command=lambda s=self,f=fn: s._candyplay(f))

		self.make_toolbar(bb)

		mb.addmenu('|', '', '')

		self.recent = []

		book = Pmw.NoteBook(f2)
		book.grid(row=0, column=1, sticky=N+S+E)

		runlog = book.add('Pype')
		triallog = book.add('Trial')
		stats = book.add('Perf')
		itrack1 = book.add('iTrak')
		tally = book.add('Tally')

		tallyf = Frame(tally)
		tallyf.pack(side=BOTTOM, fill=X)

		self._console = LogWindow(runlog)
		self._info = LogWindow(triallog)

		self._whereami()

		self.statsw = Label(stats, text='',
							anchor=W, justify=LEFT,
							font="Courier 10")
		self.statsw.pack(expand=0, fill=BOTH, side=TOP)


		Button(tallyf, text="clear all",
				   command=lambda s=self: s._tally(clear=1)).pack(side=LEFT)
		b = Button(tallyf, text="clear task",
				   command=lambda s=self: s._tally(cleartask=1)).pack(side=LEFT)
		self.tallyw = LogWindow(tally, bg='gray90')
		self._runstats_update(clear=1)
		self._tally(type=None)

		f = Frame(itrack1)
		f.pack(expand=0, fill=X, side=TOP)

		fbar = Frame(f)
		fbar.pack(expand=1, fill=X, side=TOP)

		b = Button(fbar, text="update\ncalib",
				   command=self.eyeset)
		b.pack(expand=0, fill=Y, side=LEFT, pady=0)
		self.balloon.bind(b, "send tracker settings to dacq processes")

		b = Button(fbar, text='zero now\n(F8)',
				   command=lambda s=self: s.eyeshift(zero=1))
		b.pack(expand=0, fill=Y, side=LEFT)
		self.balloon.bind(b, "subject is looking at (fx,fy) NOW")

		b = Button(fbar, text="clear\naffine",
				   command=self.clearaffine)
		b.pack(expand=0, fill=Y, side=LEFT, pady=0)
		self.balloon.bind(b, "reset affine cal")

		b = Button(fbar, text="clear\ngain",
				   command=self.cleargains)
		b.pack(expand=0, fill=Y, side=LEFT, pady=0)
		self.balloon.bind(b, "reset gains cal")

		b = Button(fbar, text='clear\noffsets',
				   command=lambda s=self: s.eyeshift(reset=1))
		b.pack(expand=0, fill=Y, side=LEFT)
		self.balloon.bind(b, "reset offset's to 0,0")

		fbar = Frame(f)
		fbar.pack(expand=1, fill=X, side=TOP)

		w = b = Button(fbar, command=lambda s=self: s.eyeshift(x=1, y=0))
		addicon(self, w, 'left.gif')
		b.pack(expand=0, fill=Y, side=LEFT)
		self.balloon.bind(b, "shift offsets left (immediate effect)")
		w = b = Button(fbar, command=lambda s=self: s.eyeshift(x=-1, y=0))
		addicon(self, w, 'right.gif')
		b.pack(expand=0, fill=Y, side=LEFT)
		self.balloon.bind(b, "shift offsets right (immediate effect)")
		w = b = Button(fbar, command=lambda s=self: s.eyeshift(x=0, y=-1))
		addicon(self, w, 'up.gif')
		b.pack(expand=0, fill=Y, side=LEFT)
		self.balloon.bind(b, "shift offsets up (immediate effect)")
		w = b = Button(fbar, command=lambda s=self: s.eyeshift(x=0, y=1))
		addicon(self, w, 'down.gif')
		b.pack(expand=0, side=LEFT)
		self.balloon.bind(b, "shift offsets down (immediate effect)")

		Label(itrack1,
			  text="Use Shift/Ctrl/Meta-Arrows in UserDisplay\n"+
				   "window to adjust offsets in real-time",
			  relief=SUNKEN).pack(expand=0, fill=X, side=TOP, pady=10)

		# make sure Notebook is big enough for buttons above to show up
		#pw.setnaturalsize()
		book.setnaturalsize(pageNames=None)

		# extract some startup params.. these are read only ONCE!
		self.pix_per_dva = float(self.rig_common.queryv('mon_ppd'))

		# keyboard/event input que
		self.tkkeyque = EventQueue(self.tk, '<Key>')

		# history info
		self._hist = Label(f2, text="", anchor=W, borderwidth=1, relief=RIDGE)
		self._hist.grid(row=3, column=0, columnspan=3, sticky=W+E)
		self.balloon.bind(self._hist, "recent trial result codes")

		# make sure we're root, if possible
		root_take()

		self.dacq_going = 1
		self.eyeset()

		# stash info on port states
		# this is a hack -- some buttons are down/true others are
		# up/true .. lets user sort it all out..
		self.flip_bar = self.config.iget('FLIP_BAR')

		# beep with each reward?
		self.reward_beep = self.config.iget('REWARD_BEEP')

		# NOTE:
		# Framebuffer initialization will give up root access
		# automatically.. so make sure you start the dacq process
		# first (see above).
		try:
			root_drop()
			if not self.config.iget('SOUND'):
				beep(disable=1)
				Logger('pype: audio disabled in config file.\n')
			else:
				if self.config.get('AUDIODRIVER'):
					audiodriver = self.config.get('AUDIODRIVER')
				beep()
		finally:
			root_take()

		# added automatic detection of framerate (13-jan-2004 JAM):
		# Wed Apr 27 17:37:26 2011 mazer moved it into init_framebuffer
		fps = self.init_framebuffer()

		if self.config.iget('FPS') and self.config.iget('FPS') != fps:
			Logger('pype: error actually FPS does not match requested rate\n' +
				   '	  requested=%dhz actual=%dhz\n' %
				   (self.config.iget('FPS'), fps))
			raise PypeStartupError
		self.rig_common.set('mon_fps', '%g' % fps)
		Logger('pype: estimated fps = %g\n' % fps)

		# use mouse in userdpy as substitute for eye tracker?
		#  - if set, then mouse button-1 clicking will simulate saccade
		#	 to indicate location
		#  - should work in either the userdisplay or the framebuffer
		#	 window
		self.eyemouse = self.config.iget('EYEMOUSE', 0)
		if self.eyemouse:
			self.eyeset(xgain=1.0, ygain=1.0, xoff=0, yoff=0)
			self.fb.cursor(on=1)
		self.eyebar = 0

		# userdisplay: shadow of framebuffer window
		scale = self.config.fget('USERDISPLAY_SCALE')
		self.udpy = userdpy.UserDisplay(rightpane,
										fbsize=(self.fb.w, self.fb.h),
										scale=scale,
										pix_per_dva=self.pix_per_dva,
										app=self,
										eyemouse=self.eyemouse)

		udpy_.config(command=self.udpy.showhide)
		if self.config.iget('USERDISPLAY_HIDE'):
			self.udpy.showhide()
		if not rightpane:
			self.udpy.master.protocol("WM_DELETE_WINDOW", self._shutdown)

		if posixpath.exists(subjectrc('last.fid')):
			self.udpy.loadfidmarks(file=subjectrc('last.fid'))
		if posixpath.exists(subjectrc('last.pts')):
			self.udpy.loadpoints(subjectrc('last.pts'))
		self.dpy_w = self.fb.w
		self.dpy_h = self.fb.h

		# this must be defered until sync spot info is computed..
		self.udpy.drawaxis()

		# drop root access
		# Tue Jul 12 10:01:53 2005 mazer --
		#  dropping root access causes the ALSA libs to bitch. I'm
		#  not sure what the problem is, but we're generally having
		#  also of sound problems recently..
		root_drop()
		Logger('pype: dropped root access\n')

		# Sat Sep  3 16:56:50 2005 mazer
		# as of now, fixation break and bartransitions received via
		# the interupt handler (SIGUSR1) are handled the first time
		# idlefn() gets called after the interupt. The interupt handler
		# just sets these flags and exceptions are raised at the next
		# possible time. Therefore, you must continue to call idlefn
		# (although you can now use fast=1 to minimize CPU usage) if
		# you can FixBreak and BarTransition to work..
		self._post_fixbreak = 0
		self._post_bartransition = 0
		self._post_joytransition = 0	# joypad but > 1
		self._joypad_intbut = None
		self._post_alarm = 0
		self.lastint_ts = None			# exact time of last interupt
		self.idle_queue = []

		# catch interupts from the das_server process indicating
		# bar state transitions and fixation breaks

		# make sure bar touches don't cause interupts
		dacq_bar_genint(0)
		dacq_joy_genint(0)

		# disable interupts and default to interupt queuing
		self.interupts(enable=0, queue=1)

		# setup interupt handler
		signal.signal(signal.SIGUSR1, self._int_handler)

		# we're now ready to receive interupts, but they won't come
		# through until you do in your task:
		#	(app/self).interupts(enable=1, queued=0|1)

		#
		# External DACQ interface --
		#  this is for multichannel recording systems:
		#	 - Plexon MAP box (via PlexNet API)
		#	 - Tucker-Davis (via pype's tdt.py client-server module)
		#
		self.xdacq = None
		self.xdacq_data_store = None
		self.plex = None
		self.tdt = None

		plexhost = self.config.get('PLEXHOST')
		tdthost = self.config.get('TDTHOST')

		if self.training:
			Logger('pype: warning -- xdacq disabled in training mode\n')
		elif len(plexhost) > 0 and len(tdthost) > 0:
			Logger('pype: either PLEXHOST *or* TDTHOST (disabled!!)\n', popup=1)
		elif self.xdacq is None and len(plexhost) > 0:
			try:
				self.plex = PlexNet.PlexNet(plexhost,
											self.config.iget('PLEXPORT'))
				Logger('pype: connected to plexnet @ %s.\n' % plexhost)
				self.xdacq = 'plexon'

				mb.addmenu('PlexNet', '', '')
				mb.addmenuitem('PlexNet', 'command',
							   label='query plexnet',
							   command=self.status_plex)
				mb.addmenuitem('PlexNet', 'separator')
			except socket.error:
				Logger('pype: failed connect to plexnet @ %s.\n' % plexhost,
					   popup=1)
		elif self.xdacq is None and len(tdthost) > 0:
			tankdir = self.config.get('TDTTANKDIR')
			if len(tankdir) == 0:
				Logger('pype: no TDTANKDIR set, using C:\\', popup=1)
				tankdir = 'C:\\'
			if not tankdir[-1] == '\\':
				# dir must have trailing backslash
				tankdir = tankdir + '\\'

			tankname = subject()
			tankname += '%04d%02d%02d' % time.localtime(time.time())[0:3]

			try:
				self.tdt = pype2tdt.Controller(self, tdthost)
				Logger('pype: connected to tdt @ %s.\n' % tdthost)
				t = self.tdt.settank(tankdir, tankname)
				if t is None:
					Logger("pype: is TDT running? Can't set tank.\n", popup=1)
					self.tdt = None
				else:
					Logger('pype: tdt tank = "%s"\n' % t)
					self.xdacq = 'tdt'
			except (socket.error, tdt.TDTError):
				self.tdt = None
				Logger('pype: no connection to tdt @ %s.\n' % tdthost, popup=1)

		Logger('pype: build %s by %s on %s\n' %
			   (pypeversion.PypeBuildDate, pypeversion.PypeBuildBy,
				pypeversion.PypeBuildHost) +
			   'pype: PYPERC=%s\n' % pyperc() +
			   'pype: CWD=%s\n' % os.getcwd())

		if debug():
			import libinfo
			libinfo.print_version_info()

		if dacq_jsbut(-1):
			self._console.writenl("Joystick button #1 is BAR!", color='blue')

		self.recording = 0
		self.record_state(0)

		self.migrate_pypestate()

		self._testpat = None
		self.showtestpat()

		self._show_stateinfo()

		if self.psych:
			self.fb.screen_close()


	def elrestart(self):
		dacq_elrestart()

	def about(self, timeout=None):
		show_about(os.path.join(self.pypedir,'lib', 'logo.gif'), timeout)

	def queue_action(self, inms=None, action=None):
		"""Queue an action to happen about inms from now. Call with
		no args to clear the actio queue.

		Action will be dispatched from the idlefn() on or after the
		specified deadline.

		"""

		if inms is None:
			self.idle_queue = []
		else:
			self.idle_queue.append((dacq_ts()+inms, action,))

	def _whereami(self):
		self._console.writenl('	   ver: pype %s' % (pypeversion.PypeVersion,),
							  'blue')
		self._console.writenl('		id: %s' % (pypeversion.PypeVersionID),
							  'blue')
		self._console.writenl('pypedir: %s' % self.pypedir, 'blue')
		self._console.writenl(' pyperc: %s' % pyperc(), 'blue')
		self._console.writenl('	   cwd: %s' % os.getcwd(), 'blue')
		self._console.writenl('_'*60)

	def migrate_pypestate(self):
		fname = subjectrc('pypestate.%s' % self._gethostname())
		if (posixpath.exists(fname) and
			ask('migrate_pypestate', 'Automigrate %s?' %
				fname, ['yes', 'no']) == 0):
			try:
				d = cPickle.load(open(fname, 'r'))
				self.tallycount = d['tallycount']
				self._tally()
				# ppd's here are because previously this was set in the
				# wrong (but still functional) units
				xgain = d['eye_xgain'] * self.rig_common.queryv('mon_h_ppd')
				ygain = d['eye_ygain'] * self.rig_common.queryv('mon_v_ppd')
				xoff = d['eye_xoff']
				yoff = d['eye_yoff']

				# if you're migrating, then assume that you
				# don't want any affine transform (yet)

				self.eyeset(xgain=xgain, ygain=ygain, xoff=xoff, yoff=yoff)
				self.clearaffine()

				fname2 = fname+'.obsolete'
				os.rename(fname, fname2)

				warn('migrate_pypestate',
					 'Success; remove %s at will.' % fname2)
			except:
				reporterror(gui=False, db=self.config.iget('DBERRS'))
				warn('migrate_pypestate', 'failed!')

	def con(self, msg=None, color='black', nl=1):
		"""Write message to *console* window.

		*Console* is running log window

		:param msg: (string) message to print

		:param color: (string) color to use

		:param nl: (boolean) add newline at end?

		:return: nothing

		"""
		if msg is None:
			self._console.clear()
		else:
			if nl:
				self._console.writenl(msg, color)
			else:
				self._console.write(msg, color)

	def info(self, msg=None, color='black', nl=1):
		"""Write message to *info* window.

		*Info* is the window that gets cleared at the start of each trial.

		:param msg: (string) message to print

		:param color: (string) color to use

		:param nl: (boolean) add newline at end?

		:return: nothing

		"""
		if msg is None:
			self._info.clear()
		else:
			if nl:
				self._info.writenl(msg, color)
			else:
				self._info.write(msg, color)

	def _candyplay(self, fn):
		try:
			fn(self)
		finally:
			self.showtestpat()

	def _findparam(self):
		s = Entry_(self.tk, 'find parameter:', '').go()
		if s:
			results = ParamTable(None, None).find(s)
			if not len(results):
				self.con('%s: not found.' % s)
			else:
				for (pt, slot, n) in results:
					d = pt._get(evaluate=0)
					try:
						self.con('%s(row %d): %s=''%s''' %
								 (posixpath.basename(pt._file),
								  n, slot, d[1][slot]))
					except KeyError:
						# skip title slots..
						pass

	def keyboard(self):
		app = self
		sys.stderr.write('Dropping into keyboard shell\n')
		sys.stderr.write('"app" should be defined!\n')
		keyboard()

	def ispaused(self):
		""" this is a NOP now.. pause is gone.. """
		return 0

	def set_state(self, running=-1, led=None, paused=None):
		"""Setting running state flags.

		Use this instead of tweaking internal vars in the app object!

		3/22/2011 mazer: paused is no longer used.
		3/23/2011 mazer: led no longer used.

		"""
		if not (running is -1):	self.running = running

		if self.running:
			try:
				self._recfile.oldbg
			except AttributeError:
				self._recfile.oldbg = self._recfile.cget('bg')
			self._recfile.configure(bg='lightgreen')
		else:
			try:
				self._recfile.configure(bg=self._recfile.oldbg)
			except AttributeError:
				pass

	def _show_stateinfo(self):
		barstate = self.bardown()			# this will handle BAR_FLIP setting
		if barstate:
			t = 'BAR:DN '
		else:
			t = 'BAR:UP '
		if dacq_jsbut(-1):
			t = t + " "
			for n in range(10):
				if dacq_jsbut(n):
					t = t+('%d'%n)
				else:
					t = t+'.'
		try:
			last = self._last_stateinfo
		except AttributeError:
			last = ""


		if self.mldown is not None:
			t = text='%dml %s' % (self.mldown, t)

		if not last == t:
			self._stateinfo.configure(text=t)
			try:
				if barstate:
					self.udpy.titlebar.config(text='bar down', fg='green')
				else:
					self.udpy.titlebar.config(text='bar up', fg='red')
				self._last_stateinfo = t
			except AttributeError:
				pass

	def isrunning(self):
		"""Query to see if a task is running.

		:return: (bool)

		"""
		return self.running

	def set_result(self, type=None):
		"""Save the result of current trial.

		This should be called at the end of each trial to update
		the history stack.

		:param type: if type is None, clear saved results, otherwise
				type should be something like 'C' or 'E' to indicate
				the trial result flag.

		"""
		# combination of self.tally() and self.history()
		if type is None:
			self._results = []
			self._history()
		else:
			self._results.append(type)
			self._history(type[0])
			self._tally(type=type)
			self._runstats_update(resultcode=type)

	def get_result(self, nback=1):
		"""Get the nth to last saved trial result code.

		*NB* get_result(1) is result from last trial, not get_result(0)

		"""
		if len(self._results):
			return self._results[-nback]
		else:
			return None

	def _tally(self, type=None, clear=None, cleartask=None, reward=None):
		ctask = self.task_name
		if not clear is None:
			# clear everything
			self.tallycount = {}
		elif not cleartask is None:
			# just clear current task data
			for (task,type) in self.tallycount.keys():
				if ctask == task:
					del self.tallycount[(task,type)]
		elif not type is None:
			# add new data to current task stats
			try:
				self.tallycount[ctask,type] = self.tallycount[ctask,type] + 1
			except KeyError:
				self.tallycount[ctask,type] = 1
			try:
				del self.tally_recent[0]; self.tally_recent.append(type)
			except AttributeError:
				self.tally_recent = [''] * 5
		elif not reward is None:
			try:
				self.tallycount['reward_n'] += 1
				self.tallycount['reward_ms'] += reward
			except KeyError:
				self.tallycount['reward_n'] = 1
				self.tallycount['reward_ms'] = reward

		ks = self.tallycount.keys()
		ks.sort()

		(ntot, ncorr, s) = (0, 0, '')
		keys = self.tallycount.keys()
		keys.sort()
		for k in keys:
			if not len(k) == 2: continue

			(task, type) = k
			d = type.split()
			if len(d) > 1:
				d = "%s (%s)" % (d[0], string.join(d[1:]))
			else:
				d = d[0]
			s = s + '%s %s: %d\n' % (task, d, self.tallycount[(task,type)])
			if d[0][0] == 'C':
				ncorr = ncorr + self.tallycount[(task,type)]
			ntot = ntot + self.tallycount[(task,type)]
		s = s + '\nncorr:  %d trials' % ncorr
		s = s + '\ntotal:  %d trials' % ntot
		s = s + '\n'

		try:
			rn = self.tallycount['reward_n']
			rms = self.tallycount['reward_ms']
		except KeyError:
			rn = 0
			rms = 0
		s = s + '\nreward: %d drops (%d ms)' % (rn, rms,)
		ml = self.sub_common.queryv('mldropsize')
		if ml > 0:
			self.mldown = rn * ml
			s = s + '\nestimated: %.1f ml' % (self.mldown,)
		else:
			self.mldown = None

		s = s + '\n'
		s = s + '\n'

		try:
			N = len(self.tally_recent)
			for n in range(N):
				if n == 0:
					s = s + 'History\n'
				s = s + '%d: %s\n' % (-(N-n), self.tally_recent[n])
		except AttributeError:
			pass

		self.tallyw.clear()
		self.tallyw.write(s)

	def getcommon(self):
		"""Get common params, extend with eyecoil settings.

		"""
		d = self.rig_common.check()
		d = self.sub_common.check(mergewith=d)
		d = self.ical.check(mergewith=d)

		# for backward compatibility:
		d['@eye_xgain'] = self.ical.queryv('xgain_')
		d['@eye_ygain'] = self.ical.queryv('ygain_')
		d['@eye_xoff'] = self.ical.queryv('xoff_')
		d['@eye_yoff'] = self.ical.queryv('yoff_')
		d['@eye_rot'] = self.ical.queryv('rot_')

		d['@pwd'] = os.getcwd()
		d['@host'] = self._gethostname()

		# add flag for current notion of where spikes are really
		# coming from (currently: 'None', 'plexon' or 'tdt')
		if self.xdacq:
			d['datasrc'] = self.xdacq
		else:
			d['datasrc'] = 'None'

		return d

	def make_taskmenu(self, menubar):
		# add ~/.pyperc/Tasks/*.py (in any)
		self.tasklist = {}

		self.add_tasks(menubar, '~pyperc', pyperc('Tasks'))

		# add each subdir in ~/.pyperc/Tasks (unless prefixed with _)
		files = glob.glob(pyperc('Tasks/*'))
		for d in files:
			m = posixpath.basename(d)
			# Tue Jan  4 11:50:19 2005 mazer -- skip _* dirs (disabled)
			if os.path.isdir(d) and not (m[0] == '_'):
				self.add_tasks(menubar, "~"+m, d)

		# add tasks in current working dir (in any)
		self.add_tasks(menubar, 'cwd', '.')

		# TASKPATH can be set in the Config file and/or as env var..
		taskpathlist = []
		if self.config.get('TASKPATH', None):
			taskpathlist.append(self.config.get('TASKPATH', None))

		for p in taskpathlist:
			for d in p.split(':'):
				try:
					self.add_tasks(menubar, posixpath.basename(d), d)
				except ValueError:
					Logger("pype: skipped dup %s in TASKPATH\n" % d)

	def readpypeinfo(self, filename):
		majik = re.compile('^#pypeinfo;.*')
		f = open(filename, 'r')
		# read up to about 50 lines from the file
		lines = f.readlines(80*50)
		f.close()
		d = {}
		for l in lines:
			if majik.search(l):
				for w in l.split(';')[1:]:
					if ':' in w:
						(tag, val) = w.split(':')
						d[string.strip(tag)] = string.strip(val)
					else:
						d[string.strip(w)] = 1
		return d

	def make_recent(self):
		try:
			self._loadmenu.deletemenu('Recent')
		except KeyError:
			pass
		self._loadmenu.addmenu('Recent', '', '')
		for (t, d) in self.recent:
			self._loadmenu.addmenuitem('Recent', 'command',
									   font=('Courier', 10),
									   label=t,
									   command=lambda s=self,t=t,d=d: \
												s.loadtask(t, d))

	def add_tasks(self, menubar, menulabel, dirname):
		tasks = []
		taskdescrs = {}

		dirname = os.path.join(dirname, '')	  # ensure trailing delim
		filelist = glob.glob(os.path.join(dirname, '*.py'))

		for fname in filelist:
			d = self.readpypeinfo(fname)
			if 'task' in d:
				tasks.append(posixpath.basename(fname)[:-3])
				if 'descr' in d:
					taskdescrs[tasks[-1]] = '%s' % d['descr']
				else:
					taskdescrs[tasks[-1]] = ''
		if len(tasks) == 0:
			if debug():
				Logger('-tasks from: %s\n' % dirname)
			return
		else:
			if debug():
				Logger('+tasks from: %s\n' % dirname)
				for t in tasks:
					Logger('  %s\n' % t)


		# this is needed for pype to find non-task files in the dir
		_addpath(dirname, atend=1)

		tasks.sort()
		# right prevents long menus from generating incorrect task selection!
		menubar.addmenu(menulabel, '', '', direction=RIGHT)
		menubar.addmenuitem(menulabel, 'command',
							label=dirname, foreground='blue')
		menubar.addmenuitem(menulabel, 'command', label='Reload current',
							command=self.loadtask)
		menubar.addmenuitem(menulabel, 'separator')
		for t in tasks:
			if t in self.tasklist:
				#sys.stderr.write('Warning: duplicate task name -- %s\n' % t)
				c = 'blue'
			else:
				c = 'black'
				self.tasklist[t] = 1
			tasklabel = '%-15s %s' % (t, taskdescrs[t])
			menubar.addmenuitem(menulabel, 'command', label=tasklabel,
								font=('Courier', 10),
								foreground=c,
								command=lambda s=self,t=t,d=dirname:
								s.loadtask(t, d))
		menubar.addmenuitem(menulabel, 'separator')
		menubar.addmenuitem(menulabel, 'command', label='Reload current',
							command=self.loadtask)

	def make_toolbar(self, parent):
		if self.config.get('TOOLS', None) is None:
			return

		toolbar = None
		for tool in self.config.get('TOOLS').split(';'):
			if posixpath.exists(tool):
				d = os.path.abspath(os.path.dirname(tool))
				t = os.path.basename(tool).replace('.py','')
				if toolbar is None:
					toolbar = Frame(parent, borderwidth=1, relief=RIDGE)
					toolbar.pack(fill=Y, padx=10)
				b = Button(toolbar, text=t,
						   background='orange',
						   command=lambda s=self, t=t, d=d:s.loadtask(t,d))
				b.pack(side=LEFT)
				self.balloon.bind(b, 'quick load '+tool)

	def prevtask(self):
		try:
			if self._task_prevtaskname:
				self.loadtask(self._task_prevtaskname, self._task_prevdir)
			return 1
		except AttributeError:
			return 0

	def unloadtask(self):
		if self.taskmodule:
			self.set_startfn(None)
			if hasattr(self.taskmodule, 'cleanup'):
				self.taskmodule.cleanup(self)
			del self.taskmodule
			self.taskmodule = None
		for w in [self._named_start, self._temp_start]:
			w.config(state=DISABLED)

	def loadtask(self, taskname=None, path=None, ask=False):
		"""(Re)load task from file.

		Load a task, if taskname==None and path==None then we reload the current
		task, if possible.	If ask is true, then pop up a dialog box to ask for
		a filename..

		:param taskname: (string) task name without .py suffice

		:param path: (string) directory where task is stored

		:param ask: (bool) query user for task to load

		:return: None for error, task module on success

		"""
		import imp, filebox

		if ask:
			(f, mode) = filebox.Open(pattern='*.py',
									 text='Load task from .py file')
			if f is None:
				return None
			path = posixpath.dirname(f)
			taskname = posixpath.basename(f)
			if taskname[-3:] == '.py':
				taskname = taskname[:-3]

		if taskname is None:
			if self.task_name is None:
				return None
			taskname = self.task_name
			path = self.task_dir

		try:
			if path:
				(file, pathname, descr) = imp.find_module(taskname, [path])
			else:
				path = posixpath.dirname(taskname)
				if len(path) == 0:
					path = None
					(file, pathname, descr) = imp.find_module(taskname)
				else:
					taskname = posixpath.basename(taskname)
					if taskname[-3:] == '.py':
						taskname = taskname[:-3]
					(file, pathname, descr) = imp.find_module(taskname, [path])
		except ImportError:
			warn('pype:loadtask',
				 "Can't find task '%s' on search path.\n" % taskname +
				 "Try specifying a full path!")
			return None

		key = (taskname, path,)
		if key in self.recent: self.recent.remove(key)
		self.recent = [key] + self.recent
		self.recent = self.recent[:5]
		self.make_recent()

		# save previous task so it can be reloaded quickly...
		try:
			self._task_prevtaskname = self._task_taskname
			self._task_prevdir = self._task_dir
			self.prevtaskbut.config(text='<-%s' % self._task_prevtaskname,
									state=NORMAL)
		except AttributeError:
			self._task_prevtasktask = None
			self._task_prevdir = None

		self.unloadtask()				# unload current, if it exists..

		try:
			try:
				Logger("pype: loaded '%s' (%s)\n" % (taskname, pathname))
				taskmod = imp.load_module(taskname, file, pathname, descr)
				mtime = os.stat(pathname).st_mtime
			except:
				err = ('Error loading ''%s'' -- \n' % taskname) + get_exception()
				sys.stderr.write(err)
				warn('pype:loadtask', err, wait=0, astext=1)
				return None

			self.reloadbut.config(text='reload', state=NORMAL)

		finally:
			# in case loading throws an exception:
			if file:
				file.close()

		if path is None:
			path, base = os.path.split(pathname)

		if taskmod:
			self._task_taskname = taskname
			self._task_dir = path

			self.taskmodule = taskmod
			self._taskname(taskname, path)
			self._task_pathname = pathname
			self._task_mtime = mtime

			if hasattr(self.taskmodule, 'main'):
				# module must provide a 'main' function that is:
				#  1. a function that takes one arg (app; PypeApp handle,
				#	  ie, self).
				#  2. When called, binds something to the start function
				#	  by  calling app.set_startfn, eg:
				#		 t = make_some_task_object_with_state()
				#		 app.set_startfn(lambda app,task=t: task.start_run(app))
				# module MAY optionally provide a cleanup function that
				# also takes 'app', that will be called when the task is
				# unloaded.
				self.taskmodule.main(self)
			else:
				Logger("pype: warning -- no 'main' in %s\n" % taskname)

		if self._startfn:
			for w in [self._named_start, self._temp_start]:
				w.config(state=NORMAL)
		else:
			warn('pype:loadtask', 'no start function set!')

		return taskmod

	def set_canvashook(self, fn=None, data=None):
		"""
		Set function to call when unbound key is pressed in the
		udy canvas window. Function should take three arguments,
		e.g., **def hookfn(data, key, ev):...**.

		Where data is whatever you want the function to have
		and key is the string containing the key pressed and
		ev is the full event, in case you want (x,y) etc.

		The hook function should return 1 or 0 to indicate if
		the keypress was actually consumed.

		This function returns the old hookfn and hookdata values so
		they can be saved and restored.

		"""
		oldfn = self.udpy.userhook
		olddata = self.udpy.userhook_data
		self.udpy.userhook = fn
		self.udpy.userhook_data = data
		return (oldfn, olddata)

	def udpy_note(self, t=''):
		self.udpy.note(t)

	def cleargains(self):
		"""Clear eyecal gains.

		:return: nothing

		"""
		self.eyeset(xgain=1.0, ygain=1.0)

	def clearaffine(self):
		"""Clear eyecal affine transform (set to identity matrix).

		:return: nothing

		"""
		self.eyeset(affine=np.identity(3))

	def eyeset(self, xgain=None, ygain=None, xoff=None, yoff=None,
			   rot=None, affine=None):
		"""Update eye tracking params from pype -> comedi_server

		:param xgain, ygain: (float)

		:param xoff, yoff: (int)

		:param rot: (float)

		:param affine: (3x3 matrix)

		:return: nothing

		"""

		if not xgain is None:	self.ical.set('xgain_', '%f' % xgain)
		if not ygain is None:	self.ical.set('ygain_', '%f' % ygain)
		if not xoff is None:	self.ical.set('xoff_', '%d' % xoff)
		if not yoff is None:	self.ical.set('yoff_', '%d' % yoff)
		if not rot is None:	self.ical.set('rot_', '%f' % rot)
		if not affine is None:
			# convert 3x3 matrix into CSV string for param table storage
			a = string.join(map(lambda f: '%g'%f, affine.flatten()), ',')
			self.ical.set('affinem_', a)

		dacq_eye_smooth(self.rig_common.queryv('eye_smooth'))
		dacq_fixbreak_tau(self.rig_common.queryv('fixbreak_tau'))

		xg = self.ical.queryv('xgain_')
		yg = self.ical.queryv('ygain_')
		xo = -self.ical.queryv('xoff_')
		yo = -self.ical.queryv('yoff_')
		rot = self.ical.queryv('rot_')

		dacq_eye_params(xg, yg, xo, yo, rot)

		# it is possible to merge xgain/xoff/ygain/yoff into a single
		# matrix, by:
		#  A[0,0] *= xgain; A[2,0] += xoff;
		#  A[1,1] *= ygain; A[2,1] += yoff;
		# but there is a problem in that the offset's are in pixels
		# and need to be in ETUs.. so forget it for now..

		try:
			A = map(float, self.ical.query('affinem_').split(','))
			A = np.array(A).reshape(3,3)
			for r in range(3):
				for c in range(3):
					dacq_eye_setaffine_coef(r, c, A[r,c])
		except:
			warn('ical::affine', 'affine matrix should be 9-element vector')

	def init_dacq(self):

		# EYELINK_OPTS can be defined in the pyperc config file and
		# should be a colon-delimited list of commands to be sent to
		# the eyelink one at a time. Most users should NEVER use this
		# feature, it's really just for testing and debugging.
		#
		# NOTE: No attempt is made to make sure the built in commands
		# don't conflict with user commands.


		if self.config.iget('PUPILXTALK', default=-666) != -666:
			Logger("pype: change PUPILXTALK to EYELINK_XTALK in Config file\n")
			raise PypeStartupError

		eyelink_opts = self.config.get('EYELINK_OPTS')
		if len(eyelink_opts) > 0:
			eyelink_opts = eyelink_opts + ':'
		eyelink_opts = eyelink_opts + ('pupil_crosstalk_fixup=%s' %
									   self.config.get('EYELINK_XTALK'))
		eyelink_opts = eyelink_opts + ':active_eye=both'
		eyelink_opts = eyelink_opts + ':link_sample_data=PUPIL,AREA'
		eyelink_opts = eyelink_opts + ':heuristic_filter=0 0'
		eyelink_opts = eyelink_opts + ':pup_size_diameter=NO'

		s = dacq_start('comedi_server',
					   '--tracker=%s' % self.config.get('EYETRACKER'),
					   '--port=%s' % self.config.get('EYETRACKER_DEV'),
					   '--elopt="%s"' % eyelink_opts,
					   '--elcam=%s' % self.config.get('EYELINK_CAMERA'),
					   '--swapxy=%d' % self.config.iget('SWAP_XY'),
					   '--usbjs=%s' % self.config.get('USB_JS_DEV'), 0)

		# <0: fatal error -- exit regardless of force..
		# =0: overridable error, ok to retry..
		# =1: success
		if s <= 0:
			Logger("init_dacq: comedi_server can't start.\n")
			Logger("init_dacq: try running 'pypekill' or 'pypekill -s'\n")
			raise PypeStartupError

		# Tue Jan  8 15:08:12 2013 mazer
		#	- This basically works -- the lag between the comedi
		#	  datastream and the labjack is ~0.7ms as far as I can
		#	  tell (using cross correlation against FM chirps).
		#	- However, integration is not complete... not sure how
		#	  I want to do this -- could use it to get rid of
		#	  comedi_server completely..
		try:
			import labjack
			self.u3 = labjack.SamplerU3()
			Logger("pype: found a labjack u3 -- validation mode\n")
		except ImportError:
			Logger("pype: LabJack drivers not installed.\n")
			self.u3 = None

	def init_framebuffer(self):
		sx = self.config.get('SYNCX', None)
		if not sx is None:
			sx = int(sx)
		sy = self.config.get('SYNCY', None)
		if not sy is None:
			sy = int(sy)

		self.fb = FrameBuffer(self.config.get('SDLDPY'),
							  self.config.iget('DPYW'),
							  self.config.iget('DPYH'),
							  self.config.iget('FULLSCREEN'),
							  syncsize=self.config.iget('SYNCSIZE'),
							  syncx=sx, syncy=sy,
							  synclevel=self.config.iget('SYNCLEVEL'),
							  mouse=self.config.iget('MOUSE'),
							  frame = self.config.iget('FRAME'),
							  app=self)

		fps = self.fb.calcfps(duration=250)

		self.fb.app = self
		g = self.config.fget('GAMMA')
		if self.fb.set_gamma(g):
			Logger("pype: gamma set to %f\n" % g)
		else:
			Logger("pype: hardware does not support gamma correction\n")

		# turn off the xserver's audible bell and screensaver!
		d = self.config.get('SDLDPY')
		if os.system("xset -display %s b off" % d):
			Logger("Can't run xset to turn off bell!\n")
		if os.system("xset -display %s s off" % d):
			Logger("Can't run xset to turn off screen saver!\n")
		if os.system("xset -display %s -dpms" % d):
			Logger("Can't run xset to turn off DPMS!\n")

		return fps

	def _gethostname(self):
		"""Safe version of socket.gethostname().

		:return: first part of socket.gethostname(), if a hostname is
				actually defined, otherwise returns 'NOHOST'.

		"""
		try:
			return socket.gethostname().split('.')[0]
		except:
			return 'NOHOST'

	def _tallyfile(self, save=1):
		"""load/save tallyfile

		:return: age of last tallyfile in days

		"""

		fname = subjectrc('tally.%s.%s' % (subject(), self._gethostname(),))
		try:
			age = (time.time()-os.path.getmtime(fname)) / (60.*60.*24.)
		except OSError:
			age = -1
		try:
			if save:
				cPickle.dump(self.tallycount, open(fname, 'w'))
			else:
                if age > 0.5 and ask('loadstate',
                                     'Tally data > 12h old; load anyway?',
                                     ['yes', 'no']) == 0:
                    self.tallycount = cPickle.load(open(fname, 'r'))
		except IOError:
			Logger("Can't read/write tally file.\n")

		return age

	def _savestate(self):
		self.setgeo(save=1)
		self.rig_common.save()
		self.sub_common.save()
		self.ical.save()
		self._tallyfile(save=1)

	def _loadstate(self):
		self._tallyfile(save=0)

	def _runstats_update(self, clear=None, resultcode=None):
		if clear is not None:
			self._runstats = {}
			self._runstats['ncorrect'] = 0
			self._runstats['nerror'] = 0
			self._runstats['nui'] = 0	# really sequential UI's
		elif resultcode is not None:
			r = resultcode[0]

			if r in 'C':
				self._runstats['ncorrect'] = self._runstats['ncorrect'] + 1
				self._runstats['nui'] = 0
			elif r in 'EM':
				self._runstats['nerror'] = self._runstats['nerror'] + 1
				self._runstats['nui'] = 0
			elif r in 'U':
				self._runstats['nui'] = self._runstats['nui'] + 1

			nmax = self.sub_common.queryv('max_trials')
			n = self._runstats['ncorrect'] + self._runstats['nerror']
			if (nmax > 0) and n > nmax:
				self.set_state(running=0)
				warn('pype:_runstats_update',
					 '%d total trials reached -- stopping.' % n, wait=0)

			nmax = self.sub_common.queryv('max_correct')
			n = self._runstats['ncorrect']
			if (nmax > 0) and n > nmax:
				self.set_state(running=0)
				warn('pype:_runstats_update',
					 '%d correct trials reached -- stopping.' % n, wait=0)

			nmax = self.sub_common.queryv('max_ui')
			n = self._runstats['nui']
			if (nmax > 0) and n > nmax:
				self.set_state(running=0)
				warn('pype:_runstats_update',
					 '%d sequential UI trials -- stopping.' % n, wait=0)

		ne = self._runstats['nerror']
		nc = self._runstats['ncorrect']
		nu = self._runstats['nui']
		nt = nc + ne
		s = string.join((
			' running = %d'	   % (self.isrunning(),),
			'----------------------------------',
			'  nerror = %d'		 % (ne,),
			'ncorrect = %d [%d]' % (nc, self.sub_common.queryv('max_correct'),),
			'	  nui = %d [%d]' % (nu, self.sub_common.queryv('max_ui'),),
			' ntrials = %d [%d]' % (nt, self.sub_common.queryv('max_trials'),),
			'----------------------------------'), '\n')
		self.statsw.configure(text=s)

	def _start(self):
		self._start_helper(temp=None)

	def _starttmp(self):
		self._start_helper(temp=1)

	def _stopabort(self):
		self._doabort = 1
		self.running = 0

	def _start_helper(self, temp=None):
		if self.running:
			self._stop.config(state=DISABLED)
			self._stopnow.config(state=DISABLED)
			self.running = 0
		else:
			if (os.stat(self._task_pathname).st_mtime <> self._task_mtime and
				ask('run task', 'Task has changed\nRun anyway?',
					['yes', 'no']) == 1):
				return

			if self._validatefn:
				# abort if validatefn returns False
				if not self._validatefn(self):
					return

			try:
				self._savestate()
				self._loadmenu.disableall()
				for w in (self._named_start, self._temp_start,
						  self.reloadbut, self.prevtaskbut,):
					w.config(state=DISABLED)
				self._stop.config(state=NORMAL)
				self._stopnow.config(state=NORMAL)

				if temp:
					if self.sub_common.queryv('save_tmp'):
						fname = './%s.tmp' % self.uname
						if posixpath.exists(fname):
							posix.unlink(fname)
					else:
						fname = '/dev/null'
					self._record_selectfile(fname)
				else:
					if self._record_selectfile() is None:
						Logger('pype: run aborted\n')
						return

				# If elog is in use, then at the end of each run insert
				# (or update, since force=1) data on this file in the
				# sql database.
				# Do this at the START of the run so it can be seen right
				# away..
				if self.use_elog and not temp:
					import elogapi
					(ok, ecode) = elogapi.AddDatafile(
						self._exper,
						self.sub_common.queryv('full_subject'),
						self.uname,
						self.record_file,
						self.task_name,
						force=1)
					if not ok:
						warn('pype:_start_helper:elog', ecode)
					#del self._exper

				if self.xdacq == 'plexon':
					warn('pype:_start_helper:xdacq',
						 'Start plexon now', wait=1)
				elif self.xdacq == 'tdt':
					# start new block in current tank, this includes resting the
					# trial counter..
					(server, tank, block) = self.tdt.newblock(record=1)
					Logger('pype: tdt data = %s %s\n' % (tank, block))

				self._allowabort = 1

				self.con()

				# clear/reset result stack at the start of the run..
				self.set_result()

				# reset histogram/stats at start of run
				self.update_rt()		  # RT histogram
				self.update_psth()		  # PSTH (spike data)
				self._runstats_update(clear=1) # clear block stats

				# make sure graphic display is visible
				if self.psych:
					self.fb.screen_open()


				# call task-specific start function.
				self.set_state(running=1, paused=0, led=1)
				self.warn_run_start()
				self.con()				# clear console window
				self._startfn(self)
			except:
				reporterror(dbug=self.config.iget('DBERRS'))
			finally:
				self.record_done()
				self.set_state(running=0, paused=0, led=0)
				self.warn_run_stop()
				if self.psych:
					self.fb.screen_close()

				# either there was an error OR the task
				# completed normally, ensure proper cleanup
				# gets done:
				dacq_set_pri(0)
				dacq_set_mypri(0)
				dacq_set_rt(0)
				for w in (self._named_start, self._temp_start,
						  self.reloadbut, self.prevtaskbut,):
					w.config(state=NORMAL)
				self._stop.config(state=DISABLED)
				self._stopnow.config(state=DISABLED)
				self.showtestpat()
				self._allowabort = 0
				self._loadmenu.enableall()

			if self.xdacq == 'plexon':
				warn('pype:_start_helper:xdacq',
					 'Stop plexon now', wait=0)
			elif self.xdacq == 'tdt':
				# recording's done -- direct output back to TempBlk
				self.tdt.newblock(record=0)


	def query_ncorrect(self):
		"""Get number of correct (C) trials since run start

		:return: (int) C count

		"""
		return self._runstats['ncorrect']

	def query_nerror(self):
		"""Get number of errors (E,M) trials since run start

		:return: (int) E|M count

		"""
		return self._runstats['nerror']

	def query_nui(self):
		"""Get number of (sequential) uninitiated (U) trials since run start

		:return: (int) UI count

		"""

		return self._runstats['nui']

	def query_ntrials(self):
		"""Get number of trials since run start.

		Number of trials is sum of C, E and M types (corrects, errors
		and maxrt_exceeded, typically). Doesn't count UI or USERABORT
		trials.

		:return: (int) trial count

		"""
		return self._runstats['ncorrect'] + self._runstats['nerror']

	def _new_cell(self):
		if self.use_elog:
			warn('pype:_new_cell',
				 'Use elog "Edit>New Experiment" and then File>Save.')
		else:
			try:
				n = int(self.sub_common.queryv('cell'))
				n = n + 1
				self.sub_common.set('cell', "%d" % n)
			except ValueError:
				warn('pype:_new_cell',
					 'cell field is non-numeric, can''t increment.')

	def set_startfn(self, startfn, updatefn=None, validatefn=None):
		"""Set start run function/hook.

		The task_module.main() function must call this function to bind
		the startup function for the task. The main function can optionall
		also bind an update function that gets called after each trial. The
		update function can be used to update task-specific plots etc.

		The startfn must be a function that takes at least one argument,
		namely the PypeApp struction that acts as a handle for everything
		else (aka 'app'). Additional parameters can be included by using
		a lambda expression, for example:

		>>> t = Task(...)
		>>> app.set_startfn(lambda app, mytask=t: mystart(app, mytask))

		The return value from the start function is ignored.

		The updatefn is similar. It should be a function takes at least
		two parameters, first is 'app', second either None or a tuple.
		None for a pre-run initialization stage and a tuple with
		the info provided to record_write(), i.e.:

		>>> resultcode, rt, params, taskinfo = info

		You can do whatever you want, but if you are overriding the
		built-in RT histogram stuff (in which case it might be useful
		to know that app.rtdata contains a list of all the RTs for the
		current run) the updater shoudl return False. If it returns
		True, the built-in histogram will get updated IN ADDITION to
		whatever you did..

		validatefn (new 10/4/2013) is called before the run actually
		starts to give task chance to validate parameters, cache stimuli
		etc. Should return 'True' if pype should continue on and start
		task, 'False' to abort run.

		"""

		self._startfn = startfn
		self._updatefn = updatefn
		self._validatefn = validatefn	# called before start to validate params

	def _shutdown(self):
		"""Internal shutdown function.

		Sets the terminate flag in this instance of PypeApp. This
		will eventually cause the PypeApp to exit, once the current
		run is stopped.

		Should *never* be called by user/application directly.

		"""
		if self.running:
			if self.tk:
				self.tk.bell()
		else:
			self._savestate()			# Do this NOW!
			Logger('pype: user shutdown/close -- terminating.\n')
			self.terminate = 1

	def ts(self):
		"""Get current timestamp.

		:return: (ms) current 'time', as determined by the DACQ module.

		"""
		return dacq_ts()


	def dotrialtag(self, reset=None):
		try:
			tag = self.trialtag
		except AttributeError:
			self.trialtag = 0
			tag = self.trialtag

		if reset is None:
			ts = self.encode('TRIAL_TAG')
			self.con('[trial tagged @ %d]' % ts)
			self.trialtag = 1
		else:
			self.trialtag = 0
			return tag

	def eye_txy(self):
		"""Query current eye position (last sample and time of sample)

		:return: measurement_time_ms, xpos_pix, ypos_pix

		"""

		ts = dacq_ts()
		if (self._last_eyepos) is None or (ts > self._last_eyepos):
			self._eye_x = dacq_eye_read(1)
			self._eye_y = dacq_eye_read(2)
			self._last_eyepos = ts
		return (self._last_eyepos, self._eye_x, self._eye_y)

	def eyepos(self):
		"""Query current eye position (last sample, no time)

		:return: xpos_pix, ypos_pix

		"""
		(t, x, y) = self.eye_txy()
		return (x, y)

	def looking_at(self, x=None, y=None):
		"""Tell pype where the monkey's supposed to be looking.

		This is crucial for the F8 key -- when you hit F8 telling
		pype to rezero the eyeposition, it assumes that the monkey
		is looking at this location (in pixels) when you strike the
		key.

		:param x: (int or FixWin) - x position (pix) or a fixwin object

		:param y: (int) - y position (pix); only if x is not a fixwin!

		:return: nothing

		"""
		if x is None and y is None:
			x = y = 0
		elif y is None:
			# assume x is a fixwin object -- sz is ignored..
			x, y, sz = x.get()
		self._eyetarg_x = x
		self._eyetarg_y = y

	def eyeshift(self, x=0, y=0, reset=False, zero=False, rel=True):
		"""Adjust X & Y offsets to set DC-offsets for eye position.

		- if (reset) --> set x/y offsets to (0,0)

		- if (zero)	 --> set x/y offset to current gaze position

		- otherwise --> shift the offsets by (x*xincr, y*yincr); use a
		  lambda expression if you want to shift in a callback
		  function to set the options.

		"""
		if reset:
			x = 0
			y = 0
		elif zero:
			(x0, y0) = (dacq_eye_read(1), dacq_eye_read(2))
			x = float(self.ical.queryv('xoff_')) + x0 - self._eyetarg_x
			y = float(self.ical.queryv('yoff_')) + y0 - self._eyetarg_y
		elif rel:
			x = float(self.ical.queryv('xoff_')) + x
			y = float(self.ical.queryv('yoff_')) + y
		else:
			# assume eye is looking at specified point -- for mouse clicks!
			(x0, y0) = (dacq_eye_read(1), dacq_eye_read(2))
			x = float(self.ical.queryv('xoff_')) + x0 - x
			y = float(self.ical.queryv('yoff_')) + y0 - y
		self.eyeset(xoff=x, yoff=y)
		self.encode(EYESHIFT)

	def idlefn(self, ms=None, update=1, toplevel=None, fast=None):
		"""Idle function -- call when there's nothing to do to update GUI.

		The idle function -- this function should be call periodically
		by everything.	Whenever the program's looping or busy waiting
		for something (bar to go up/down, timer to expire etc), the
		app should just call idlefn().	The optional ms arg will run
		the idle function for the indicated amount of time -- this is
		not accurate; it just uses the tk after() command, so it's
		X11 limited and only approximate.

		This function is also responsible for monitoring the GUI's
		keyboard queue and handling key events.	 Right now only some
		basics are implemented -- give a drop of juice, open/close
		solenoid, run/stop etc.. more can be implemented and eventually
		there should be a way to set user/app specific keybindings
		just like the user buttons.

		*NB* anywhere this is called you **MUST** catch the UserAbort
		exception!!!

		"""
		import pygame

		if self._post_fixbreak:
			self._post_fixbreak = 0
			raise FixBreak
		if self._post_bartransition:
			self._post_bartransition = 0
			raise BarTransition
		if self._post_joytransition:
			self._post_joytransition = 0
			raise JoyTransition
		if self._post_alarm:
			self._post_alarm = 0
			raise Alarm

		if len(self.idle_queue):
			now = dacq_ts()
			# note: work with copy, to avoid problems with 'remove' below..
			for (deadline, action) in self.idle_queue[:]:
				if (deadline - now) <= 0:
					self.idle_queue.remove((deadline, action))
					action()

		if fast:
			return

		if (not self.recording) and (self.plex is not None):
			# drawin the plexon buffer to prevent overflow when
			# pype is idle...
			tank, ndropped = self.plex.drain()
			if tank is None:
				Logger('pype: lost plexon signal.. this is bad..')

		if self.tk is None:
			if not ms is None:
				t = Timer()
				while t.ms() < ms:
					pass
		elif ms is None:
			# If gamepad/joystick attached -- use as follows:
			#  0,1,2,3 --> SIMULATED DIGITAL I/O LINES (comedi_server handles)
			#  4,5,6,7 --> special functions, see below
			# NOTE: 0,1,2.. refers to "labels" 1,2,3...
			#
			# 0 ("1"): Response Bar
			# XX 1 ("2"): Juice squirter (aka SW1)
			# XX 2 ("3"): userdefined switch 2 (aka SW2)
			# 3 ("4"): not used
			# 4 ("5"): alternate stop button
			# 5 ("6"): alternate F8 (zero eye tracker)
			# 6+7 ("7"+"8"): emergency quit hotkey
			if dacq_jsbut(-1):
				if dacq_jsbut(4):
					if self.running:
						self._start_helper()
				elif dacq_jsbut(5):
					self.eyeshift(zero=1)
				elif dacq_jsbut(6) and dacq_jsbut(7):
					sys.stderr.write('JOYSTICK PARACHUTE DEPLOYED!\n')
					sys.exit(0)

			if self._doabort and self._allowabort:
				# user hit abort/stop button -- this will abort next
				# time task calls idlefn...
				self._doabort = 0
				raise UserAbort

			# process keys from the TkInter GUI (user display etc)
			(c, ev) = self.tkkeyque.pop()
			if c:
				c = string.lower(c)
				if c == 'escape':
					if self._allowabort:
						self.con("[esc]", color='red')
						raise UserAbort
				elif c == 'f4':
					self.reward()
				elif c == 'f8':
					self.eyeshift(zero=1)
				elif c == 'f7' and self.running:
					self.dotrialtag()

			# process keys from the framebuffer window
			if 'f8' in self.fb.checkkeys():
				self.eyeshift(zero=1)
				self.con('framebuffer:f8')
				while not self.fb.checkkeys() == []: pass
			elif 'escape' in self.fb.checkkeys():
				if self._allowabort:
					self.con('framebuffer:esc')
					while not self.fb.checkkeys() == []: pass
					self.con("[esc]", color='red')
					raise UserAbort

			while 1:
				pev = pygame.event.poll()
				if pev.type is pygame.NOEVENT:
					break
				elif pev.type is pygame.KEYDOWN and \
					(pev.key < 256) and (pev.mod & pygame.KMOD_ALT) and \
					unichr(pev.key) == u's' and self._allowabort:
					self.con("stopping run", color='red')
					self.running = 0
					raise UserAbort
				elif self.eyemouse:
					doint = 0
					if pev.type is pygame.MOUSEBUTTONDOWN and pev.button==1:
						self.eyeshift(x=pev.pos[0] - (self.fb.w/2),
									  y=(self.fb.h/2) - pev.pos[1], rel=False)
					elif pev.type is pygame.KEYDOWN and unichr(pev.key) == u' ':
						if ~self.eyebar:
							doint = 1
						self.eyebar = 1
					elif pev.type is pygame.KEYUP and unichr(pev.key) == u' ':
						if self.eyebar:
							doint = 1
						self.eyebar = 0
					if doint:
						# simulated barTransition..
						self._int_handler(None, None, iclass=1, iarg=0)

			x, y = self.eyepos()
			if (x is not None) and (y is not None):
				self.udpy.eye_at(x, y, xt=self._show_xt_traces.get())

			if update:
				self.tk.update()

			if self.taskidle:
				self.taskidle(self)

			self._show_stateinfo()

		else:
			t = Timer()
			while t.ms() < ms:
				self.idlefn()

	def _drain(self):
		"""Open solenoid to drain juicer.

		"""
		if not self.running:
			self._juice_on()
			w = warn('pype:_drain', 'Juicer is open!')
			self._juice_off()

	def _history(self, code=None):
		"""
		Displays subject's recent history (based on result
		codes). Call with no args to clear/reset, string/char
		to push a trial onto the stack. Shouldn't be called
		by users; users should call set_result instead.

		"""

		MAXHIST = 40
		if (code is None) or (len(code) == 0):
			self._histstr = ''
		else:
			self._histstr = (self._histstr + code[0])[-MAXHIST:]

		if self.tk:
			self._hist.config(text='results: ' + self._histstr)

	def warn_run_start(self):
		if self.sub_common.queryv('warningbeeps'):
			for n in range(3):
				beep(1000, 100)
				beep(0, 10)

	def warn_run_stop(self):
		if self.sub_common.queryv('warningbeeps'):
			beep(1000, 100)
			beep(500, 100)

	def warn_trial_correct(self, flash=None):
		"""Give positive (auditory+visual) feedback for correct response.

		:param flash: (ms) duration of GREEN flash or None for no flash

		:return: nothing

		"""
		beep(3000, 250, wait=0)
		if flash:
			self.fb.clear((0, 255, 0), flip=1)
			self.idlefn(flash)
			self.fb.clear((1, 1, 1), flip=1)
		pass

	def warn_trial_incorrect(self, flash=None):
		"""Give negative (auditory+visual) feedback for error response.

		:param flash: (ms) duration of RED flash or None for no flash

		:return: nothing

		"""
		beep(500, 500, wait=0)
		if flash:
			self.fb.clear((255, 0, 0), flip=1)
			self.idlefn(flash)
			self.fb.clear((1, 1, 1), flip=1)

	def dropsize(self):
		"""Query dropsize.

		:return: (ms) mean dropsize

		"""
		return self.sub_common.queryv('dropsize')

	def dropvar(self):
		"""Query dropsize variance.

		:return: (ms) dropsize variance

		"""
		return self.sub_common.queryv('dropvar')

	def reward(self, dobeep=1, multiplier=1.0, ms=None):
		"""Give reward.

		Deliver a squirt of juice based on current dropsize and
		dropvar settings.

		:return: (ms) actual size of delivered reward

		"""

		# if var==0, then ms is the exact time of the drop, if var>0
		# then drop time is selected randomly from a normal distribution
		# with mean=ms, std=var

		# becasue the distribution is normal, very small and very
		# large numbers can (rarely) come up, so you MUST clip the
		# distribution to avoid pype locking up in app._reward_finisher()...

		if ms is None:
			ms = int(round(multiplier * float(self.dropsize())))
			sigma = self.dropvar()**0.5
		else:
			# user specified ms, no variance
			sigma = 0

		if ms == 0:
			return

		maxreward = self.sub_common.queryv('maxreward')
		minreward = self.sub_common.queryv('minreward')

		if sigma > 0:
			while 1:
				t = nrand(mean=ms, sigma=sigma)
				if (t > minreward) and (t < maxreward):
					break
			if dobeep and self.reward_beep:
				beep(1000, 40)
			thread.start_new_thread(self._reward_finisher, (t,))
			if self.tk:
				self.con("[ran-reward=%dms]" % t, color='black')
			actual_reward_size = t
		else:
			if dobeep and self.reward_beep:
				beep(1000, 100)
			self._juice_drip(ms)
			if self.tk:
				self.con("[reward=%dms]" % ms, color='black')
			actual_reward_size = ms
		self._tally(reward=actual_reward_size)
		self.dropcount = self.dropcount + 1

		# Fri Dec  8 14:02:49 2006 mazer
		#  automatically encode the actual reward size (ms open) in
		#  the data file
		self.encode('ACT_' + REWARD + '%d' % actual_reward_size)

		return actual_reward_size

	def _reward_finisher(self, t):
		"""
		This is ONLY to be called from inside reward(), not a user-visble
		function. The point is to call _juice_drip() in a separate thread
		and to block over rewards from being delivered until this one's
		finished.

		"""
		self._rewardlock.acquire()
		self._juice_drip(t)
		self._rewardlock.release()

	def _juice_on(self):
		"""Open juice solenoid.

		"""
		dacq_juice(1)

	def _juice_off(self):
		"""Close juice solenoid.

		"""
		dacq_juice(0)

	def _juice_drip(self, ms):
		dacq_juice_drip(int(round(ms)))

	def barchanges(self, reset=None):
		"""Count touch bar transitions.

		Reset (ie, barchanges(reset=1)) once the bar's been grabbed
		and then monitor with barchanges() to see if the count
		increases. Count incremewnts each time there's a state change
		(0->1 or 1->0). Sampled at DACQ frequency (~1khz), so as to
		avoid loosing signals during CPU intensive graphics.

		:return: (boolean)

		"""
		if reset:
			return dacq_bar_transitions(1)
		else:
			return dacq_bar_transitions(0)

	def bar_genint(self, enable=1):
		"""Enable/disable exceptions (aka interrupts) when the touch
		bar is touched.

		If this is enabled, then the das_server will generate a SIGUSR1
		interupt each time the bar changes state.  This gets caught
		by an internal function and converted into a python
		exception: BarTransition.

		**Don't even think about calling this outside a try/except
		wrapper to catch the BarTransition exception, or you will have
		serious problems!**

		"""
		if enable:
			self._post_bartransition = 0
			dacq_bar_genint(1)
		else:
			dacq_bar_genint(0)
			# also: clear saved flag -- no more interupts
			# in theory you could loose a pending interupt here, but it
			# should be unlikely.
			self._post_bartransition = 0

	def joy_genint_getbutton(self):
		return self._joypad_intbut

	def joy_genint(self, enable=1):
		"""Enable/disable exceptions (aka interrupts) for joypad input

		If this is enabled, then the das_server will generate a SIGUSR1
		interupt each time a joypad button, other than #1, is pressed.
		When you call with enable=1, it will check to make sure no
		buttons are currently pressed -- if there are, it will return
		None and you need to try again..
		**Don't even think about calling this outside a try/except
		wrapper to catch the JoyTransition exception, or you will have
		serious problems!**

		:param enable: (bool) enable interupt generation -- when enabling
				ints, check return value to make sure call succeeded.

		:return: if enable is set, flag indicating whether or not ints were
				actuall enabled (see notes above)
		"""

		if enable:
			for n in range(10):
				if dacq_jsbut(n):
					return None
			self._joypad_intbut = None
			self._post_joytransition = 0
			dacq_joy_genint(1)
			return 1
		else:
			dacq_joy_genint(0)
			# also: clear saved flag -- no more interupts
			# in theory you could loose a pending interupt here, but it
			# should be unlikely.
			self._post_joytransition = 0

	def set_alarm(self, ms=None, clear=None):
		"""Set an interupt/exception alarm to go off.

		An **Alarm** exception will be generated when the timer
		expires. Exception will be raised from idlefn() at next
		available opportunity, so you must periodicall call idlfn()
		once you set the alarm.

		*NB* This requires app.allow_ints to be true in order to work!

		*NB* only one alarm	is allowed at a time.

		:param ms: (ms) ms from now for alarm to go off

		:param clear: (boolean) clear existing alarm

		:return: nothing

		"""
		if ms:
			dacq_set_alarm(ms)
		elif clear:
			dacq_set_alarm(0)

	def interupts(self, enable=None, queue=None):
		"""Enable or disable interupts from comedi_server.

		:param enable: (boolean) Enable or disable interupts. Use None to
				leave current setting alone

		:param queue: (boolean) if true, then interupts are queued and
				handled by idlefn(). Otherwise they are raised
				immediately and must be caught.	 Use None to
				leave current setting alone

		:return: tuple of current interupt status: (enable, queue)

		"""

		if not (enable is None):
			self.allow_ints = enable
		if not (queue is None):
			self._queue_ints = queue

		return (self.allow_ints, self._queue_ints)

	def _int_handler(self, signal, frame, iclass=None, iarg=None):
		"""This is for catching SIGUSR1's from the dacq process.

		"""

		if iclass is None:
			iclass = dacq_int_class()
		if iarg is None:
			iarg = dacq_int_arg()

		# print 'INT', iclass, iarg

		if iclass == 666:
			self.running = 0
			warn('eyelink', 'Lost eyelink connection!', wait=0)
			return

		# for INT_FATAL interupts -- handle regardless of allow_ints
		# flag -- this probably means eyelink connection died..
		if not self.allow_ints:
			# interupts are disabled -- do nothing
			return

		# latch interupts off -- must explictly enable interupts to use again
		self.allow_ints = 0

		# class/arg is:
		#	1: DIN transition (arg is input # that changed; bar==0)
		#		--> this is also joypad/stick button #1 presses
		#	2: fixwin break (arg is meaningless -- always 0)
		#	3: alarm expired (arg is meaningless -- always 0)
		#	4: joypad/stick transition (button # > 1)
		self.lastint_ts = dacq_ts()

		if iclass == 1:
			if iarg == 0:
				dacq_release()
				if self._queue_ints:
					self._post_bartransition = 1
				else:
					raise BarTransition
		elif iclass == 4:
			dacq_release()
			self._joypad_intbut = iarg+1
			if self._queue_ints:
				self._post_joytransition = 1
			else:
				raise JoyTransition
		elif iclass == 2:
			dacq_release()
			if self._queue_ints:
				self._post_fixbreak = 1
			else:
				raise FixBreak
		elif iclass == 3:
			dacq_release()
			if self._queue_ints:
				self._post_alarm = 1
			else:
				raise Alarm
		else:
			sys.stderr.write('Stray SIGUSR1: iclass=%d iarg=%d\n',
							 (iclass, iarg))
			self.allow_ints = 1
			return

	def bardown(self):
		"""Query to see if touchbar is touched (aka 'down').

		"""
		if self.flip_bar:
			if self.eyemouse:
				return not self.eyebar
			else:
				return not dacq_bar()
		else:
			if self.eyemouse:
				return self.eyebar
			else:
				return dacq_bar()

	def barup(self):
		"""Query to see if touchbar is touched (aka 'down').

		"""
		return not self.bardown()

	def joybut(self, n):
		"""Query the nth joystick button (starting with #0, aka B1).

		Joystick labels are labeled starting with B1, while indexing
		in pype starts at 0. So to query the button labeled "1", you
		need to do *joybut(0)*.

		To make life easier -- this will also accept keys 1,2,3.. as
		standins for B1,B2 so you can run without a joystick/keypad.

		:return: (bool) up or down status

		"""
		return dacq_jsbut(n) or ('%d'%(n+1)) in self.fb.checkkeys()

	def joyaxis(self):
		"""Query the joystick axis state.

		:return: (xpos, ypos)

		"""
		return (dacq_js_x(), dacq_js_y())

	def setgeo(self, w=None, default=None, load=None, loadempty=None,
			   save=None, posonly=0):
		"""Manage window geometry database (sticky across sessions).

		:param w: (widget) widget to query -- title string is use as key!

		:param default: (str) default geom if not in DB (WxH+X+Y)

		:param load: (bool) load database from ~/.pyperc/winpos

		:param loadempty: (bool) initialize empty database. This is to
				force a reset of all window positions to retrieve windows
				that might appear off screen!

		:param save: (bool) save database to ~/.pyperc/winpos

		:param posonly: (bool) only use position info

		:return: nothing
		"""

		filename = pyperc('winpos')

		if loadempty:
				self._winpos = {}
		elif load:
			try:
				self._winpos = cPickle.load(open(filename, 'r'))
			except IOError:
				self._winpos = {}
				pass
			except EOFError:
				self._winpos = {}
				pass
		elif save:
			wlist = []
			wlist.append(self.tk)
			for k in self.tk.children.keys():
				wlist.append(self.tk.children[k])

			for w in wlist:
				try:
					geo = w.geometry()
					if not geo[0:3] == '1x1':
						self._winpos[w.title()] = geo
				except AttributeError:
					pass

				cPickle.dump(self._winpos, open(filename, 'w'))
		else:
			try:
				geo = self._winpos[w.title()]
				if geo[0:3] == '1x1':
					raise KeyError
				if posonly:
					geo = "".join(re.compile('[+-][0-9]+').findall(geo)[-2:])
				w.geometry(geo)
			except KeyError:
				if default:
					w.geometry(default)

	def close(self):
		"""Call to initiate pype shutdown.

		Completely close and cleanup application -- shutdown the DACQ
		interface and framebuffer and restore the X11 bell etc.

		"""
		self.unloadtask()

		if self._testpat: del self._testpat

		if self.fb:
			del self.fb
			# turn bell and screensaver back on -- this isn't really
			# quite right -- it always gets turned back on, even if they
			# weren't on to start with..
			d = self.config.get('SDLDPY')
			os.system("xset -display %s b on" % d)
			os.system("xset -display %s s on" % d)
			os.system("xset -display %s +dpms" % d)

		if self.dacq_going:
			dacq_stop()
			dacq_going = 0

		if self.plex is not None:
			self.plex.drain(terminate=1)
			Logger('pype: closed connection to plexon.\n')

		try:
			self.udpy.fidinfo(file=subjectrc('last.fid'))
			self.udpy.savepoints(subjectrc('last.pts'))
		except AttributeError:
			pass

		if self.tk:
			# only do the state thing if in GUI mode
			self._savestate()
			Logger('pype: saved state.\n')
		Logger('pype: bye bye.\n')

	def repinfo(self, msg=None):
		"""Set trial/block/repetition information in the GUI window.

		:param msg: (string) Short bit of text stick in the window. If
				called with no args or msg==None, clear the window.

		:return: nothing

		"""
		self._repinfo.configure(text=msg)

	def taskname(self):
		"""Query name of task.

		:return: (string) current task name (no extension) or none.

		"""
		return self._taskname()


	def _taskname(self, taskname=[], path=[]):
		"""Query or set name of task.

		:param taskname: (string) set/clear task name

		:param path: (string) set/clear task source directory/path

		:return: (string) task name (no extension)

		"""
		if taskname == []:
			return self.task_name

		if taskname is None:
			self.task_name = None
			if self.tk:
				self._tasknamew.configure(text="task: <none>")
				self.balloon.bind(self._tasknamew, 'no task loaded')
		else:
			self.task_name = taskname
			self.task_dir = path
			if self.tk:
				self._tasknamew.configure(text="task: %s" % self.task_name)
				self.balloon.bind(self._tasknamew,
								  'src: %s/%s.py' % (self.task_dir,
													 self.task_name))

	def _set_recfile(self):
		if self.tk:
			if self.record_file is None:
				self._recfile.config(text="datafile: <none>")
				self.balloon.bind(self._recfile, 'no datafile open')
			else:
				if len(self.record_file) > 40:
					spacer = "..."
				else:
					spacer = ""
				self._recfile.config(text="datafile: %s%s"
									  % (spacer, self.record_file[-25:]))
				self.balloon.bind(self._recfile, self.record_file)

	def set_userbutton(self, n, text=None, check=None, command=None):
		"""Set callback and label for user-defined buttons.

		"""
		if check:
			c = Checkbutton(self._userbuttonframe,
							text=text, relief=RAISED)
		else:
			c = Button(self._userbuttonframe,
					   text=text, relief=RAISED, command=command)
		c.pack(expand=0, fill=X, side=TOP, pady=2)
		return c

	def taskbutton(self, text=None, check=None, command=None, size=8):
		"""Create a task-button in the GUI and link to command.

		"""
		if check:
			c = Checkbutton(self._userbuttonframe,
							text=text, anchor=W, relief=RAISED)
		else:
			c = Button(self._userbuttonframe,
					   text=text, anchor=W, relief=RAISED, command=command)
		c.pack(expand=0, fill=X, pady=2)

		return c

	def record_start(self):
		"""Start recording data.

		Clear the per-trial recording buffer and reset the per-trial
		timer.	This should be called at the start of every trial,
		always at the same point in the trial.	All per-trial
		timestamps (encodes and datastreams) will be timestamped
		relative to this call (which will be t=0).

		"""

		# bump up the data collect process priorities
		dacq_set_pri(self.rig_common.queryv('dacq_pri'))
		dacq_set_mypri(self.rig_common.queryv('fb_pri'))
		if self.rig_common.queryv('rt_sched'):
			# if rt_sched is set in the rig menu, switch scheduler mode
			# to real time for the duration of the trial
			dacq_set_rt(1)

		self.record_buffer = []

		# Thu Oct 23 15:51:34 2008 mazer
		#
		# - The record_state() function can now block for 250ms to
		#	ensure that the plexon has time to register onset of new
		#	trial, therefore, the timestamp should be recorded when
		#	record_state() returns, not before it's called.
		#
		# - So the t=self.encode(START) has been moved from right
		#	before the self.record_state(1) to right after

		# tell plexon trial is BEGINNING
		self.record_state(1)
		if self.u3:
			self.u3.go()
		t = self.encode(START)

		# Mon Oct 27 12:56:47 2008 mazer
		# - log full 'time of day' for start event
		self.encode('TOD_START %f' % time.time())

		self.recording = 1

		# start with fresh eye trace..
		self.udpy.eye_clear()

		# save recording start time -- this is used to ensure
		# 250ms between start/stop events for proper plexon sync

	def record_stop(self):
		"""Stop recording data.

		End of trial clean up.

		"""

		# Thu Oct 23 15:53:43 2008 mazer
		# see note about re self.encode(START) -- this has been moved
		# to right AFTER the self.record_state(0) call to avoid
		# problems with plexon sync..

		self.udpy.eye_clear()

		# tell plexon trial is OVER
		self.recording = 0
		self.record_state(0)
		t = self.encode(STOP)
		if self.u3:
			self.u3.stop(wait=1)

		# Mon Oct 27 12:56:47 2008 mazer
		# - log full 'time of day' for start event
		self.encode('TOD_STOP %f' % time.time())

		# bump back down the data collect process priorities
		dacq_set_pri(0)
		dacq_set_mypri(0)
		dacq_set_rt(0)

		if self.plex is not None:
			self.xdacq_data_store = _get_plexon_events(self.plex, fc=40000)

	def status_plex(self):
		if self.plex is not None:
			Logger("pype: plexon units --")
			for (chan, unit) in self.plex.neuronlist():
				Logger(" sig%03d%c" % (chan, chr(ord('a')+unit)))
			Logger("\n")
		else:
			Logger("pype: plexnet not enabled.")

	def record_state(self, state):
		"""Enable or disable plexon (or other auxilliary recording
		system) state.

		This basically triggers the external recording system (plexon,
		TDT, etc) to start recording by changing the polarity on
		digitial output line 2.

		In the case of the plexon, a 250ms ITI imposed as well to
		make sure the plexon can keep up and there are no drop outs.
		This is known problem with the plexon -- if you strobe the
		gating signal faster than 250ms it can loose the strobe.

		"""

		try:
			l = self._last_recstate
		except:
			self._last_recstate = dacq_ts()

		if self.xdacq is 'plexon':
			warn = 1
			while (dacq_ts() - self._last_recstate) < 250:
				if warn:
					sys.stderr.write('warning: short ITI, stalling\n')
					warn = 0
		# this is (was?) causing a wedge!!!
		dacq_dig_out(2, state)
		self._last_recstate = dacq_ts()

	def eyetrace(self, on):
		"""Start/stop recording eye position data.

		Begin recording eye trace data now. Or, stop recording eye
		data now.  Be sure to call this before you save data with
		record_write() below!

		This idea is that you may not want to record eye position
		data until the fixation spot is acquired or the touchbar
		touched etc, so this provides fine grained control over
		storage of the eye pos data stream. You can start saving
		spike data first with record_start() and later start
		saving eye traces (although not *vice versa*).

		:param on: (boolean)

		:return: nothing

		"""
		if on:
			dacq_adbuf_toggle(1)
			self.encode(EYE_START)
			self._eyetrace = 1
		elif self._eyetrace:
			# only allow turn off once..
			self.encode(EYE_STOP)
			if dacq_adbuf_toggle(0):
				self.encode(EYE_OVERFLOW)
				Logger('pype: warning -- eyetrace overflowed\n')
				warn('pype:eyetrace', 'eye trace overflow')
			self._eyetrace = 0

	def encode(self, code=None, ts=None):
		"""Insert event code into the per-trial timestream.

		:param code: (string or tuple/lsit) Any string can be used, but
				it's best to use the constants defined in the
				pype.events module or a modified version of these for
				portability and to facilitate data analysis. If a
				sequence of strings is provided, all events will be
				inserted into the timesteam with the same (current)
				timestamp. If code is None, then it's a dummy encode
				that can be used to retrieve the current time.

		:param ts: (int) optional time in ms for enodes -- by default
				the current timestamp is used, but a timestamp can
				be provided to override (allowing multiple seqeuential
				encodes with the same timestamp)

		:return: (ms) actual event timestamp

		"""

		if ts is None:
			ts = dacq_ts()

		if code is not None:
			if (type(code) is TupleType) or (type(code) is ListType):
				# Mon Aug 19 12:27:30 2013 mazer
				# this worked only for tuples, should also work for lists now.
				for acode in code:
					if len(acode) > 0:
						self.record_buffer.append((ts, acode))
			else:
				if len(code): self.record_buffer.append((ts, code))

		return ts

	def get_encodes(self):
		return self.record_buffer

	def get_spikes_now(self):
		"""Query current set of spike times for this trial.

		This is gets the spike data out from the ad/ad server in
		mid-trial. You can use this to do on-line statistics or
		generate dynamic stimuli etc.  It should not be considered
		final data -- this is only an approximation, particularly if
		you're still recording data when you call this.

		:return: (array) array of spike times

		"""
		n = dacq_adbuf_size()
		t = np.zeros(n, np.float)
		s0 = np.zeros(n, np.int)

		for i in range(0,n):
			t[i] = dacq_adbuf_t(i) / 1000.0
			s0[i] = dacq_adbuf_c3(i)

		spike_thresh = int(self.rig_common.queryv('spike_thresh'))
		spike_polarity = int(self.rig_common.queryv('spike_polarity'))
		spike_times = _find_ttl(t, s0, spike_thresh, spike_polarity)

		return spike_times

	def find_saccades(self, thresh=2, mindur=25, maxthresh=None,
					  start=None, stop=None):
		"""Find saccades in mid-trial.

		Retreives the eye trace data using get_eyetrace_now() and then
		calls pypedata.find_saccades with the specified parameters. *See
		documentation on pypedata.find_saccades() for algorithm/parameter
		details.*

		:param thresh: (pix/time) velocity threshold for saccade detection

		:param mindur: (ms) minimum allowable separation between saccades

		:param maxthresh: (pix/time) anything over this velocity (if
				specified) is a blink.

		:param start: (ms) time/timestamp to start looking

		:param stop: (ms) time/timestamp to stop looking

		:returns: (list of tuples) See pypedata.find_saccades().

		"""

		(t, x, y) = self.get_eyetrace_now()

		#ppd = self.rig_common.queryv("mon_h_ppd") # float
		#thresh = thresh * ppd
		#if maxthresh: maxthresh = maxthresh * ppd
		if (not start is None) or (not stop is None):
			if start is None: start = 0
			if stop is None: stop = len(t)
			ix = np.greater_equal(t, start) & np.less(t, stop)
			t = t[ix]
			x = x[ix]
			y = y[ix]
		slist = find_saccades((t, x, y, None),
							  thresh=thresh,
							  mindur=mindur,
							  maxthresh=maxthresh)
		return slist

	def get_eyetrace_now(self, raw=0):
		"""Query current eye trace - note: was get_eyepos_now().

		This function extracts the current state of the x/y eye
		position buffers from the dacq_server NOW.	Like get_spikes()
		you can use this in mid-trial or at the end of the trial to
		adapt the task based on his eye movements.	This should NOT be
		considered the final data, particularly if you're still in
		record mode when you call this function

		:param raw: (bool) if true, then return the raw, uncalibrated
				eye trace data 'stored' in the first two analog channel
				streams.

		:return: (mult-val-ret) time, xpos, ypos arrays (up to current
				time)

		"""
		n = dacq_adbuf_size()
		t = np.zeros(n, np.float)
		x = np.zeros(n, np.int)
		y = np.zeros(n, np.int)

		for i in range(0,n):
			t[i] = dacq_adbuf_t(i) / 1000.0
			if raw:
				x[i] = dacq_adbuf_c0(i)
				y[i] = dacq_adbuf_c1(i)
			else:
				x[i] = dacq_adbuf_x(i)
				y[i] = dacq_adbuf_y(i)

		return (t, x, y)

	def get_phototrace_now(self):
		"""Query current photo trace - note: was get_photo_now().

		:return: (mult-val-ret) time, photodiode-voltage (up to
				current time)

		"""
		n = dacq_adbuf_size()
		t = np.zeros(n, np.float)
		p = np.zeros(n, np.int)

		for i in range(0,n):
			t[i] = dacq_adbuf_t(i) / 1000.0
			p[i] = dacq_adbuf_c2(i)

		return (t, p)

	def get_events_now(self):
		"""Query current event stream (encodes).

		:return: (array) *copy* of current encode buffer

		"""
		return self.record_buffer[::]

	def record_write(self, resultcode=None, rt=None,
					 params=None, taskinfo=None, returnall=False):
		"""Write the current record to the specified datafile.

		Call this at the end of each trial in your task to do
		post-processing and flush all the recorded data to disk.

		:param resultcode: (string)

		:param rt: (number) Reaction time in ns (or -1 for "not applicable")

		:param params: (dict) final dictionary of all parameters (including
				params added by the task as part of the data flow)

		:param taskinfo: (tuple) anything "extra" you want saved along with
				the rest of the trial data.

		:param returnall: (bool; def=False) return a copy of the full data
				struct written to the datafile.

		:return: if returnall is False, then return values is a tuple (time,
				photodiode-waveform, spike-waveform). Otherwise, it's simply
				a complete copy of the object written to the datafile, which
				includes ALL the available data.

		"""

		if (self.record_file == '/dev/null' and
					self.sub_common.queryv('fast_tmp')):
			fast_tmp = 1
		else:
			fast_tmp = 0

		# force taskinfo to be a tuple..
		if type(taskinfo) != TupleType:
			taskinfo = (taskinfo,)

		# stop eye recording, just in case user forgot.
		self.eyetrace(0)

		# clear the idlefn queue, just in case..
		self.queue_action()

		tag = self.dotrialtag(reset=1)

		n = dacq_adbuf_size()
		self.eyebuf_t = np.zeros(n, np.float)
		self.eyebuf_x = np.zeros(n, np.int)
		self.eyebuf_y = np.zeros(n, np.int)
		self.eyebuf_pa = np.zeros(n, np.int)
		self.eyebuf_new = np.zeros(n, np.int)
		p0 = np.zeros(n, np.int)
		s0 = np.zeros(n, np.int)

		# be careful here -- if you're trying to look at the photodiode
		# signals, you'd better not set fast_tmp=1...
		ndups = 0
		if not fast_tmp or self._show_eyetrace.get():
			if self.config.iget('save_raweye', 0):
				rawx = np.zeros(n, np.int)
				rawy = np.zeros(n, np.int)
			else:
				rawx = None
				rawy = None

			for i in range(0,n):
				# convert dacq_adbuf_t() in 'us' to 'ms' for saving
				self.eyebuf_t[i] = dacq_adbuf_t(i) / 1000.0
				self.eyebuf_x[i] = dacq_adbuf_x(i)
				self.eyebuf_y[i] = dacq_adbuf_y(i)
				self.eyebuf_pa[i] = dacq_adbuf_pa(i)
				self.eyebuf_new[i] = dacq_adbuf_new(i)
				p0[i] = dacq_adbuf_c2(i) # photo diode
				s0[i] = dacq_adbuf_c3(i) # spike detect
				if not rawx is None:
					rawx[i] = dacq_adbuf_c0(i)
					rawy[i] = dacq_adbuf_c1(i)

			###############################################################3
			# (starting) Thu Oct 21 14:38:49 2010 mazer
			# look for duplicates in the time stream -- this means
			# something's wrong with comedi_server or passing doubles
			# around...
			for i in range(1, n):
				if self.eyebuf_t[i-1] == self.eyebuf_t[i]:
					ndups = ndups + 1
			if ndups > 0:
				sys.stderr.write("warning: %d duplicate timestamp(s)\n" % ndups)
			#
			###############################################################3

		photo_thresh = int(self.rig_common.queryv('photo_thresh'))
		photo_polarity = int(self.rig_common.queryv('photo_polarity'))
		self.photo_times = _find_ttl(self.eyebuf_t, p0,
									  photo_thresh, photo_polarity)

		spike_thresh = int(self.rig_common.queryv('spike_thresh'))
		spike_polarity = int(self.rig_common.queryv('spike_polarity'))
		self.spike_times = _find_ttl(self.eyebuf_t, s0,
									  spike_thresh, spike_polarity)

		if self.u3:
			# here's problem: labjack timestamps are free running
			# clock monotonic.. pype's are zero'd to when comedi_server
			# was initialized!
			#
			# Mon Jan  7 15:12:15 2013 mazer
			#  this looks like the two are synced to within 0.7ms (LJ
			#  seems to lag the comedi stream by about 0.7 ms).
			(ut, a0, a1, a2, a3) = self.u3.get(t0=dacq_ts0())

			tmpf = open('foo.asc', 'w')
			for n in range(len(ut)):
				tmpf.write('%d %f %f\n' % (1, ut[n], a0[n],))
			for n in range(len(self.eyebuf_t)):
				tmpf.write('%d %f %f\n' % (0, self.eyebuf_t[n], p0[n],))
			tmpf.close()
		else:
			ut = []
			a0 = []

		self.update_rt((resultcode, rt, params, taskinfo))
		if 1 or resultcode[0] == CORRECT_RESPONSE:
			self.update_psth((self.spike_times, self.record_buffer))
		if self._updatefn:
			self._updatefn((resultcode, rt, params, taskinfo),
						   (self.spike_times, self.record_buffer))


		if self._show_eyetrace.get():
			self._plotEyetraces(self.eyebuf_t,
								self.eyebuf_x, self.eyebuf_y,
								((self.eyebuf_t, p0),),
								((self.eyebuf_t, s0), (ut, a0), ),
								self.spike_times)

		self.udpy.info("[%dspk %dsync %ddups]" %
					   (len(self.spike_times), len(self.photo_times), ndups,))

		# Completely wipe the buffers -- don't let them accidently
		# get read TWICE!!	They're saved as self/app.eyebuf_[xyt]
		# in case you wawnt them for something..
		dacq_adbuf_clear()

		# insert these into the param dictionary for later retrieval
		params['PypeBuildDate']	 = pypeversion.PypeBuildDate
		params['PypeBuildHost'] = pypeversion.PypeBuildHost

		# these are git/svn info (if available)
		params['PypeVersionInfo'] = pypeversion.PypeVersionInfo
		params['PypeVersionID'] = pypeversion.PypeVersionID

		# starting with pype3 (string set in mkpypeversion.sh)
		params['PypeVersion']  = pypeversion.PypeVersion

		# pype internal ('pi') -- user tagged this trial (f7)?
		params['piTrialTag'] = tag

		if not fast_tmp and self.record_file:
			# dump the event stream
			info = (resultcode, rt, params) + taskinfo

			# Wed Sep 11 14:36:42 2002 mazer
			#
			#  Structure of the saved record (mirrored in pypdata.py):
			#
			#  rec[0]		record type STRING: ('ENCODE' usually)
			#  rec[1]		info TUPLE: (resultcode, rt, paramdict, taskinfo)
			#						taskinfo can be ANYTHING user wants to
			#						save in the datafile
			#  rec[2]		event LIST: [(time, event), (time, event) ...]
			#  rec[3]		time VECTOR (list)
			#  rec[4]		eye x-pos VECTOR (list)
			#  rec[5]		eye y-pos VECTOR (list)
			#  rec[6]		LIST of photodiode time stamps
			#  rec[7]		LIST of spike time stamps
			#  rec[8]		record_id (SCALAR; auto incr'd after each write)
			#  rec[9]		raw photodiode response VECTOR
			#  rec[10]		raw spike response VECTOR
			#  rec[11]		TUPLE of raw analog channel data
			#				(chns: 0,1,2,3,4,5,6), but 2 & 3 are same as
			#				rec[9] and rec[10], so they're just None's in
			#				this vector to save space. c5 and c6 aren't
			#				currently implemented
			#  rec[12]		pupil area data (if available) in same format
			#				as the eye [xy]-position data above
			#				(added: 08-feb-2003 JAM)
			#  rec[13]		on-line plexon data via PlexNet. This should be
			#				a list of (timestamp, unit) pairs, with timestamps
			#				in ms and unit's following the standard plexon
			#				naming scheme (01a, 02a, 02b etc..)
			#				(added: rec[13] 31-oct-2005 JAM)
			#  rec[14]		eyenew data (added: Fri Apr	 8 15:27:34 2011 mazer )

			if self.xdacq == 'tdt':
				# insert tdt tank info into the parameter table for this
				# trial so we can recover the data later.
				(server, tank, block, tnum) = self.tdt.getblock()

				# str() here convert UTF8 strings back to plain old ascii,
				# which is the only thing the p2m can currently handle. small
				# risk here -- don't use international chars for datafile names!
				#
				# NOTE: first trial has tdt_tnum == 1, not zero!!!!
				#
				info[2]['tdt_server'] = str(server.encode('ascii'))
				info[2]['tdt_tank'] = str(tank.encode('ascii'))
				info[2]['tdt_block'] = str(block.encode('ascii'))
				info[2]['tdt_tnum'] = tnum

			rec = [
				ENCODE,
				info,
				self.record_buffer,
				_tolist(self.eyebuf_t),
				_tolist(self.eyebuf_x),
				_tolist(self.eyebuf_y),
				_tolist(self.photo_times),
				_tolist(self.spike_times),
				self.record_id,
				_tolist(p0),			# photo diode trace (analog)
				_tolist(s0),			# spike detect trace (TTL)
				(
					_tolist(rawx),		# raw eye position X
					_tolist(rawy),		# raw eye position Y
					None,				# was photo diode trace (dup!)
					None,				# was spike detect trace (dup!)
					None,
					None,
					None,
					),
				_tolist(self.eyebuf_pa),
				self.xdacq_data_store,
				_tolist(self.eyebuf_new),
				]

			f = open(self.record_file, 'a')
			labeled_dump('encode', rec, f, 1)
			f.close()

		self.record_id = self.record_id + 1

		if returnall:
			p = PypeRecord(None, 0, rec)
			p.compute()
			return p
		else:
			return (self.eyebuf_t, p0, s0)

	def record_split(self, rec):
		class Record(object):
			pass

		r = Record()
		r.resultcode = rec[1][0]
		r.rt = rec[1][1]
		r.params = rec[1][2]
		r.taskinfo = rec[1][3]
		r.evt = rec[2]
		r.t = rec[3]
		r.x = rec[4]
		r.y = rec[5]
		r.pa = rec[12]
		r.photo_times = rec[6]
		r.spike_times = rec[7]

		return r


	def record_note(self, tag, note):
		"""Insert note into current datafile.

		Try not to use this -- it's really obsolete and hard to parse!

		"""
		if self.record_file:
			rec = [NOTE, tag, note]
			f = open(self.record_file, 'a')
			labeled_dump('note', rec, f, 1)
			f.close()

	def _guess_fallback(self):
		"""Guess next filename/number by looking at files in CWD.

		"""

		subject = self.sub_common.queryv('subject')

		if self.training:
			cell = 0
		else:
			cell = self.sub_common.queryv('cell')

		try:
			pat = "%s%04d.*.[0-9][0-9][0-9]" % (subject, int(cell))
		except ValueError:
			pat = "%s%s.*.[0-9][0-9][0-9]" % (subject, cell)
		# generate list of files (including zipped files)
		flist = glob.glob(pat)+glob.glob(pat+'.gz')

		next = 0
		for f in flist:
			try:
				n = int(f.split('.')[2])
				if n >= next:
					next = n + 1
			except ValueError:
				pass

		try:
			return "%s%04d.%s.%03d" % (subject, int(cell),
									   self.task_name, next)
		except ValueError:
			return "%s%s.%s.%03d" % (subject, cell,
									   self.task_name, next)

	def _guess_elog(self):
		"""Guess next filename/number using elog.

		"""
		import elogapi

		animal = self.sub_common.queryv('subject')
		full_animal = self.sub_common.queryv('full_subject')

		if len(animal) == 0 or len(full_animal) == 0:
			warn('pype:_guess_elog',
				 "Set 'subject' and 'full_subject' parameters.")
			return None

		# search database based on full_animal (animal=full_subject)
		exper = elogapi.GetExper(full_animal)
		if exper is None:
			# create first experiment based on 'subject', ie, file prefix..
			exper = "%s%04d" % (animal, 1)
		# update cell slot in worksheets with exper
		self.sub_common.set('cell', exper)

		if self.training:
			exper = exper[:-4] + '0000'
		self._exper = exper

		# now find next avilable number in the sequence
		pat = "%s.*.[0-9][0-9][0-9]" % (exper, )
		# generate list of files (including zipped files)
		flist = glob.glob(pat)+glob.glob(pat+'.gz')

		next = 0
		for f in flist:
			try:
				n = int(f.split('.')[2])
				if n >= next:
					next = n + 1
			except ValueError:
				pass

		return "%s.%s.%03d" % (exper, self.task_name, next)


	def _guess(self):
		if self.use_elog:
			return self._guess_elog()
		else:
			return self._guess_fallback()


	def record_done(self):
		"""Let pype know run (*not* trial) is over.

		Call this function at the end of each run (ie, datafile) to
		let pype know it's ok to clean up and reset things for the
		next run.

		This really should be called "run_done".

		"""

		self.record_note('pype', 'run ends')
		self.record_file = None
		self._set_recfile()

	def _record_selectfile(self, fname=None):
		import filebox

		if not fname is None:
			self.record_file = fname
		else:
			self.record_file = None
			while 1:
				g = self._guess()
				if g is None:
					return None
				(file, mode) = filebox.SaveAs(initialdir=os.getcwd(),
											  pattern='*.[0-9][0-9][0-9]',
											  initialfile=g,
											  datafiles=1)
				if file is None:
					return None
				else:
					self.record_file = file

					if posixpath.exists(self.record_file):
						if mode == 'w':
							Logger('pype: unlinking: %s\n' % self.record_file)
							posix.unlink(self.record_file)
						elif mode == 'a':
							Logger('pype: appending to: %s\n' %
								   self.record_file)
					break

		self._set_recfile()
		self.record_note('pype', 'run starts')

		# stash the userparms dict in the file.. this contains
		# the monitor parameters, just in case they get lost
		# or forgotten..
		self.write_userparams()
		#self.record_note('userparams', self.config.dict)

		return 1

	def write_userparams(self):
		self.record_note('userparams', self.config.dict)

	def showtestpat(self):
		"""Idle the framebuffer (put up test pattern display).

		Not really for users -- this is really only used by the
		candy module to clear the screen when candy exits.

		"""
		if not self.fb: return

		if self._testpat is None:
			t = self.config.get('TESTPAT')
			if t and posixpath.exists(t):
				fname = t
			elif posixpath.exists(pyperc('testpat')):
				fname = pyperc('testpat');
			else:
				fname = self.pypedir + '/lib/testpat.png'
			s = Sprite(x=0, y=0, fname=fname, fb=self.fb, depth=99,
					   on=1, name='testpat')
			s.scale(self.fb.w, self.fb.h)
			self._testpat = s
		drawtest(self.fb, self._testpat)

	def plotEyetracesRange(self, start=None, stop=None):
		"""Set time range for useful portion of the eye trace.

		If these are set, then when the eye trace is plotted, the time
		range is restricted to this time frame to speed up
		plotting. Typically this is used to prevent looking at all the
		time while the animal's trying to acquire the fixspot, which
		isn't very interesting and may slow things down.

		"""

		self._show_eyetrace_start = start
		self._show_eyetrace_stop = stop

	def _plotEyetraces(self, t, x, y, p0, s0, raster):
		import pylab

		if len(t) < 1:
			return

		if self._show_eyetrace_start is not None:
			start = self._show_eyetrace_start
		else:
			start = t[0]

		if self._show_eyetrace_stop is not None:
			stop = self._show_eyetrace_stop
		else:
			stop = t[-1]

		t0 = t[0]
		skip = 1

		pylab.ion()
		pylab.figure(99)
		pylab.clf()

		pylab.subplot(4, 1, 1)
		pylab.plot(t[::skip] - t0, x[::skip], 'r-',
				   t[::skip] - t0, y[::skip], 'g-')
		pylab.xlim(start - t0, stop - t0)
		pylab.ylabel('X=RED Y=GRN')

		colors = 'krgbckrgbckrgbc'

		pylab.subplot(4, 1, 2)
		n = 0
		for (tt, p) in p0:
			pylab.plot(tt[::skip] - t0, p, colors[n]+'-')
			pylab.hold(True)
			n += 1
		pylab.hold(False)
		pylab.xlim(start - t0, stop - t0)
		pylab.ylabel('photo')


		pylab.subplot(4, 1, 3)
		n = 0
		for (tt, s) in s0:
			pylab.plot(tt[::skip] - t0, s, colors[n]+'-')
			pylab.hold(True)
			n += 1
		pylab.hold(False)
		#pylab.xlim(start - t0, stop - t0)
		pylab.ylabel('spikes')

		pylab.subplot(4, 1, 4)
		raster = np.array(raster) - t0
		pylab.plot(raster, 0.0 * raster, 'k.')
		pylab.ylim(-1,1)
		pylab.xlim(start - t0, stop - t0)
		pylab.ylabel('raster')
		pylab.draw()


	def update_rt(self, infotuple=None):
		import pylab

		if infotuple is None:
			self.rtdata = []
		else:
			resultcode, rt, params, taskinfo = infotuple
			if rt > 0:
				self.rtdata.append(rt)

		self.rthist.fig.clf()

		a = self.rthist.fig.add_subplot(1,1,1)

		if len(self.rtdata) == 0:
			a.text(0.5, 0.5, 'NO RT DATA',
				   transform=a.transAxes, color='red',
				   horizontalalignment='center', verticalalignment='center')
		else:
			h = np.array(self.rtdata)
			n, bins, patches = a.hist(h, facecolor='grey')
			a.text(0.02, 1-0.02,
				   '$\\mu=%.0fms$\n$\\sigma=%.0fms$\n$n=%d$' % \
				   (np.mean(h), np.std(h), len(h)),
				   color='red',
				   horizontalalignment='left',
				   verticalalignment='top',
				   transform=a.transAxes)

			x = np.linspace(bins[0], bins[-1], 25)
			g = pylab.normpdf(x, np.mean(h), np.std(h));
			g = g * np.sum(n) / np.sum(g)
			a.plot(x, g, 'r-', linewidth=2)
			a.axvspan(self.sub_common.queryv('minrt'),
					  self.sub_common.queryv('maxrt'),
					  color='b', alpha=0.25)
			a.axis([-10, 1.25*self.sub_common.queryv('maxrt'), None, None])
			a.set_ylabel('n=%d' % len(h))
		a.set_xlabel('Reaction Time (ms)')

		try:
			self.rthist.drawnow()
		except:
			if warn('matlibplot error',
					'Probably must delete ~/.matlibplot', once=True):
				reporterror()

	def update_psth(self, data=None, trigger=PSTH_TRIG):
		"""
		Note: this only adds to the psth if the trigger event is present.
		"""
		import pylab

		if self.psth is None: return

		if data is None:
			self.psthdata = np.array([])
		else:
			spike_times = np.array(data[0])
			events = data[1]
			t0 = find_events(events, trigger)
			if t0 == []:
				# no trigger event.. don't update..
				return
			else:
				self.psthdata = np.concatenate((self.psthdata, spike_times-t0,))

		self.psth.fig.clf()
		a = self.psth.fig.add_subplot(1,1,1)
		if len(self.psthdata) == 0:
			a.text(0.5, 0.5, 'NO SPIKE DATA',
				   transform=a.transAxes, color='red',
				   horizontalalignment='center', verticalalignment='center')
		else:
			# how histogram first 2s of data in 50 ms bins; this really
			# should be settable by the task..
			a.hist(self.psthdata, facecolor='blue',
				   bins=40, range=(-100, 1900))
		a.set_xlabel('Time (ms)')
		a.set_ylabel('nspikes')

		try:
			self.psth.drawnow()
		except:
			if warn('matlibplot error',
					'Probably must delete ~/.matlibplot', once=True):
				reporterror()

	def makeFixWin(self, x, y, tweak=0):
		"""Helper function for creating new fixation window in std way.

		Actual window size will be scaled up automatically from the
		base radius (subject_param:win_size) using subject_param:win_scale
		and eccentricity of the fixation window (relative to montior ctr).

		:param x,y: (pixels) center of fixation window

		:param tweak: (pixels) task-specific additive adjustment to radius

		:return: FixWin object

		"""

		# base fixwin radius in pixels + task-specific teak
		r = self.sub_common.queryv('win_size') + tweak

		# add eccentricity dependent adjustment factor:
		r = r + (self.sub_common.queryv('win_scale') * ((x**2 + y**2)**0.5))

		# vertical elongation factor (i.e., major/minor axis ratio)
		vbias = self.sub_common.queryv('vbias')

		return FixWin(x=x, y=y, size=int(round(r + adj)), app=self, vbias=vbias)

def getapp():
	"""Get global handle to running PypeApp.

	:returns: PypeApp instance or None (if PypeApp hasn't been instantiated)

	"""
	return PypeApp._instance

def _hostconfigfile():
	"""Get host-specific config file.

	Typically this is: $(PYPERC)/Config.{HOST_NAME}

	:return: (string) config filename

	"""
	h = socket.gethostname().split('.')[0]
	return pyperc('Config.%s' % h)

def _find_ttl(t, x, thresh=500, polarity=1):
	"""Find TTL pulses in x.

	*NB* this is backwards (ie, polarity=1 means negative going), but
	it's too late to change now..

	:param x: (vector) numpy waveform from dacq device

	:param thresh: (a2d units) threshold for detecting events in 'x'

	:param polarity: (in) >0 for negative going, <=0 for positive
		going pulses.

	:return: (list) time in ms of first samples above or below
		threshold (depending on value of polarity)

	"""

	times = []
	inpulse = 0
	if polarity > 0:
		for i in range(0, len(t)):
			if (not inpulse) and (x[i] < thresh):
				times.append(t[i])
				inpulse = 1
			elif inpulse and (x[i] > thresh):
				inpulse = 0
	else:
		for i in range(0, len(t)):
			if (not inpulse) and (x[i] > thresh):
				times.append(t[i])
				inpulse = 1
			elif inpulse and (x[i] < thresh):
				inpulse = 0
	return times

def _safeLookup(dict, key, default):
	"""Dictionary look up with a default value.

	:return: dict[key], if available, else default

	"""
	try:
		return dict[key]
	except (TypeError, KeyError):
		return default

def subject():
	"""Query subject id string.

	This is usually supplied by starting pype with the -s argument.

	:return: (string) subject id

	"""
	try:
		return os.environ['SUBJECT']
	except KeyError:
		return 'none'

def subjectrc(file=""):
	"""Query subject-specific config *directory*.

	Each subject should have a private directory for config and state
	files etc. By default this is ~/.pyperc/subj_id. The default can
	be altered by setting the $PYPERC environment variable.

	:return: (string) name of subject config directory

	"""
	return pyperc(os.path.join('_' + subject(), file))

def pyperc(file=""):
	"""Query config *directory*.

	By default this is ~/.pyperc, but can be overridden by
	setting the $PYPERC envronment var.

	:return: (string) name of .pyperc config directory

	"""
	if 'PYPERC' in os.environ:
		rcdir = os.environ['PYPERC']
	else:
		rcdir = os.path.join(os.path.expanduser('~'), '.pyperc')

	return os.path.join(rcdir, file)

class FixWin(object):
	"""Fixation Window Encapsulation

	Although this is a class and comedi_server supports multiple
	fixation windows, this class is hard coded to use window #0,
	so there can really only be one instantation at a time.

	User's should not really instantiate these directly any longer, but
	rather use app.makeFixWin() method.

	"""
	def __init__(self, x=0, y=0, size=10, app=None, vbias=1.0):
		self.app = app
		self.icon = None
		self.set(x, y, size)
		self.vbias = vbias				# ellipsoid: multiplicate scale of ydim
		self.fwnum = 0					# hard coded..

	def __del__(self):
		self.interupts(enable=0)		# disable interupt generation
		self.draw(clear=1)				# clear from user display

	def interupts(self, enable=0):
		"""Enable or disable interupts from this fixwin.

		Note: this simply allows one of the fixwins to generate
		interupts AS ALONG AS PYPE HAS INTERUPTS ENABLED! So, to
		activate this, you need to also make sure you call
		app.interupts(enable=1) as well, to enable global interupt
		handling.

		"""

		if enable:
			# clear any pending INT and then enable
			self._post_fixbreak = 0
			dacq_fixwin_genint(self.fwnum, enable)
		else:
			# disable, then clear any pending INTs
			dacq_fixwin_genint(self.fwnum, enable)
			self._post_fixbreak = 0

	def genint(self, enable=None):
		"""use interupts() method instead!"""
		self.interupts(enable=enable)
		warn('genint',
			 'fixwin.genint() obsolete -- change to fixwin.interupts()',
			 wait=None, action=None, once=1)

	def get(self):
		return self.x, self.y, self.size

	def set(self, x=None, y=None, size=None):
		"""Change (or set) size and position of fix window.

		Call on() method to update dacq process.

		:param x,y: (pixels) position parameters

		:param size: (pixels) window radius

		:return: nothing

		"""
		if not x is None: self.x = x
		if not y is None: self.y = y
		if not size is None: self.size = size

	def move(self, x, y, size=-1):
		"""Move fixwin

		Llike set, but for a live, active fixwin -- updates setting
		immediately without chaning the interupt/active state of the
		window. This is for implementing something like a pursuit
		tracker.

		:param x,y: (pixels) new position parameters (absolute, not relative!)

		:param size: (pixels) window radius (-1 for no change)

		:return: nothing

		"""
		if not x is None: self.x = x
		if not y is None: self.y = y
		if not size is None: self.size = size
		dacq_fixwin_move(self.fwnum, x, y, size)


	def reset(self):
		dacq_fixwin_reset(self.fwnum)

	def on(self):
		"""Tell comedi_server to monitor fixwin.

		:return: nothing

		"""
		dacq_fixwin(self.fwnum, self.x, self.y, self.size, self.vbias)

	def off(self):
		"""Tell comedi_server to stop monitoring fixwin

		:return: nothing

		"""
		dacq_fixwin(self.fwnum, 0, 0, -1, 0.0)

	def inside(self):
		"""Check to see if eye is inside fixwin.

		:return: (boolean) in/out

		"""
		return dacq_fixwin_state(self.fwnum)

	def broke(self):
		"""Check to see if eye moved out of window, since acquired.

		:return: (boolean) fixation broken since last check?

		"""
		return dacq_fixwin_broke(self.fwnum)

	def break_time(self):
		"""Get the exact time fixation was broken.

		:return: (ms)

		"""
		return dacq_fixwin_break_time(self.fwnum)

	def draw(self, color='grey', dash=None, clear=None):
		"""Draw fixation window on user display.

		:return: nothing

		"""
		if self.icon:
			self.app.udpy.icon(self.icon)

		if clear:
			self.icon = None
		else:
			self.icon = self.app.udpy.icon(self.x, self.y,
										   2*self.size, 2*self.size*self.vbias,
										   color=color, type=2, dash=dash)

class Timer(object):
	def __init__(self, on=True):
		if on:
			self.reset()
		else:
			self.disable()

	def disable(self):
		self._start_at = None

	def reset(self):
		"""Reset timer.

		:return: nothing

		"""
		self._start_at = dacq_ts()

	def ms(self):
		"""Query timer.

		:return: (ms) elapsed time

		"""
		if self._start_at is None:
			return 0
		else:
			return dacq_ts() - self._start_at

class Holder(object):
	"""Dummy class.

	This is just a handle to hold task-related information. You
	can hang things off it and then pickle it or stash it for
	later use.

	"""
	pass

def now(military=1):
	"""Get current timestring.

	:return: (strin) timestring in form HHMM or HHMM[am|pm] depending
		on whether 'military' is true or false.

	"""
	(year, month, day, h, m, s, x1, x2, x3) = time.localtime(time.time())
	if military:
		return "%02d:%02d" % (h, m)
	else:
		if h > 12:
			return "%02d:%02d AM" % (h-12, m)
		else:
			return "%02d:%02d PM" % (h-12, m)

def _get_plexon_events(plex, fc=40000):
	"""
	Drain the Plexon network-based database of timestamp events
	until we hit a StopExtChannel event (this is from the pype-plexon
	TTL sync line). All events left in the tank (post-trial) will
	be discarded.

	"""
	import PlexHeaders

	events = None

	hit_stop = 0
	while not hit_stop:
		tank, ndropped = plex.drain()
		if tank is None:
			Logger("pype: oh no.. lost plexon signal during run\n")
			return None

		for e in tank:
			(Type, Channel, Unit, ts, waveform) = e
			if (Type == PlexHeaders.Plex.PL_ExtEventType and
						Channel == PlexHeaders.Plex.PL_StartExtChannel):
				if events is not None:
					Logger("pype: double trigger\n")
					return None
				events = []
				zero_ts = ts
			elif events is not None:
				if (Type == PlexHeaders.Plex.PL_ExtEventType and
							Channel == PlexHeaders.Plex.PL_StopExtChannel):
					hit_stop = 1
					# drain rest of tank, then return
				else:
					# use fc (sample freq in hz) to convert timestmaps to ms
					events.append((int(round(float(ts - zero_ts) / fc * 1000.0)),
								   Channel, Unit))

	return events

def _addpath(d, atend=None):
	"""
	Add directory to the HEAD (or TAIL) of the python search path.

	**NOTE:**
	This function also lives in pyperun.py.template.

	"""
	if atend:
		sys.path = sys.path + [d]
	else:
		sys.path = [d] + sys.path

def _tolist(v):
	try:
		return v.tolist()
	except AttributeError:
		return v	# v is None (or some other non-numpy array object)

def loadwarn(*args):
	"""OBSOLETE

	Pype now extends the import module to provide this functionality
	automatically as needed.

	"""
	pass

class EmbeddedFigure:
	"""Create matplotlib figure embedded in tkinter parent window.

	"""

	def __init__(self, parent, *args, **kwargs):
		from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
		from matplotlib.figure import Figure

		self.fig = Figure(*args, **kwargs)
		self._canvas = FigureCanvasTkAgg(self.fig, master=parent)
		self._canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)

	def drawnow(self):
		if matplotlib:
			self._canvas.show()

class SimplePlotWindow(Toplevel):
	"""Toplevel plot window for use with matplotlib.

	>>> w = SimplePlotWindow('testplot', app)
	>>> w.fig.clf()
	>>> a = w.fig.add_subplot(1,1,1)
	>>> a.plot(np.random.random(200))
	>>> a.set_xlabel('xlabel')
	>>> a.set_ylabel('xlabel')
	>>> a.set_title('title')
	>>> w.drawnow()

	Note: Unless userclose is set to True, the user will not
	be able to close the plot window and it must be closed
	programmatically by calling widget.destroy() method..

	"""

	def __init__(self, name, app=None, userclose=False, *args, **kw):
		from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
		from matplotlib.figure import Figure

		apply(Toplevel.__init__, (self,), kw)

		self.title(name)
		self.fig = Figure()
		self._canvas = FigureCanvasTkAgg(self.fig, master=self)
		self._canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
		if not userclose:
			self.protocol("WM_DELETE_WINDOW", lambda: 1)

		if app:
			# note: only position is remembered, not size -- this
			# is becaue teh FigureCanvasTkAgg has a size param we're
			# not using here..
			app.setgeo(self, default='+20+20')

	def drawnow(self):
		self._canvas.show()

def show_about(file, timeout=None):
	"""Display a about/splash screen. If transient is True, then return,
	but use callback to clsoe it after 10 secs, otherwise user must close.

	"""

	from PIL import Image, ImageTk

	im = ImageTk.PhotoImage(Image.open(file))
	w = Toplevel(background='white')
	if timeout:
		w.overrideredirect(1)
	w.withdraw()

	f = Frame(w, background='white', relief=RIDGE)
	f.pack(expand=1, fill=BOTH)
	icon = Label(f, relief=FLAT, image=im, background='white')
	icon._image = im
	icon.pack(expand=1, fill=BOTH, side=TOP)

	t = "\n".join(
		(
			"pype: python physiology environment",
			"Version %s" % pypeversion.PypeVersion,
			"Copyright (c) 1999-2013 James A. Mazer",
			"Build Date: %s" % pypeversion.PypeBuildDate,
			))
	text = Label(f, text=t, background='white')
	text.pack(expand=1, fill=BOTH, side=BOTTOM)

	w.update_idletasks()
	screencenter(w)
	w.deiconify()
	w.update_idletasks()
	if timeout:
		w.after(timeout, w.destroy)

if __name__ == '__main__':
	sys.stderr.write('%s should never be loaded as main.\n' % __file__)
	sys.exit(1)

