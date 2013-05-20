# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""Default Configuration Variables

Author -- James A. Mazer (james.mazer@yale.edu)

"""

"""Revision History

Tue Jun 26 14:21:36 2007 mazer

- abstract out from pype.py to put all config vars in a single
  file for documentation/code-clarity purposes.

Tue Mar 31 13:59:22 2009 mazer

- added TESTPAT

Mon Oct	 1 13:02:25 2012 mazer

- OPENGL flag removed -- this is no longer an option..
"""

import os
import config

def defaults(srcfile=None):

	# load config directory from source file (usually Config.$HOSTNAME)
	c = config.Config(srcfile)

	# merge with list of default/initial values -- these values will
	# NOT override what's in the config file (override=None), so they
	# will only be set if not set in the config file (ie, these are
	# the default values).

	#####################################################
	# general settings

	c.set('DEBUG', '0',
		  doc='debug mode')
	c.set('SPLASH', '1',
		  doc='show splash screen on startup')

	#####################################################
	# physical hardware (i/o) settings

	c.set('DACQ_SERVER', 'comedi_server',
		  doc='name of DACQ executable')
	c.set('ARANGE',	'10.0',
		  doc='set analog input volt. range (+-V)')
	c.set('PPORT', '-1',
		  doc='enable parallel port access '+
		  'specific 1 for default or 0xNNN for non-default')
	c.set('FLIP_BAR', '0',
		  doc='flip response  bar input polarity')
	c.set('FLIP_SW1', '0',
		  doc='flip user switch 1 input polarity')
	c.set('FLIP_SW2', '0',
		  doc='flip user switch 2 input polarity')
	c.set('ENABLE_SW1', '1',
		  doc='enable/disable SW1')
	c.set('REWARD_BEEP', '1',
		  doc='beep when giving rewards?')
	c.set('SOUND', '1',
		  doc='access to sound card?')

	c.set('USB_JS_DEV',	'',
		  doc='enable USB joystick -- device file')

	#####################################################
	# graphics display screen parameters

	c.set('MONW', '-1',
		  doc='physical monitor width (cm)')
	c.set('MONH', '-1',
		  doc='physical monitor height (cm)')
	c.set('VIEWDIST', '-1',
		  doc='physical viewing distance (cm)')
	c.set('MON_ID', '',
		  doc='ID string for data file')
	c.set('DPYW', '1024',
		  doc='display width (pix)')
	c.set('DPYH', '768',
		  doc='display height (pix)')
	c.set('DPYBITS', '32',
		  doc='bit-depth for display')
	c.set('FPS', '0',
		  doc='desired frame rate (frames/sec)')
	c.set('GAMMA', '1.0',
		  doc='default gamma value')
	c.set('FULLSCREEN', '1',
		  doc='full screen mode?')
	c.set('MOUSE', '0',
		  doc='initialize mouse?')
	c.set('FRAME', '0',
		  doc='show window frame/border (non-fullscr)')

	# note: None for SYNCX/Y means autoconfig to lower right..
	c.set('SYNCSIZE', '50',
		  doc='size of sync pulse square (pix)')
	c.set('SYNCX', None,
		  doc='X location of sync square CENTER (pix)')
	c.set('SYNCY', None,
		  doc='Y location of sync square CENTER (pix)')
	c.set('SYNCLEVEL', '255',
		  doc='gray scale value of sync-on')
	c.set('TESTPAT', None,
		  doc='filename for test pattern')

	if os.environ.has_key('DISPLAY'):	# display device for graphics
		c.set('SDLDPY', os.environ['DISPLAY'])
	else:
		c.set('SDLDPY', ':0.1')

	if not c.iget('FULLSCREEN'):
		# if not using FULLSCREEN mode, then force the graphics to
		# be displayed locally (in a window)
		if os.environ.has_key('DISPLAY'):
			c.set('SDLDPY', os.environ['DISPLAY'])

	#####################################################
	# eye tracker parameters

	c.set('EYETRACKER', 'ANALOG',
		  doc='eye tracker mode: ANALOG, ISCAN, EYELINK or NONE')
	c.set('EYETRACKER_DEV', '',
		  doc='serial port or IP address')
	c.set('SWAP_XY', '0',
		  doc='swap X & Y on eye tracker')

										# EYELINK SPECIFIC OPTIONS
	c.set('EYELINK_XTALK', '0,-0.001',
		  doc='crosstalk adj: pupil pos/size')
	c.set('EYELINK_OPTS', '',
		  doc='any extra options to pass to API')
	c.set('EYELINK_CAMERA',	'1',
		  doc='left or right camera (0, 1)')

	#####################################################
	# plexon interface
	c.set('PLEXHOST', '',
		  doc='PlexNet Host IP number')
	c.set('PLEXPORT', '6000',
		  doc='PlexNet Host Tcp Port')

	#####################################################
	# TDT interface
	c.set('TDTHOST', '',
		  doc='name or IP# of window box running tdt.py')
	
	#####################################################
	# User Display Settings
	c.set('USERDISPLAY_HIDE', 0,
		  doc='iconify udpy window on startup')
	c.set('USERDISPLAY_SCALE', 1.0,
		  doc='scale user display by ... for big monitors')
	c.set('TICKS_MAJOR', 1,
		  doc='show major (5dva) grid tickmarks?')
	c.set('TICKS_MINOR', 1,
		  doc='show minor (1dva) grid tickmarks?')
	c.set('ONE_WINDOW', 0,
		  doc='one window for GUI and UserDisplay?')

	#####################################################
	# Disable use of ELOG -- overides env-var $ELOG
	c.set('ELOG', 1,
		  doc='enable/disable use of elog api/interface')

	return c

def defaults_show():
	c = defaults()
	for k in c.keys():
		d = c.getdoc(k)
		if not d is None:
			print "# %s" % d
		print '%s: %s' % (k, c.get(k),)

def defaults_info():
	return """
