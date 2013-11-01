#!/usr/bin/python
# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-
#pypeinfo; module; owner:mazer; for:all; descr: base class for fixation tasks

"""
Thu Dec	 9 10:50:37 2004 mazer -- touch_01.py

- ztouch13 --> touch_01.py (first training program for Picard @ yale)
 Then complete rewrite for Picard.. new task

Thu Dec 30 10:10:24 2004 mazer	-- touch_02.py

- added 'reward_on_down' parameter -- if false, then reward if given
  bar if bar is released w/in 'maxrt' ms (if maxrt<0, no time limit).

Thu Dec 30 13:03:52 2004 mazer -- touch_03.py

- implemented spotcolor2, forgot to turn in on..
  got rid of reward_on_down

Mon Jan	 3 10:58:20 2005 mazer -- touch_04.py

- added running history buffer

Tue Jan 11 15:27:53 2005 mazer -- touch_07.py

- added *maxrt/*minrt (local to this task)
  if either is <= 0, they are disabled..

Tue Jan 18 13:33:16 2005 mazer -- change_01.py

- started with touch_07.py

- modifiied so that all the monkey has to do is press the
  bar whenever the spot dims

Sun Mar 13 12:32:11 2005 mazer	 -- change_02.py

- modified change_01 so that touching bar during preperiod
  can just be ignored, instead of generating an error

Thu May	 5 09:49:32 2005 mazer -- change_05 -> fchange_01.py

- added fixation monitoring

Sat May	 7 12:31:45 2005 mazer -- 01 -> 02

- yesterday we debug and fixed some minor bugs on fchange_01 and
  added encodes for fixation onset/break etc. And added the
  graceperiod, to prevent high-speed passage through the fixwin
  from triggering a fixation break.

Mon Jul 11 17:52:36 2005 mazer --

- added handmap hooks (see http://www.mlab.yale.edu/lab/index.php/Handmap)

Fri Jul 15 12:32:45 2005 mazer

- fchange_04: if monk keeps hand on bar eventually it'll cause the eyetrace
  buffer to wrapper around generating an error. this was fixed by not
  starting the eyetrace until after the bar is free.

Wed July 27, 2005 (Touryan)

- adapted to display natural images with gaussian bubble masks

- uses module newmovie

Thu Jul 28 13:05:32 2005 mazer

- (re)created as fixmaster.py for subclassing of tasks..

- this module contains the base class, FixMaster, that all
  other fixation tasks (at least for picard) should be subclasses
  from.

Fri Jul 29 09:55:04 2005 mazer

- added automatic versioning..

Thu Nov 10 13:21:09 2005 mazer

- added vernier frame code

Mon June 12, 2006 (Touryan)

- Overloaded subject-task parameters now have same name
	(*winsize,*vbias,*maxrt,*minrt) -> (win_size,vbias,maxrt,minrt)
- Preperiod renamed iti

Mon Aug 14 09:57:42 2006 mazer

- added 'win_scale' to adjust fixation window as a function of
  eccentricity: win_scale sets amount to add to win_size for each
  pixel beyond 0 eccentricity

- set up run_trial so pre_run_trial() and post_run_trial() can return
  modified parameter tables ('P'), if necessary. By default they don't
  return anything, but if you explicitly return a non-None value, it's
  assumed to be a new version of P.

- added eyecal mode -- if eyecal mode is enabled from parameter
  worksheet and a grid of eyecal points specified on the user display,
  then fixation points (fx, fy) are taken from the specified grid in
  randomized blocks.

Wed Nov 15 10:37:19 2006 mazer

- got rid of 'correct_resp' --> totally obsolete and confusing..

Tue Nov 27 14:29:44 2007 mazer

- Added small random gap between .stimulate() end and dot dimming.
  This is set by specifying 'dimgap'. The gap is actually subtracted
  from 'hold', so it doesn't change the distribution of trial
  durations.  To get back to the original behavior, just set 'dimgap'
  to 0

Wed Jun 24 15:34:49 2009 mazer

- changed to use global win_size, win_scale etc..

Mon Apr	 5 14:41:47 2010 mazer

- added stimdel (stimulus delay) to introduce gap between fixation
	being acquired and stimulus stream starting.

Thu Jan 27 14:42:19 2011 mazer

- got rid of zoombox junk

- changed 'spotsize' to 'hspotsize' (half-size)

Fri Jun 15 15:32:54 EDT 2012 amarin
- paramaterized error color

Mon Jun 18 14:07:02 2012 mazer

- changed things around so that the 'stimulate' stream can continues
  to run after the dot dims so stimulus offset and dot dimming times
  are completely uncorrelated. The way this is done is that the
  dot dimming and "maxrt exceeded" times are queued at the start of
  the stimulation period, and then executed during the nearest call
  to the idlefn. Since things are queued, there could be up to 2 frame
  dur lags (1 is more likely), but the exact RT is computed at the
  end of the correct trials based on the actual frame flip events.

  For the moment, the tasks that subclass of fixmaster can continue
  to function as before -- the timeout that signals the end of the
  stimulate period (not terminated by either BarTransition or NoResponse
  events) is set to an infinite value and just spin until the real
  response comes in.

"""

