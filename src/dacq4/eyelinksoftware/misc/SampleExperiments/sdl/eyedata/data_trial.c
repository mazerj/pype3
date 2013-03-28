/*****************************************************************************
 * Copyright (c) 1997 - 2003 by SR Research Ltd., All Rights Reserved        *
 *                                                                           *
 * This software is provided as is without warranty of any kind.  The entire *
 * risk as to the results and performance of this software is assumed by the *
 * user. SR Research Ltd. disclaims all warranties, either express or implied*
 * ,including but not limited, the implied warranties of merchantability,    *
 * fitness for a particular purpose, title and noninfringement, with respect *
 * to this software.                                                         *
 *                                                                           *
 *                                                                           *
 * For non-commercial use by Eyelink licencees only                          *
 *                                                                           *
 * Windows 95/98/NT/2000/XP sample experiment in C                           *
 * For use with Version 2.0 of EyeLink Windows API                           *
 *****************************************************************************/
#include "eyedata.h"
#include <gazecursor.h>


/************************PERFORM AN EXPERIMENTAL TRIAL************************/
/* End recording: adds 100 msec of data to catch final events */
static void end_trial(void)
{
  erase_gaze_cursor();
  clear_full_screen_window(target_background_color);    /* hide display */
  end_realtime_mode();   /* NEW: ensure we release realtime lock */
  pump_delay(100);       /* CHANGED: allow Windows to clean up   */
                         /* while we record additional 100 msec of data  */
  stop_recording();
}

/*	Run a single trial, recording to EDF file and sending data through link 
	This example draws to a bitmap, then copies it to display for 
	fast stimulus onset 
	The order of operations is:
		- Set trial title, ID for analysis
		- Draw to bitmap and create EyeLink display graphics
		- Drift correction
		- start recording
		- Copy bitmap to display
		- start recording
		- unblank display
		- loop till button press, timeout, or abort, drawing gaze cursor	
		- stop recording, handle abort and exit
*/
	 
