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


  
#include "text.h"
#include <sdl_text_support.h>


/*********** TEXT PAGES ***********/

static char text1[] = 
"Buck did not read the newspapers, or he would have known that trouble was "
"brewing, not alone for himself, but for every tide-water dog, strong of "
"muscle and with warm, long hair, from Puget Sound to San Diego.  Because "
"men, groping in the Arctic darkness, had found a yellow metal, and because "
"steamship and transportation companies were booming the find, thousands of "
"men were rushing into the Northland.  These men wanted dogs, and the dogs "
"they wanted were heavy dogs, with strong muscles by which to toil, and furry "
"coats to protect them from the frost. \n"
"   Buck lived at a big house in the sun-kissed Santa Clara Valley.  Judge "
"Miller's place, it was called.  It stood back from the road, half hidden "
"among the trees, through which glimpses could be caught of the wide cool "
"veranda that ran around its four sides.";

static char text2[] = 
"  The house was approached by "
"gravelled driveways which wound about through wide-spreading lawns and under "
"the interlacing boughs of tall poplars.  At the rear things were on even a "
"more spacious scale than at the front.  There were great stables, where a "
"dozen grooms and boys held forth, rows of vine-clad servants' cottages, an "
"endless and orderly array of outhouses, long grape arbors, green pastures, "
"orchards, and berry patches.  Then there was the pumping plant for the "
"artesian well, and the big cement tank where Judge Miller's boys took their "
"morning plunge and kept cool in the hot afternoon. \n"
"   And over this great demesne Buck ruled.  Here he was born, and here he "
"had lived the four years of his life.  It was true, there were other dogs, "
"There could not but be other dogs on so vast a place, but they did not "
"count.  ";

static char text3[] = 
"   They came and went, resided in the populous kennels, or lived "
"obscurely in the recesses of the house after the fashion of Toots, the "
"Japanese pug, or Ysabel, the Mexican hairless,--strange creatures that "
"rarely put nose out of doors or set foot to ground. On the other hand, there "
"were the fox terriers, a score of them at least, who yelped fearful promises "
"at Toots and Ysabel looking out of the windows at them and protected by a "
"legion of housemaids armed with brooms and mops. \n"
"   But Buck was neither house-dog nor kennel-dog.  The whole realm was his.  "
"He plunged into the swimming tank or went hunting with the Judge's sons; he "
"escorted Mollie and Alice, the Judge's daughters, on long twilight or early "
"morning rambles; on wintry nights he lay at the Judge's feet before the "
"roaring library fire; he carried the Judge's grandsons on his back, or "
"rolled them in the grass.";

static char text4[] = 
"Among the terriers he stalked "
"imperiously, and Toots and Ysabel he utterly ignored, for he was king,--king "
"over all creeping, crawling, flying things of Judge Miller's place, humans "
"included. \n"
"   His father, Elmo, a huge St.  Bernard, had been the Judge's inseparable "
"companion, and Buck bid fair to follow in the way of his father.  He was not "
"so large,--he weighed only one hundred and forty pounds,--for his mother, "
"Shep, had been a Scotch shepherd dog.  Nevertheless, one hundred and forty "
"pounds, to which was added the dignity that comes of good living and "
"universal respect, enabled him to carry himself in right royal fashion.  "
"During the four years since his puppyhood he had lived the life of a sated "
"aristocrat; he had a fine pride in himself, was even a trifle egotistical, "
"as country gentlemen sometimes become because of their insular situation.  ";

char *pages[4] = { text1, text2, text3, text4 };


/******************************* TRIAL SETUP AND RUN ************************/

#define NTRIALS 4  /* formatted text trials  */



/* FOR EACH TRIAL:
	- set title, TRIALID
	- Create bitmaps and EyeLink display graphics
	- Check for errors in creating bitmaps
	- Run the trial recording loop
	- Delete bitmaps
	- Return any error code
*/