import sys, random, string
#import traceback
from pype import *
from pype_aux import *
from Tkinter import *
from events import *

class NoResponse(Exception): pass

def clearfix(fixwin):
	if fixwin:
		fixwin.interupts(enable=0)
		fixwin.off()
		fixwin.draw()
	return None

def destroyall(ws):
	for w in ws:
		if w: w.destroy()


class Task:

	# don't touch or override this:
	MasterRev = "$Id: fixmaster.py 785 2013-07-11 12:37:10Z mazer $"

	# OVERRIDE:
	TaskRev = None

	def __init__(self, app, taskname=None, parent=None):
		self.app = app

		if self.TaskRev is not None:
			self.version_no = (self.MasterRev.split()[2],
							   self.TaskRev.split()[2])
			self.version_info = (self.MasterRev,
								 self.TaskRev)
		else:
			self.version_no = (self.MasterRev.split()[2],
							   "-1")
			self.version_info = (self.MasterRev, "none")
		self.version_no = map(int, self.version_no)

		# fixmaster shared/common parameters
		commparams = ( \
			psection('Stimulus Common'),
			pint('x', '50',
                 'stimulus x pos (pix)'),
			pint('y', '50',
                 'stimulus y pos (pix)'),

			psection('Fixation'),
			pyesno('fixring', 0,
                   'bg-colored ring around fixspot?'),
			pyesno('stim_to_end', 0,
                   'stimulate past fixspot dimming?'),
			pcolor('errcolor', '( 200,128,128)',
                   'screen error color'),
			pyesno('eyecal', 0,
                   'eyecal mode or udpy [fx, fy]'),
			piparam('fx', '0',
                    'fix spot x OFFSET (pixels)'),
			piparam('fy', '0',
                    'fix spot y OFFSET (pixels)'),
			pcolor('spotcolor1', '(255,255,255)',
                   'target color during hold (rgb)'),
			pcolor('spotcolor2', '(128,128,128)',
                   'target color triggering release (rgb)'),
			plist('spotcolor2s', '[]',
                  'target colors ([] for spotcolor2, else list'),
			pint('hspotsize', '5',
                 'half size of target (pixels)'),
			pint('win_size_adj', '0',
                 'task-specific additive adjustment factor for win_size'),
			pfloat('rewfreq', '1.0',
                   'frequency (0-1) of times reward is given on correct trial'),
			pyesno('resp_down',	1,
                   'response is bar down?'),

			psection('Timing'),
			piparam('hold', '3000',
                    'how long to hold fixation (ms)'),
			pyesno('repeat_errs', 0,
                   'repeat hold time on error?'),
			piparam('dimgap', '250',
                    'gap between stimulus stream and dim (ms)'),
			piparam('stimdel', '0',
                    'gap between fix acquired and stimulus seq (ms)'),
			pyesno('early_resets', 0,
                   'reset timer for early touch?'),
			pyesno('error_beep', 0,
                   'beep for errors?'),
			pint('maxacquire', '1000',
                 'maximum time to acquire fix spot (ms; 0=>infinite time)'),
			pint('graceperiod', '100',
                 'fix actuall starts after period has elapse (ms)'),
			)

		# task-specfic shared/common parameters
		taskparams = self.task_params()
		if taskname is None:
			taskname = app.taskname()

		self.params = []
		if parent is None:
			self.parent = None
			parfile = 'fixmaster' + '.par'
			self.commbut = app.taskbutton(text='[fixmaster]', check=1)
			self.commnotebook = DockWindow(title='[fixmaster]',
										   checkbutton=self.commbut)
			self.params.append(ParamTable(self.commnotebook,
										  commparams, file=parfile))
		else:
			self.parent = parent
			self.commbut = None
			self.commnotebook = None

		if len(taskparams) > 0:
			parfile = taskname + '.par'
			self.taskbut = app.taskbutton(text=taskname, check=1)
			self.tasknotebook = DockWindow(title=taskname,
									   checkbutton=self.taskbut)
			self.params.append(ParamTable(self.tasknotebook,
										  taskparams, file=parfile))
		else:
			self.taskbut = None
			self.tasknotebook = None

		self.dlist = DisplayList(app.fb)

	def __del__(self):
		for p in self.params:
			p.save(remove=1)
		destroyall([self.commbut, self.commbut,
                    self.commnotebook, self.taskbut, self.tasknotebook]);
		self.app.udpy_note('')
		self.dlist.clear()
		del self.dlist

	def start_run(self, app, pre=1, run=1, post=1, clear=1):
		if pre:
            self.record = 1
			if clear:
				app.con()

			P = app.getcommon()
			if self.parent:
				P = self.parent.params[0].check(mergewith=P)
				self.parent.params[0].save()
			for p in self.params: P = p.check(mergewith=P)
			for p in self.params: p.save()

			# Acute Mode Warning -- disabled..
			if 0 and P['acute']:
				warn('Paused','** Start Spike2 **',wait=1)

			self.behav_hist = []
			self.lasthold = None

			self.fixgrid = None

			# pre_start can set up a fixgrid array on it's own..
			# the fixgrid should be [[x,y],[x,y]...[x,y]]. Leave
			# it alone to let fixmaster deal with it..
			if not self.pre_start(app, P):
				return 0

			if P['eyecal'] or self.fixgrid is not None:
				if self.fixgrid is None:
					self.fixgrid = app.udpy.getpoints()
				if self.fixgrid is None or len(self.fixgrid) < 1:
					warn('error', 'eyecal set, no fixgrid specified!', wait=0)
					return 0
				self.fixgridreps = -1 # number complete reps so far
				self.fixgridcopy = [] # points left on this rep
				self.ntries = 0			  # repeated trials trials on same targ

			app.record_note('task_is', 'not applicable')

		self.ncorrect = 0
		self.ntrials = 0
		if run:
			while app.running:
				try:
					self.run_trial_wrapper(app)
				except UserAbort:
					pass
				if app.ispaused():
					warn("Paused", "Task is paused, close to continue", wait=1)
					app.set_state(paused=0)

		if post:
			P = app.getcommon()
			if self.parent:
				P = self.parent.params[0].check(mergewith=P)
				self.parent.params[0].save()
			for p in self.params: P = p.check(mergewith=P)
			for p in self.params: p.save()

			self.post_start(app, P)

		return 1

	def _makefixwin(self, app, P):
		if P['win_size'] > 0:
			ws = P['win_size'] + P['win_size_adj']
			adj = ((P['fx']**2 +  P['fy']**2)**0.5) * P['win_scale']
			fixwin = FixWin(P['fx'], P['fy'], int(ws + adj), app, P['vbias'])
			fixwin.draw(color='black')
		else:
			fixwin = None
		return fixwin

	def run_trial_wrapper(self, app, meta=None):
		P = app.getcommon()
		if self.parent:
			P = self.parent.params[0].check(mergewith=P)
			self.parent.params[0].save()
		for p in self.params: P = p.check(mergewith=P)

		if P['repeat_errs']:
			if not self.lasthold is None:
				P['hold'] = self.lasthold
				app.con("--> rerunning (hold=%dms)!" % P['hold'])
				self.lasthold = None

		# if spotcolor2s list is given, pick a spotcolor2
		# from the list..
		c = P['spotcolor2s']
		if len(c) > 0:
			P['spotcolor2'] = c[pick_one(c)]

		app.info()
		for k in ('hold', 'maxrt', 'minrt', 'spotcolor1', 'spotcolor2'):
			app.info('%s: %s' % (k, P[k]))

		# you need this "%s" % ... because otherwise it's an instance
		# of the Timestamp class that gets pickled into the datafile!
		# fine for record_note, but not good for .params & p2m..
		timestamp = "%s" % Timestamp()
		ntrials = app.query_ntrials()

		# backward compatibility:
		app.record_note('trialtime', (ntrials, timestamp))

        if self.record:
            app.record_start()
		(resultcode, rt, P) = self.run_trial(app, P, meta=meta)
        if self.record:
            app.record_stop()


		if resultcode[0] == 'C':
			self.ncorrect = self.ncorrect + 1
		self.ntrials = self.ntrials + 1

		P['_trialtime'] = timestamp
		P['_ntrials'] = ntrials
		P['_version_no'] = self.version_no
		P['_version_info'] = self.version_info
		app.record_write(resultcode=resultcode, rt=rt, params=P)

		# push result info onto history stack..
		self.behav_hist.append((resultcode, rt, P))

	def do_dim(self, sprite=None, P=None, app=None):
		if sprite:
			# the dimmed sprite actually will become visible on the next
			# update/flip.. which should be within a frame, unless the
			# task is doing something bad..
			if P['fixring']:
				ssz = 1 + P['hspotsize'] * 2
				sprite.rect(0, 0, ssz-1, ssz-1, P['spotcolor2'])
			else:
				sprite.fill(P['spotcolor2'])
			self.dimat = self.app.encode('approx_'+TEST_OFF)
		else:
			self.dimat = None

        #if app: app.con('DIM')

	def do_miss(self, acute, app):
        #if app: app.con('MISS')
		if acute:
			raise NoProblem
		else:
			raise NoResponse

	def run_trial(self, app, P, meta):
		app.repinfo('%d trials (%d corr)' % (self.ntrials, self.ncorrect))
		P = self.pre_run_trial(app, P)

		if meta:
			P['metarf_file'] = meta[0]	# metarf file name (to file spike2 file)
			P['metarf_tnum'] = meta[1]	# metarf trial number

		rt = -1
		t = Timer()
		t2 = Timer()

		if self.fixgrid:
			if self.ntries > 3:
				# 3 tries in a row, skip this point and reset counter
				app.con('skipping: (%d,%d)' % (self.fixgridcopy[0][0],
												self.fixgridcopy[0][1]))
				self.fixgridcopy = self.fixgridcopy[1:]
				self.ntries = 0

			if len(self.fixgridcopy) == 0:
				# generate fresh permuation of fixgrid points
				self.fixgridcopy = permute(self.fixgrid)
				self.fixgridreps = self.fixgridreps + 1
				self.ntries = 0

			P['fx'] = self.fixgridcopy[0][0]
			P['fy'] = self.fixgridcopy[0][1]
			app.info('%d fixgrid reps; %d left this rep.' % \
				 (self.fixgridreps, len(self.fixgrid)))
			self.ntries = self.ntries + 1
		else:
			# this makes the userdpy fix spot control the basic
			# fixation point and 'fx' and 'fy' from the worksheet
			# control the variance range around that location...
			P['fx'] = P['fx'] + P['fix_x']
			P['fy'] = P['fy'] + P['fix_y']

		fixwin = self._makefixwin(app, P)

		app.udpy.display(None)
		app.looking_at(x=P['fx'], y=P['fy'])

		if P['acute']:
			spotfb = None
		else:
			spotfb = app.fb
		ssz = 1 + P['hspotsize'] * 2		#  spotsize--> ODD and NONZERO
		if P['fixring']:
			# put a bg-colored ring around the fixspot
			bb = ssz + 6
			spot = Sprite(width=bb, height=bb, x=P['fx'], y=P['fy'],
						  depth=10, fb=spotfb, name="spot")
			spot.off()
			spot.fill(P['bg'])
			spot.rect(0, 0, ssz-1, ssz-1, P['spotcolor1'])
		else:
			spot = Sprite(width=ssz, height=ssz, x=P['fx'], y=P['fy'],
						  depth=10, fb=spotfb, name="spot")
			spot.off()
			spot.fill(P['spotcolor1'])

		self.dlist.add(spot)

		try:
			self.dlist.update(flip=1)
			app.udpy.display(self.dlist)

			t.reset()
			app.info('%dms inter-trial interval' % (P['iti'],))
			app.idlefn(P['iti'])

			resp_down = P['resp_down']

			app.eyetrace(1)

			# stage 0: turn on fixation spot
			spot.on()
			if app.taskidle: app.idlefn()			# let handmap update display
			else:			 self.dlist.update(flip=1)
			app.encode(TEST_ON)
			t.reset()
			app.udpy.display(self.dlist)


			try:
				# stage 1: wait until fixating and bar is down/free
				if fixwin:
					# wait for monkey to enter the fixation window
					fixwin.draw(color='red')
					fixwin.on()
					app.info('waiting for fixation & bar down/free')

					fixed = 0
					t.reset()
					while 1:
						if P['resp_down']:
							if fixed and app.barup():
								break
						elif fixed and app.bardown():
							break

						if fixwin.inside():
							fixed = 1
							t2.reset()
							while t2.ms() < P['graceperiod']:
								if fixwin.broke():
									fixed = 0
									fixwin.reset()
									break
								else:
									app.idlefn()
						if P['uitimeout'] > 0 and t.ms() > P['uitimeout']:
							app.info('uitimeout exceeded, UI trial')
							app.con("%s: UI" % (Timestamp(),))
							resultcode = UNINITIATED_TRIAL
							raise MonkError
						else:
							app.idlefn()
					app.encode(FIX_ACQUIRED)

					fixwin.interupts(enable=1)	# fix break -> FixBreak Exception
					fixwin.draw(color='green')
					app.info('fix acquired, trial continues')
				t.reset()

				app.info('trial fully initiated: hand and/or eye')

				# stage 2: setup interrupts and actions, clock out stimuli

				app.bar_genint(1)		# touch/release generates BarTransition
				app.interupts(enable=1)	# both bar-change & fixwin-breaks!

				self.do_dim()
				try:
					if P['stim_to_end']:
						maxhold = P['hold'] + P['maxrt']
						app.queue_action(P['hold'],
										 lambda s=spot,P=P,app=app:self.do_dim(s, P, app))
						app.queue_action(maxhold,
										 lambda a=P['acute'],app=app:self.do_miss(a, app))
						app.encode('stimdelay')
						app.idlefn(P['stimdel'])
						app.encode('stimulate_start')
						app.encode(PSTH_TRIG)
						# stimulate loops until BarTransition or 'do_miss' action
						self.stimulate(app, P, t, 1e6*maxhold)
					else:
						app.encode('stimdelay')
						app.idlefn(P['stimdel'])
						app.encode('stimulate_start')
						app.encode(PSTH_TRIG)
						self.stimulate(app, P,
									   t, P['hold']-P['stimdel']-P['dimgap'])
						# make sure all stimuli except fixspot are gone..
						if len(self.dlist.sprites) > 1:
							for s in self.dlist.sprites[:]:
								if not s is spot:
									self.dlist.delete(s)
							self.dlist.update(flip=1)
						app.idlefn(P['dimgap'])
						self.do_dim(spot, P)
						self.dlist.update(flip=1)
						app.queue_action(P['maxrt'],
										 lambda a=P['acute'],app=app:self.do_miss(a,app))
						while 1:
							self.app.idlefn()
				finally:
					stop = app.ts()
					app.queue_action()					# clear queue
					app.interupts(enable=0)				# disable all interupts
					t.reset()							# reset timeout timer
					self.dlist.delete()
					self.dlist.update()
					app.fb.sync(None)
					app.fb.flip()
					app.encode('stimulate_end')
					fixwin = clearfix(fixwin)

			# stage 3: resolve final trial outcome based on exception class

			except BarTransition:
				#app.bar_genint(0) --> shouldn't ever happen
				app.encode(BAR_CHANGE)
				if self.dimat is None:
					resultcode = EARLY_RELEASE + ' PreTarget'
					app.info('early response --> timeout')
					app.con("%s: early resp (%d)" % (Timestamp(), P['hold']))
					self.errorsig(app, spot, P)
					self.lasthold = P['hold'] # repeat trial
					while t.ms() < P['timeout']:
						app.idlefn()
					raise MonkError
				else:
					# go back to encode data and compute exact RT from page flip
					rt = stop - self.dimat
					for (ets, ecode) in app.get_encodes():
						if (ecode is MARKFLIP) and (ets >= self.dimat):
							# this is when the actual page flip occured..
							rt = stop - ets
							app.encode(TEST_OFF, ets)
							break
					app.info('correct resp --> reward')
					self.squirt(app, P)
					app.con("%s: hold=%d rt=%d" % (Timestamp(), P['hold'], rt))
					raise NoProblem

			except FixBreak:
				app.bar_genint(0)
				app.encode(FIX_LOST)
				resultcode = EARLY_RELEASE	+ ' FixBreak'

				self.errorsig(app, spot, P)
				self.lasthold = P['hold'];
				app.info('fixation break')
				app.con("%s: hold=%d -- fix break" % (Timestamp(), P['hold']))
				while t.ms() < P['timeout']:
					app.idlefn()
				raise MonkError

			except NoResponse:
				app.bar_genint(0)
				resultcode = MAXRT_EXCEEDED + ' MaxRT'

				self.errorsig(app, spot, P)
				self.lasthold = P['hold']
				app.info('past max rt --> timeout')
				app.con("%s: max rt exceeded" % Timestamp())
				while t.ms() < P['timeout']:
					app.idlefn()
				raise MonkError
		except NoProblem:
			resultcode = CORRECT_RESPONSE + ' Correct'
			if self.fixgrid:
				# correct trial; remove point from fixgrid list
				self.fixgridcopy = self.fixgridcopy[1:]
				self.ntries = 0
		except MonkError:
			pass
		except UserAbort:
			resultcode = USER_ABORT + ' Abort'
		except:
			ee = sys.exc_info()
			traceback.print_tb(ee[2])
			warn("fixmaster",
				 'Uncaught Task Exception:\n' +
				 traceback.format_exc(), astext=1)
		finally:
			# clean up section
			app.interupts(enable=0)
			app.bar_genint(0)
			fixwin = clearfix(fixwin)

			self.post_fixation(app)

			app.looking_at()
			app.eyetrace(0)
			self.dlist.delete_all()
			app.fb.sync(0)
			self.dlist.update(flip=1)
			app.udpy.display(self.dlist)

			#del spot

			app.set_result(resultcode)
			app.info('trial is done.')

			P = self.post_run_trial(app, P)

		# resultcode: string (typically CORRRECT_RESPONSE etc..)
		# rt: reaction time in ms
		# P: updated parameter dictionary

		return (resultcode, rt, P)

	def squirt(self, app, P):
		beep(3000, 50, vol=0.5, wait=0)
		# Random (Binary) Reward
		if random.random() > (1.0 - P['rewfreq']):
			# true reward:
			app.reward(dobeep=0)
		else:
			# click solenoid so fast it doesn't deliver anything..
			app.reward(dobeep=0,ms=10)
		app.encode(REWARD)

	def errorsig(self, app, spot, P):
		try:
			if P['error_beep']:
				beep(500, 500, vol=0.5, wait=0)
			spot.off()
			self.dlist.clear()
			self.dlist.update()
            try:
                app.fb.clear(P['errcolor'], flip=1)
                app.idlefn(ms=250)
            finally:
                app.fb.clear(flip=1)
			app.udpy.display(self.dlist)
		except UserAbort:
			print "caught abort in errorsig"

	# following methods should/can be overridden by the task  ###############

	def task_params(self):
		# OVERRIDE -- return list of parameters suitable for ParamTable():
		return ()

	def pre_start(self, app, P):
		# OVERRIDE -- called after file selection, but run starts: return 0/1
		return 1

	def post_start(self, app, P):
		# OVERRIDE -- called at the end of run to cleanup: no return
		pass

	def pre_run_trial(self, app, P):
		# OVERRIDE -- called before each trial: return 'altered' param dict
		return P

	def post_run_trial(self, app, P):
		# OVERRIDE -- called after each trial: return 'altered' param dict
		return P

	def stimulate(self, app, P, timer, duration):
		# OVERRIDE -- called during fixation: no return
		# NB: function **MUST** yield control when 'duration' has elapsed
		#	  on the (already) running time
		while timer.ms() < duration:
			app.idlefn()

	def post_fixation(self, app):
		# OVERRIDE -- called after fixation break, early bar touch
		#			  or end of a correct fixation etc -- for cleaning
		#			  up the handmap stimuli during ITI : no return
		#  Note: this is really a cleanup function.. could get called
		#		 more than once.
		pass



if not __name__ == '__main__':
	loadwarn(__name__)
else:
	sys.stderr.write("not a runable program!\n");
	sys.exit(1)