Sound & Video
-------------
FULLSCREEN		(0|1)	enable full screen mode
DPYBITS			(#)		number of display bits (typically 24 or 32)
DPYH			(#)		display height in pixels
DPYW			(#)		display width in pixels
GAMMA			(float) scalar gamma correction for monitor (luminance)
MONH			(#)		monitor height in cm
MONW			(#)		monitor width in cm
MON_ID			(str)	identifier string for monitor (brand etc)
VIEWDIST		(#)		viewing distance (eye to monitor) in cm
AUDIODRIVER		(str)	name of pygame SDL_AUDIODRIVER
REWARD_BEEP		(0|1)	beep on each reward
SOUND			(0|1)	sound on/off (default is on)
SYNCLEVEL		(#)		intensity (0-255) of sync pulse signal
SYNCSIZE		(#)		size (pixels) of sync pulse sprite (width & height)
SYNCX			(#)		x-location (pixels) of sync pulse sprite
SYNCY			(#)		y-location (pixels) of sync pulse sprite

Eye Tracking
------------
EYETRACKER		(str)	eyetracker device: ANALOG, ISCAN or EYELINK
EYETRACKER_DEV	(str)	device file (IP # for eyelink)
SWAP_XY			(0|1)	swap x and y channels on eyetracker
EYELINK_CAMERA	(0,1)	left or right eyelink (EL2) camera to read
EYELINK_OPTS	(str)	extra options for the eyelink API
EYELINK_XTALK	(#,#)	luminance-position cross talk correction for eyelink

Data Acquisition
----------------
FLIP_BAR		(0|1)	flip sign of monkey bar (sw0)
FLIP_SW1		(0|1)	flip sign of user switch 1
FLIP_SW2		(0|1)	flip sign of user switch 2
ENABLE_SW1		(0|1)	enable switch 1 for manual rewards
PPORT			(hex#)	parallel port (cage trainer); should start with 0x

Remote Data Acquisition
-----------------------
PLEXHOST		(str)	IP # or name of machine running PlexNet
PLEXPORT		(#)		port # for PlexNet
TDTHOST			(str)	name or IP number of machine running tdt.py

Other
-----
DEBUG			(0|1)	enables debug mode
SPLASH			(0|1)	display splash screen
PSYCH			(0|1)	psychophysics mode (also -p option on command line)
HIDE_USERDISPLAY (0|1)	hide usder display window on startup
TICKS_MAJOR		(0|1)	show major (5deg) tickmarks on userdisplay
TICKS_MINOR		(0|1)	show minor (1deg) tickmarks on userdisplay

Environment Vars (use setenv, not config file!)
-----------------------------------------------
TTANK			(0/1)	if 0, then forces skipping to TTANK queries
TTANKSERVER		(str)	hostname for ttank server (overrides pypefile)
TTANKDIR		(str)	directory for ttanks (overrides pypefile)

Note: TTANKHOST/DIR are useful when the data get stored directly
	  to a local disk, but later moved to a new location for
	  permanent storage (like a RAID).
"""