/* Given trial number, execute trials Returns trial result code */
int do_text_trial(int num)
{
	SDL_Surface *bitmap = NULL;
	int i;
	char image_fn[100];	/* image file name;*/ 
		

	  /* Must be offline to draw to EyeLink screen */
	set_offline_mode();		    
	eyecmd_printf("clear_screen 0");       

	/* This supplies the title at the bottom of the eyetracker display  */
	eyecmd_printf("record_status_message 'TEXT, PAGE %d/%d' ", num, NTRIALS);

	/* 
	 Always send a TRIALID message before starting to record. 
	 It should contain trial condition data required for analysis.
	*/ 
	eyemsg_printf("TRIALID PAGE%d", num);
	
	/*  TRIAL_VAR_DATA message is recorded for EyeLink Data Viewer analysis
		It specifies the list of trial variables value for the trial 
		This must be specified within the scope of an individual trial (i.e., after 
		"TRIALID" and before "TRIAL_RESULT") 
	*/ 
	eyemsg_printf("!V TRIAL_VAR_DATA %d", num);

	sprintf(image_fn, "test%d.png", num);	/* get the image file name */ 
	/*	IMGLOAD command is recorded for EyeLink Data Viewer analysis
		It displays a default image on the overlay mode of the trial viewer screen. 
		Writes the image filename + path info
	*/
	eyemsg_printf("!V IMGLOAD FILL Images/%s", image_fn);	
		
	get_new_font("Times Roman", SCRHEIGHT/25, 0);
	
	bitmap = SDL_CreateRGBSurface(SDL_SWSURFACE,SCRWIDTH, SCRHEIGHT,dispinfo.bits,0,0,0,0);
	set_margin(SCRWIDTH/20,SCRHEIGHT/20,SCRWIDTH/20,SCRHEIGHT/20);
	set_line_spacing(((double)(SCRHEIGHT)/15.0)/(double) get_font_height());
	SDL_FillRect(bitmap,NULL,SDL_MapRGB(bitmap->format, target_background_color.r, target_background_color.g, target_background_color.b));
	graphic_printf(bitmap,target_foreground_color,WRAP,0,0,pages[num-1]);  

	/* 
		Save bitmap and transfer to the tracker pc.
		Since it takes a long to save the bitmap to the file, the 
		value of sv_options should be set as SV_NOREPLACE to save time
	*/
	bitmap_save_and_backdrop(bitmap, 0, 0, 0, 0, image_fn,"images",SV_NOREPLACE, 0,0, BX_NODITHER|BX_GRAYSCALE); 
	
	i = bitmap_recording_trial(bitmap, 20000L); 
	SDL_FreeSurface(bitmap);
	
	return i;
}

/******************************* TRIAL LOOP ************************/


	/*	
		This code sequences trials within a block 
		It calls run_trial() to execute a trial, 
		then interperts result code. 
		It places a result message in the EDF file 
		This example allows trials to be repeated 
		from the tracker ABORT menu. 
	*/

int run_trials(void)
{
	int i;
	int trial;
	
	
	SETCOLOR(target_background_color ,255,255,255);   /* This should match the display  */
	set_calibration_colors(&target_foreground_color, &target_background_color); 
  
	/*	TRIAL_VAR_LABELS message is recorded for EyeLink Data Viewer analysis
		It specifies the list of trial variables for the trial 
		This should be written once only and put before the recording of individual trials
	*/
	eyemsg_printf("TRIAL_VAR_LABELS PAGE");
    
	/* PERFORM CAMERA SETUP, CALIBRATION */
	do_tracker_setup();

	/* loop through trials */
	for(trial=1;trial<=NTRIALS;trial++)
	{
		/* drop out if link closed */
	  if(eyelink_is_connected()==0 || break_pressed())        
		return ABORT_EXPT;
	
				/* RUN THE TRIAL */
	  i = do_text_trial(trial);
	  end_realtime_mode();   /* safety: make sure realtime mode stopped */

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

