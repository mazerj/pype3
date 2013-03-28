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
#include <sdl_text_support.h>




/*********** TRIAL SELECTOR **********/

#define NTRIALS 1   /* simple demonstration */

/*
	There is only one data trial.
	Returns trial result code
*/
int do_control_trial(int num)
{
  /* gaze control trial sets up its own bitmap */
  return gaze_control_trial(60000L);  
}




/********************************* TRIAL LOOP ********************************/
 

/*
	This code sequences trials within a block It calls run_trial() to execute 
	a trial, then interperts result code. It places a result message in the 
	EDF file This example allows trials to be repeated from the tracker 
	ABORT menu. 
*/
int run_trials(void)
{
	int i;
	int trial;

	set_calibration_colors(&target_foreground_color, &target_background_color); 
	/* 
	TRIAL_VAR_LABELS message is recorded for EyeLink Data Viewer analysis
	It specifies the list of trial variables for the trial 
	This should be written once only and put before the recording of individual trials
	*/
	eyemsg_printf("TRIAL_VAR_LABELS CONDITION");

  	/* PERFORM CAMERA SETUP, CALIBRATION */
	do_tracker_setup();
				
	/* loop through trials */
	for(trial=1;trial<=NTRIALS;trial++)
	{
		/* drop out if link closed */
		if(eyelink_is_connected()==0 || break_pressed())    
			return ABORT_EXPT;

				/* RUN THE TRIAL */

		i = do_control_trial(trial);
		end_realtime_mode();/* safety: make sure realtime mode stopped */

		switch(i)         	/* REPORT ANY ERRORS */
		{
		case ABORT_EXPT:      /* handle experiment abort or disconnect */
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