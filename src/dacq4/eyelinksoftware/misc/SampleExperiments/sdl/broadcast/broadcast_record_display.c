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

#include <stdlib.h>
#include "broadcast.h"
#include <sdl_text_support.h>
#include <gazecursor.h>



/* functions to map gaze from tracker to local pixels */
extern INT16 track2local_x(float x); 
extern INT16 track2local_y(float y);


/********* PERFORM AN EXPERIMENTAL TRIAL  *******/
	 
int record_mode_display(void)
{
  ALLF_DATA evt;
  UINT16 key;
  int eye_used = -1;   /* which eye to show gaze for */
  float x, y;	       /* gaze position  */
  float ox=-1, oy=-1;  /* old gaze position (to determine change)  */

  /* create font for position display */
  get_new_font( "Arial", SCRWIDTH/50, 0);
  while(getkey()); /* dump any pending local keys  */

  /*enable link data reception without changing tracker mode */
  eyelink_reset_data(1);   
  initialize_cursor(window, SCRWIDTH/50);
  eyelink_data_switch(RECORD_LINK_SAMPLES | RECORD_LINK_EVENTS);
  
  while(1)    /* loop while in record mode */
    {
	  
      if(eyelink_tracker_mode() != EL_RECORD_MODE) break;
      key = getkey();            /* Local keys/abort test */
      if(key==TERMINATE_KEY)     /* test ALT-F4 or end of execution */
         break;
      else if(key)             /* OTHER: echo to tracker for control */
		eyelink_send_keybutton(key,0,KB_PRESS);

               /* CODE FOR PLOTTING GAZE CURSOR  */
      if(eyelink_newest_float_sample(NULL)>0)  /* new sample? */
		{
			eyelink_newest_float_sample(&evt);  /* get the sample data */
			if(eye_used == -1)   /* set which eye to track by first sample */
			{
				eye_used = eyelink_eye_available(); 
				if(eye_used == BINOCULAR)  /* use left eye if both tracked */
					eye_used = LEFT_EYE;
			}
			else
			{
				x = evt.fs.gx[eye_used];   /* get gaze position from sample  */
				y = evt.fs.gy[eye_used];
				if(x!=MISSING_DATA && y!=MISSING_DATA &&
					evt.fs.pa[eye_used]>0)  /* plot if not in blink */
                {                        /* plot in local coords   */
					draw_gaze_cursor(track2local_x(x), 
                                    track2local_y(y));
                              /* report gaze position (tracker coords) */
               
                     {
					   SDL_Rect r = {(INT16)(SCRWIDTH*0.87), 0, (INT16)(window->w -SCRWIDTH*0.87), 50};
					   SDL_FillRect(window,&r,SDL_MapRGB(window->format,0, 0, 0));
                       graphic_printf(window, target_foreground_color, NONE, (int)(SCRWIDTH*0.87), 0, " %4.0f  ", x);
                       graphic_printf(window, target_foreground_color, NONE, (int)(SCRWIDTH*0.93), 0, " %4.0f  ", y);
                     }
                   ox = x;
                   oy = y;
                 }
				else
				{
					erase_gaze_cursor();   /* hide cursor during blink */
				}
                
				/* print tracker timestamp of sample */
				{
			   		SDL_Rect r = {(INT16)(SCRWIDTH*0.75), 0, (INT16)(SCRWIDTH*0.87 -SCRWIDTH*0.75), 50};
					SDL_FillRect(window,&r,SDL_MapRGB(window->format,0, 0, 0));
					graphic_printf(window,target_foreground_color, NONE, (int)(SCRWIDTH*0.75), 0, " % 8d ", evt.fs.time);
				}
			}
		}
    }	
  erase_gaze_cursor();   /* erase gaze cursor if visible */
  return 0;
}

