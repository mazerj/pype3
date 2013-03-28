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

#include "gcwindow.h"
#include <gazecursor.h>



/********* PERFORM AN EXPERIMENTAL TRIAL  *******/


/* End recording: adds 100 msec of data to catch final events */
static void end_trial(void)
{
  clear_full_screen_window(target_background_color);    /* hide display */
  end_realtime_mode();   /* NEW: ensure we release realtime lock */
  pump_delay(100);       /* CHANGED: allow Windows to clean up   */
                         /* while we record additional 100 msec of data  */
  stop_recording();
  while(getkey()) {};
}

/* 
	Run a single trial, recording to EDF file and sending data through link 
	This example draws to a bitmap, then copies it to display for fast stimulus onset 

	 The order of operations is:
	- Set trial title, ID for analysis
	- Draw foreground, background bitmaps and create EyeLink display graphics
	- Drift correction
	- start recording
	- <DON'T copy bitmap to display: draw window when first sample arrives>
	- loop till button press, timeout, or abort, drawing gaze contingent window
	- stop recording, dispose of bitmaps, handle abort and exit

	NEW CODE FOR GAZE CONTINGENT DISPLAY:
	- create both foreground and background bitmaps
	- uses the eyelink_newest_float_sample() to get latest update
	- initialize window with initialize_gc_window()
	- moves window with redraw_gc_window()

	Run gaze-contingent window trial
	<fgbm> is bitmap to display within window
	<bgbm> is bitmap to display outside window
	<wwidth, wheight> is size of window in pixels
	<mask> flags whether to treat window as a mask
	<time_limit> is the maximum time the stimuli are displayed 
*/
int gc_window_trial(SDL_Surface * fgbm, SDL_Surface * bgbm, 
                    int wwidth, int wheight, int mask, UINT32 time_limit)
{
  UINT32 trial_start=0;	/* trial start time (for timeout)  */
  UINT32 drawing_time;  /* retrace-to-draw delay */
  int button;			/* the button pressed (0 if timeout)  */
  int error;            /* trial result code */

  ALLF_DATA evt;         /* buffer to hold sample and event data */
  int first_display = 1; /* used to determine first drawing of display   */
  int eye_used = 0;      /* indicates which eye's data to display */
  float x, y;			 /* gaze position  */

	/*
	 NOTE: TRIALID AND TITLE MUST HAVE BEEN SET BEFORE DRIFT CORRECTION!
	 FAILURE TO INCLUDE THESE MAY CAUSE INCOMPATIBILITIES WITH ANALYSIS SOFTWARE!
	 */

	/*
		 DO PRE-TRIAL DRIFT CORRECTION 
		 We repeat if ESC key pressed to do setup. 
	*/
  
  while(1)
    {              /* Check link often so we can exit if tracker stopped */
      if(!eyelink_is_connected()) return ABORT_EXPT;
	   /* 
			We let do_drift_correct() draw target in this example
			3rd argument would be 0 if we already drew the display
	   */
      error = do_drift_correct((INT16)(SCRWIDTH/2), (INT16)(SCRHEIGHT/2), 1, 1);
           /* repeat if ESC was pressed to access Setup menu  */
      if(error!=27) break;
    }

    clear_full_screen_window(target_background_color);   /* make sure display is blank */
  
	/*
		Start data recording to EDF file, BEFORE DISPLAYING STIMULUS 
		You should always start recording 50-100 msec before required
		otherwise you may lose a few msec of data 
  
		tell start_recording() to send link data
	*/
  error = start_recording(1,1,1,1);	/* record with link data enabled */
  if(error != 0) return error;      /* ERROR: couldn't start recording */
                              /* record for 100 msec before displaying stimulus  */
  begin_realtime_mode(100);   /* Windows 2000/XP: no interruptions from now on */

    /* DONT DISPLAY OUR IMAGES TO SUBJECT until we have first gaze postion! */
  SDL_BlitSurface(bgbm,NULL,window,NULL);
  initialize_dynamic_cursor(window, min(wwidth,wheight) ,fgbm);
  
  if(!eyelink_wait_for_block_start(100, 1, 0))  /* wait for link sample data */
    {
      end_trial();
      alert_printf("ERROR: No link samples received!");
      return TRIAL_ERROR;
    }
  eye_used = eyelink_eye_available(); /* determine which eye(s) are available  */
  switch(eye_used)		      /* select eye, add annotation to EDF file	 */
    {			
      case RIGHT_EYE:
        eyemsg_printf("EYE_USED 1 RIGHT");
        break;
      case BINOCULAR:           /* both eye's data present: use left eye only */
        eye_used = LEFT_EYE;
      case LEFT_EYE:
        eyemsg_printf("EYE_USED 0 LEFT");
        break;
    }
                                 /* Now get ready for trial loop */
  eyelink_flush_keybuttons(0);   /* reset keys and buttons from tracker  */
                       /* 
						we don't use getkey() especially in a time-critical trial
						as Windows may interrupt us and cause an unpredicatable delay
                        so we would use buttons or tracker keys only  
					   */

    
     /*Trial loop: till timeout or response -- added code for reading samples and moving cursor */
	while(1) 
	{                            /* First, check if recording aborted  */
		if((error=check_recording())!=0) return error;  
								 /* Check if trial time limit expired */
		if(current_time() > trial_start+time_limit && trial_start!=0)
		{
			eyemsg_printf("TIMEOUT");    /* message to log the timeout  */
			end_trial();                 /* local function to stop recording */
			button = 0;                  /* trial result message is 0 if timeout  */
			break;                       /* exit trial loop */
		}

		if(break_pressed())     /* check for program termination or ALT-F4 or CTRL-C keys */
		{
			end_trial();         /* local function to stop recording */
			return ABORT_EXPT;   /* return this code to terminate experiment */
		}

		if(escape_pressed())    /* check for local ESC key to abort trial (useful in debugging)    */
		 {
			end_trial();         /* local function to stop recording */
			return SKIP_TRIAL;   /* return this code if trial terminated */
		 }

			/* BUTTON RESPONSE TEST */
			/* Check for eye-tracker buttons pressed */
			/* This is the preferred way to get response data or end trials	 */
		  button = eyelink_last_button_press(NULL);
		if(button!=0)       /* button number, or 0 if none pressed */
		{
			eyemsg_printf("ENDBUTTON %d", button);  /* message to log the button press */
			end_trial();                            /* local function to stop recording */
			break;                                  /* exit trial loop */
		}

		/* NEW CODE FOR GAZE CONTINGENT WINDOW  */
		if(eyelink_newest_float_sample(NULL)>0)  /* check for new sample update */
		{
			eyelink_newest_float_sample(&evt);   /* get the sample  */
			x = evt.fs.gx[eye_used];    /* yes: get gaze position from sample  */
			y = evt.fs.gy[eye_used];
			if(x!=MISSING_DATA && y!=MISSING_DATA && evt.fs.pa[eye_used]>0)     /* make sure pupil is present */
			{
				
			  if(first_display)  /* mark display start AFTER first drawing of window */
				{       

				  drawing_time = current_msec();  /* time of retrace */
				  trial_start = drawing_time;   /* record the display onset time  */
				}
				
			  draw_gaze_cursor((int)x, (int)y);  /* move window if visible */
			  
			  if(first_display)  /* mark display start AFTER first drawing of window */
				{       
				  first_display = 0;      
				  drawing_time = current_msec() - drawing_time; /* delay from retrace */
				  eyemsg_printf("%d DISPLAY ON", drawing_time);	/* message for RT recording in analysis  */
				  eyemsg_printf("SYNCTIME %d", drawing_time);	/* message marks zero-plot time for EDFVIEW  */
				  //SDL_Flip(window);
				  SDL_BlitSurface(bgbm,NULL,window,NULL);
				}
			  
			}
			else
			{
				/* 
					Don't move window during blink 
				 */
			}
		} 
	}                       /* END OF RECORDING LOOP */

  end_realtime_mode();      /* safety cleanup code */
  while(getkey());          /* dump any accumulated key presses */

  /* report response result: 0=timeout, else button number */
  eyemsg_printf("TRIAL_RESULT %d", button);

  /* Call this at the end of the trial, to handle special conditions */
  return check_record_exit();
}

