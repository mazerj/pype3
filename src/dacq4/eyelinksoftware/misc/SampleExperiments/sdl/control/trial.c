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

#include "control.h"
#include <gazecursor.h>
#include <sdl_text_support.h>

SDL_Surface *segment_source = NULL;
/************************PERFORM AN EXPERIMENTAL TRIAL************************/
/* End recording: adds 100 msec of data to catch final events */
static void end_trial(void)
{
  clear_full_screen_window(target_background_color);    /* hide display */
  end_realtime_mode();   /* NEW: ensure we release realtime lock */
  pump_delay(100);       /* CHANGED: allow Windows to clean up   */
                         /* while we record additional 100 msec of data  */
  stop_recording();
  
    /* Reset link data, disable fixation event data */
  eyecmd_printf("link_event_filter = LEFT,RIGHT,FIXATION,SACCADE,BLINK,BUTTON");
  eyecmd_printf("fixation_update_interval = 0");
  eyecmd_printf("fixation_update_accumulate = 0");
 
}

/* 
	Run a gaze-control trial, recording to EDF file and sending FIXUPDATE 
	events through link. This example draws to a bitmap, then copies it to 
	display for fast stimulus onset 

	The order of operations is:
	- Set trial title, ID for analysis
	- Draw to bitmap and create EyeLink display graphics
	- Create regions
	- Drift correction
	- start recording
	- start recording
	- loop till button press, timeout, or abort, and process FIXUPDATE events	
	- stop recording, handle abort and exit

	NOTE: 
		This trial draws its own bitmap and creates control regions.
		This is done becuase gaze-control trials will usually generate
		the display and the list of rregions with the same code.

	NOTE: 
		realtime mode and display of a bitmap is used here.
		This is to allow experiment-quality timing.
		A typical gaze-control interface would draw directly to the display
		and would not use realtime mode, to increase Windows responsiveness.  
*/

