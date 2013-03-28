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



#include "simple.h"



/*********** TRIAL SETUP AND RUN **********/

#define NTRIALS 4  /* 4 simple graphics trials  */
static char *trial_word[4] = { "One", "Two", "Three", "Four" };

/* 
	FOR EACH TRIAL:
	- set title, TRIALID
	- Create bitmaps and EyeLink display graphics
	- Check for errors in creating bitmaps
	- Run the trial recording loop
	- Delete bitmaps
	- Return any error code

   Given trial number, execute trials
   Returns trial result code
*/
int do_simple_trial(int num)
{
  /* This supplies the title at the bottom of the eyetracker display  */
  eyecmd_printf("record_status_message 'SIMPLE WORDS, TRIAL %d/%d' ", num, NTRIALS);

  /* 
	Always send a TRIALID message before starting to record. 
	It should contain trial condition data required for analysis.
  */
  eyemsg_printf("TRIALID %s", trial_word[num-1]);

 
  /* TRIAL_VAR_DATA message is recorded for EyeLink Data Viewer analysis
   It specifies the list of trial variables value for the trial 
   This must be specified within the scope of an individual trial (i.e., after 
   "TRIALID" and before "TRIAL_RESULT") */
  eyemsg_printf("!V TRIAL_VAR_DATA %s", trial_word[num-1]);


  /* Before recording, we place reference graphics on the EyeLink display */
  set_offline_mode();  /* Must be offline to draw to EyeLink screen */
  eyecmd_printf("clear_screen 0"); /* clear tracker display and draw box at center  */
  eyecmd_printf("draw_box %d %d %d %d  7", SCRWIDTH/2-16, SCRHEIGHT/2-16, 
  					   SCRWIDTH/2+16, SCRHEIGHT/2+16);

  /* Actually run the trial: display a single word */
  return simple_recording_trial(trial_word[num-1], 20000L); 
}


/******************************** TRIAL LOOP ****************************************
* This code sequences trials within a block It calls run_trial() to execute a trial, 
* then interperts result code. It places a result message in the EDF file 
* This example allows trials to be repeated from the tracker ABORT menu. 
************************************************************************************/
int run_trials(void)
{
  int i;
  int trial;
  
  SETCOLOR(target_background_color ,255,255,255);   /* This should match the display  */
  set_calibration_colors(&target_foreground_color, &target_background_color); 
 
  /*TRIAL_VAR_LABELS message is recorded for EyeLink Data Viewer analysis
   It specifies the list of trial variables for the trial 
   This should be written once only and put before the recording of individual trials */
  eyemsg_printf("TRIAL_VAR_LABELS TRIAL_WORD");


  /* PERFORM CAMERA SETUP, CALIBRATION */
  do_tracker_setup();

  /* loop through trials */
	for(trial=1;trial<=NTRIALS;trial++)
	{
	  if(eyelink_is_connected()==0 || break_pressed())    /* drop out if link closed */
		{
			return ABORT_EXPT;
		}
				/* RUN THE TRIAL */
	  i = do_simple_trial(trial);
	  end_realtime_mode();          /* safety: make sure realtime mode stopped */

	  switch(i)         	/* REPORT ANY ERRORS */
		{
		  case ABORT_EXPT:        /* handle experiment abort or disconnect */
			eyemsg_printf("EXPERIMENT ABORTED");
			return ABORT_EXPT;
		  case REPEAT_TRIAL:	  /* trial restart requested */
			eyemsg_printf("TRIAL REPEATED");
			trial--;
			break;
		  case SKIP_TRIAL:	  /* skip trial */
			eyemsg_printf("TRIAL ABORTED");
			break;
		  case TRIAL_OK:          /* successful trial */
			eyemsg_printf("TRIAL OK");
			break;
		  default:                /* other error code */
			eyemsg_printf("TRIAL ERROR");
			break;
		}
	}  /* END OF TRIAL LOOP */
  return 0;
}