int realtime_data_trial(SDL_Surface *gbm, UINT32 time_limit)
{
	UINT32 trial_start;	/* trial start time (for timeout)  */
	UINT32 drawing_time;  /* retrace-to-draw delay */
	int button;			/* the button pressed (0 if timeout) */
	int error;            /* trial result code */

	ALLF_DATA evt;        /* buffer to hold sample and event data */
	int eye_used = -1;    /* indicates which eye's data to display */
	float x, y;			/* gaze position  */

	/*
		NOTE: TRIALID AND TITLE MUST HAVE BEEN SET BEFORE DRIFT CORRECTION!
		FAILURE TO INCLUDE THESE MAY CAUSE INCOMPATIBILITIES WITH ANALYSIS 
		SOFTWARE!

		DO PRE-TRIAL DRIFT CORRECTION 
		We repeat if ESC key pressed to do setup. 
	 */
	while(1)
	{  
		/* Check link often so we can exit if tracker stopped */
	  if(!eyelink_is_connected()) return ABORT_EXPT;
	   /*	We let do_drift_correct() draw target in this example
			3rd argument would be 0 if we already drew the display
		*/
	  error = do_drift_correct((INT16)(SCRWIDTH/2), (INT16)(SCRHEIGHT/2), 1, 1);
	   /* repeat if ESC was pressed to access Setup menu  */
	  if(error!=27) break;
	}
	
	clear_full_screen_window(target_background_color);    /* make sure display is blank */
 
	/*	Start data recording to EDF file, BEFORE DISPLAYING STIMULUS 
		You should always start recording 50-100 msec before required
		otherwise you may lose a few msec of data 

		NEW CODE FOR GAZE CURSOR: tell start_recording() to send link data
	*/

	error = start_recording(1,1,1,1);	/* record with link data enabled */
	if(error != 0) return error;      /* ERROR: couldn't start recording */
	/* record for 100 msec before displaying stimulus  */
	/* Windows 2000/XP: no interruptions from now on */
	begin_realtime_mode(100); 
	/*
		DISPLAY OUR IMAGE TO SUBJECT  by copying bitmap to display
		Because of faster drawing speeds and good refresh locking,
		we now place the stimulus onset message just after display refresh 
		and before drawing the stimulus.  This is accurate and will allow 
		drawing a new stimulus each display refresh.
		However, we do NOT send the message after the retrace--this may take
		too long instead, we add a number to the message that represents 
		the delay from the event to the message in msec
	*/
	

	SDL_BlitSurface(gbm,NULL,window,NULL);
	Flip(window);
	drawing_time = current_msec();/* time of retrace */
	trial_start = drawing_time;
	SDL_BlitSurface(gbm,NULL,window,NULL); /* draw on the background */
	initialize_cursor(window, SCRWIDTH/25);  	

	/* delay from retrace (time to draw) */
	drawing_time = current_msec()-drawing_time;
	/* message for RT recording in analysis  */
	eyemsg_printf("%d DISPLAY ON", drawing_time);
	/* message marks zero-plot time for EDFVIEW  */
	eyemsg_printf("SYNCTIME %d", drawing_time);

	if(!eyelink_wait_for_block_start(100, 1, 0))/*wait for link sample data*/
	{
	  end_trial();
	  alert_printf("ERROR: No link samples received!");
	  return TRIAL_ERROR;
	}
	/* determine which eye(s) are available */
	eye_used = eyelink_eye_available();
	switch(eye_used)/* select eye, add annotation to EDF file	*/
	{			
	  case RIGHT_EYE:
		eyemsg_printf("EYE_USED 1 RIGHT");
		break;
	  case BINOCULAR:  /* both eye's data present: use left eye only */
		eye_used = LEFT_EYE;
	  case LEFT_EYE:
		eyemsg_printf("EYE_USED 0 LEFT");
		break;
	}
	/* Now get ready for trial loop */
	eyelink_flush_keybuttons(0);/* reset keys and buttons from tracker  */

	/* 
		we don't use getkey() especially in a time-critical trial
		as Windows may interrupt us and cause an unpredicatable delay
		so we would use buttons or tracker keys only  
	 */

	/*	
		Trial loop: till timeout or response -- 
		added code for reading samples and moving cursor
	*/
	while(1) 
	{ 
	  /* First, check if recording aborted  */
	  if((error=check_recording())!=0) return error;  
								 
	  /* Check if trial time limit expired */
	  if(current_time() > trial_start+time_limit)
		{
			eyemsg_printf("TIMEOUT");    /* message to log the timeout  */
			end_trial();             /* local function to stop recording*/
			button = 0;         /* trial result message is 0 if timeout */
			break;              /* exit trial loop*/
		}

	  /* check for program termination or ALT-F4 or CTRL-C keys*/
	  if(break_pressed())     
		{
			end_trial();         /* local function to stop recording*/
			return ABORT_EXPT;/* return this code to terminate experiment*/
		}

	  /* check for local ESC key to abort trial (useful in debugging)   */
	  if(escape_pressed())    
		 {
			end_trial();         /* local function to stop recording*/
			return SKIP_TRIAL;   /* return this code if trial terminated*/
		 }

		/* BUTTON RESPONSE TEST */
		/* Check for eye-tracker buttons pressed*/
		/* This is the preferred way to get response data or end trials	*/
	  button = eyelink_last_button_press(NULL);
	  if(button!=0)       /* button number, or 0 if none pressed*/
		{
			/* message to log the button press*/
			eyemsg_printf("ENDBUTTON %d", button);  
			/* local function to stop recording*/
			end_trial();                            
			break; /* exit trial loop*/
		}

	/* NEW CODE FOR GAZE CURSOR */

	  if(eyelink_newest_float_sample(NULL)>0)/*check for new sample update*/
		{
			eyelink_newest_float_sample(&evt);/* get a copy of the sample*/
			x = evt.fs.gx[eye_used];/* get gaze position from sample */
			y = evt.fs.gy[eye_used];
			/* make sure pupil is present*/
			if(x!=MISSING_DATA && y!=MISSING_DATA && evt.fs.pa[eye_used]>0)   
				draw_gaze_cursor((int)x,(int)y);  /* show and move cursor*/
			else
				erase_gaze_cursor();    /* hide cursor if no pupil*/
			
		}
	}                       /* END OF RECORDING LOOP*/

	end_realtime_mode();      /* safety cleanup code*/
	while(getkey());          /* dump any accumulated key presses*/

   /* report response result: 0=timeout, else button number*/
	eyemsg_printf("TRIAL_RESULT %d", button);
	
	/* Call this at the end of the trial, to handle special conditions*/
	return check_record_exit();
}

