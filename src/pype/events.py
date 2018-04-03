# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""Events and result codes

Event definitions, based on the encode tags used by the
ORTEX program from Bob Desimone's lab at NIMH.

Author -- James A. Mazer (mazerj@gmail.com)

"""

####################################################################
# Result Codes -- Trial Outcome
####################################################################

# standard trial result codes (try to use these if possible!!)
# result codes are single letter -- additional (task-specfic) info
# can be appended, if required.

ANY_RESPONSE			= None
CORRECT_RESPONSE		= 'C'
USER_ABORT				= 'A'
UNINITIATED_TRIAL		= 'U'
MAXRT_EXCEEDED			= 'M'
EARLY_RELEASE			= 'E'
ERROR_RESPONSE			= 'X'

# this is for trials where there's really no 'correct' or 'incorrect'
# response possible -- like spontaneous data or freeviewing..
NA_RESPONSE				= 'N'

rcodes = {
	'C': 'CORRECT_RESPONSE',
	'A': 'USER_ABORT',
	'U': 'UNITIATED_TRIAL',
	'M': 'MAXRT_EXCEEDED',
	'E': 'EARLY_RELEASE'
}

def iscorrect(code):
	if code[0] == CORRECT_RESPONSE:
		return 1
	else:
		return 0

def isabort(code):
	if code[0] == ABORT:
		return 1
	else:
		return 0

def isui(code):
	if code[0] == UNINITIATED_TRIAL:
		return 1
	else:
		return 0

def ismaxrt_exceeded(code):
	if code[0] == MAXRT_EXCEEDED:
		return 1
	else:
		return 0

def isearly_release(code):
	if code[0] == EARLY_RELEASE:
		return 1
	else:
		return 0

####################################################################
# Event Codes -- timestamped and put in the encode buffer
####################################################################

# internal use only by pype

EYESHIFT = 'eyeshift'					# F8 key (or something similar)
ABORT = 'abort'                         # user hit ESC key

# semi internal -- generated automatically by pype, but ok to count on..

MARKFLIP = 'INT_MARKFLIP'

# for general (task) use:


START_ITI				= 'start_iti'
END_ITI					= 'end_iti'

START_PRE_TRIAL			= 'start_pre_trial'
END_PRE_TRIAL			= 'end_pre_trial'

START_POST_TRIAL		= 'start_post_trial'
END_POST_TRIAL			= 'end_post_trial'

START_WAIT_FIXATION		= 'start_wait_fixation'
END_WAIT_FIXATION		= 'end_wait_fixation'
FIXATION_OCCURS			= 'fixation_occurs'

START_WAIT_BAR			= 'start_wait_bar'
END_WAIT_BAR			= 'end_wait_bar'
BAR_UP					= 'bar_up'
BAR_DOWN				= 'bar_down'
BAR_CHANGE				= 'bar_change'

TEST_ON					= 'test_on'
TEST_OFF				= 'test_off'

FIX_ON					= 'fix_on'
FIX_OFF					= 'fix_off'

FIX_ACQUIRED			= 'fix_acquired'
OLD_FIX_ACQUIRED		= 'fix_acuired'
FIX_LOST				= 'fix_lost'
FIX_DONE				= 'fix_done'

TARGET_ACQUIRED			= 'target_acquired'
TARGET_LOST				= 'target_lost'

START_SPONT				= 'start_spont'
STOP_SPONT				= 'stop_spont'

REWARD					=  'reward'

SPIKE1					= '_s1'
SPIKE2					= '_s2'
SPIKE3					= '_s3'
SPIKE4					= '_s4'
SPIKE5					= '_s5'
SPIKE6					= '_s6'
SPIKE7					= '_s7'
SPIKE8					= '_s8'
SPIKE9					= '_s9'
SPIKE10					= '_s10'
SPIKE11					= '_s11'
SPIKE12					= '_s12'
SPIKE13					= '_s13'
SPIKE14					= '_s14'
SPIKE15					= '_s15'
SPIKE16					= '_s16'

# DMTS constants
SAMPLE_ON				= 'sample_on'
SAMPLE_OFF				= 'sample_off'
TARGETS_ON				= 'targets_on'
TARGETS_OFF				= 'targets_off'
mod_MATCH				= ' match'		# modifier only
mod_NON_MATCH			= ' non-match'	# modifier only


# for internal use:
START					= 'start'
STOP					= 'stop'
EYE_START				= 'eye_start'
EYE_STOP				= 'eye_stop'
EYE_OVERFLOW			= 'eye_overflow'

# new events for non-cortex-like stuff... add below:
FLIP					= 'flip'

# debugging mark
MARK					= 'mark'

# trigger event for automatic psth
PSTH_TRIG				= 'psth_trig'

####################################################################
# label tags for pickled datafiles
####################################################################

ENCODE = 'ENCODE'
NOTE = 'NOTE'
WARN = 'WARN'
ANNOTATION = 'ANNOTATION'


if __name__=='__main__' :
	pass