int gaze_control_trial(UINT32 time_limit)
{
	UINT32 trial_start;		/* trial start time (for timeout) */
	UINT32 drawing_time;	/* retrace-to-draw delay*/
	int button;				/* the button pressed (0 if timeout) */
	int error;				/* trial result code*/

	ALLF_DATA evt;			/* buffer to hold sample and event data*/
	int eye_used = -1;		/* indicates which eye's data to display*/
	int i;

	SDL_Surface *gbm;			/* The bitmap containing the stimulus display*/

	   /* This supplies the title at the bottom of the eyetracker display */
	eyecmd_printf("record_status_message 'GAZE CONTROL TRIAL' ");

	/*	
	Always send a TRIALID message before starting to record. 
	It should contain trial condition data required for analysis.
	*/
	eyemsg_printf("TRIALID CONTROL");

  /* TRIAL_VAR_DATA message is recorded for EyeLink Data Viewer analysis
	It specifies the list of trial variables value for the trial 
	This must be specified within the scope of an individual trial (i.e., after 
	"TRIALID" and before "TRIAL_RESULT") 
	*/
	eyemsg_printf("!V TRIAL_VAR_DATA GAZECTRL");
	/* 
	IMGLOAD command is recorded for EyeLink Data Viewer analysis
	It displays a default image on the overlay mode of the trial viewer screen. 
	Writes the image filename + path info
     */
	eyemsg_printf("!V IMGLOAD FILL images/grid.png");	

	/* 
	IAREA command is recorded for EyeLink Data Viewer analysis
	It creates a set of interest areas by reading the segment files
	Writes segmentation filename + path info
	*/
	eyemsg_printf("!V IAREA FILE segments/grid.ias"); 

	/* Before recording, we place reference graphics on the EyeLink display*/
	set_offline_mode();			/* Must be offline to draw to EyeLink screen*/
	gbm = draw_grid_to_bitmap_segment("grid.ias", "segments", 1);;/* Draw bitmap and EyeLink reference graphics*/
	segment_source = gbm;

	/* 
		Save bitmap and transfer to the tracker pc.
		Since it takes a long to save the bitmap to the file, the 
		value of sv_options should be set as SV_NOREPLACE to save time
	*/

	bitmap_save_and_backdrop(gbm, 0, 0, 0, 0, "grid.png", "images", SV_NOREPLACE,
				  0, 0, (UINT16)(BX_MAXCONTRAST|((eyelink_get_tracker_version(NULL)>=2)?0:BX_GRAYSCALE)));

	   /* DO PRE-TRIAL DRIFT CORRECTION */
	   /* We repeat if ESC key pressed to do setup. */
	while(1)
	{              /* Check link often so we can exit if tracker stopped*/
	  if(!eyelink_is_connected()) return ABORT_EXPT;
	   /* We let do_drift_correct() draw target in this example*/
	   /* 3rd argument would be 0 if we already drew the display*/
	  error = do_drift_correct((INT16)(SCRWIDTH/2), (INT16)(SCRHEIGHT/2), 1, 1);
		   /* repeat if ESC was pressed to access Setup menu */
	  if(error!=27) break;
	}

	clear_full_screen_window(target_background_color);  /* make sure display is blank*/

		/* Configure EyeLink to send fixation updates every 50 msec*/
	eyecmd_printf("link_event_filter = LEFT,RIGHT,FIXUPDATE");
	eyecmd_printf("fixation_update_interval = 50");
	eyecmd_printf("fixation_update_accumulate = 50");

	init_regions();	/* Initialize regions for this display*/

	/* 
		Start data recording to EDF file, BEFORE DISPLAYING STIMULUS 
		You should always start recording 50-100 msec before required
		otherwise you may lose a few msec of data 
	*/
	error = start_recording(1,1,0,1);   /* send events only through link*/
	if(error != 0)           /* ERROR: couldn't start recording*/
	{
	  SDL_FreeSurface(gbm);   /* Be sure to delete bitmap before exiting!*/
	  return error;        /* Return the error code*/
	}
							  /* record for 100 msec before displaying stimulus */
	begin_realtime_mode(100);   /* Windows 2000/XP: no interruptions from now on*/

	/* 
		DISPLAY OUR IMAGE TO SUBJECT  by copying bitmap to display
		Because of faster drawing speeds and good refresh locking,
		we now place the stimulus onset message just after display refresh 
		and before drawing the stimulus.  This is accurate and will allow 
		drawing a new stimulus each display refresh.
	 
		However, we do NOT send the message after the retrace--this may take too long
		instead, we add a number to the message that represents the delay 
		from the event to the message in msec
	*/


	/* COPY BITMAP to display*/
	SDL_BlitSurface(gbm, NULL, window,NULL);
	Flip(window);
	drawing_time = current_msec();                   /* time of retrace*/
	trial_start = drawing_time;
	SDL_BlitSurface(gbm, NULL, window,NULL);
	



	/* delay from retrace (time to draw)*/
	drawing_time = current_msec()-drawing_time;    
	/* message for RT recording in analysis */
	eyemsg_printf("%d DISPLAY ON", drawing_time);
	/* message marks zero-plot time for EDFVIEW */
	eyemsg_printf("SYNCTIME %d", drawing_time);	 

	

	/* Print a title for the trial (for demo only)*/
	get_new_font("Times Roman", 24, 1);     
	graphic_printf(window,target_foreground_color, NONE, SCRWIDTH/2, 24, "Gaze Control Trial");
	

	if(!eyelink_wait_for_block_start(100, 0, 1))  /* wait for link event data*/
	{
	  end_trial();
	  alert_printf("ERROR: No link events received!");
	  return TRIAL_ERROR;
	}
	eye_used = eyelink_eye_available(); /* determine which eye(s) are available*/ 
	switch(eye_used)		      /* select eye, add annotation to EDF file	*/
	{			
	  case RIGHT_EYE:
		eyemsg_printf("EYE_USED 1 RIGHT");
		break;
	  case BINOCULAR:           /* both eye's data present: use left eye only*/
		eye_used = LEFT_EYE;
	  case LEFT_EYE:
		eyemsg_printf("EYE_USED 0 LEFT");
		break;
	}
								 
	/* Now get ready for trial loop*/
	eyelink_flush_keybuttons(0);   /* reset keys and buttons from tracker */

	/* 
		we don't use getkey() especially in a time-critical trial
		as Windows may interrupt us and cause an unpredicatable delay
		so we would use buttons or tracker keys only  
		Trial loop: till timeout or response -- added code for processing
		FIXUPDATE events
	*/
	while(1) 
	{ 
		/* First, check if recording aborted */
	  if((error=check_recording())!=0) return error;  
								 
	  /* Check if trial time limit expired*/
	  if(current_time() > trial_start+time_limit)
		{
			eyemsg_printf("TIMEOUT");    /* message to log the timeout */
			end_trial();                 /* local function to stop recording*/
			button = 0;                  /* trial result message is 0 if timeout */
			break;                       /* exit trial loop*/
		}

	  if(break_pressed())     /* check for program termination or ALT-F4 or CTRL-C keys*/
		{
			end_trial();         /* local function to stop recording*/
			return ABORT_EXPT;   /* return this code to terminate experiment*/
		}

	  /* check for local ESC key to abort trial (useful in debugging)   */
	  if(escape_pressed())    
		 {
			end_trial();         /* local function to stop recording*/
			return SKIP_TRIAL;   /* return this code if trial terminated*/
		 }

		/* BUTTON RESPONSE TEST */
		/* Check for eye-tracker buttons pressed
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

		/* GET FIXUPDATE EVENTS, PROCESS*/

		i = eyelink_get_next_data(NULL);    /* Check for data from link*/
		if(i == FIXUPDATE)	  /* only process FIXUPDATE events*/
		{
			/* get a copy of the FIXUPDATE event */
			eyelink_get_float_data(&evt);  
			/* only process if it's from the desired eye?*/
			if(evt.fe.eye == eye_used)	   
			{   
				/* get average position and duration of the update */
				process_fixupdate((int)(evt.fe.gavx), (int)(evt.fe.gavy),/* Process event */
	       			 evt.fe.entime-evt.fe.sttime);
			}
		}
	}/* end of loop*/
	/* report response result: 0=timeout, else button number*/
	eyemsg_printf("TRIAL_RESULT %d", button);
		/* Call this at the end of the trial, to handle special conditions*/
	SDL_FreeSurface(gbm);
	segment_source = NULL;
	return check_record_exit();
}



