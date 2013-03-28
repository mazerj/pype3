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


#include <string.h>
#include "comm_listener.h"
#include <sdl_text_support.h>
#include <gazecursor.h>

/* functions to map gaze from tracker to local pixels */
extern float track2local_x(float x);
extern float track2local_y(float y);





/********* PLOT GAZE DATA DURING RECORDING  *******/	 
int listener_record_display(void)
{
  ALLF_DATA evt;
  UINT32 trial_start_time = 0;
  unsigned key;
  int eye_used;        /* which eye to show gaze for */
  float x, y;	       /* gaze position */
  float ox=-1, oy=-1;  /* old gaze positio (to determine change) */
  int i;
	
  /* create font for position display */
  get_new_font( "Arial", SCRWIDTH/50, 0);

  initialize_cursor(window, SCRWIDTH/50);

  eye_used = eyelink_eye_available();
  if(eye_used==BINOCULAR) eye_used = LEFT_EYE;/* use left eye if both available */
  
  while(eyelink_is_connected())  /* loop while record data availablemode */
    {
      key = getkey();            /* Local keys/abort test */
      if(key==TERMINATE_KEY)     /* test ALT-F4 or end of execution */
         break;

      if(!eyelink_in_data_block(1, 1)) 
		  break;  /* stop if end of record data */
      i = eyelink_get_next_data(NULL);   /* check for new data item */
      if(i == MESSAGEEVENT)   /* message: check if we need the data */
        {
          eyelink_get_float_data(&evt);     /* get message */
                           /* get trial start time from "SYNCTIME" message */
          if(!_strnicmp(evt.im.text, "SYNCTIME", 8))
            {
              trial_start_time = 0;    /* offset of 0, if none given */
              sscanf(evt.im.text, "%*s %d", &trial_start_time);
              trial_start_time = evt.im.time - trial_start_time;  
            }
#ifdef PRINT_MESSAGES
	  graphic_printf(window, target_foreground_color, NONE, SCRWIDTH/100, j++*SCRHEIGHT/50, 
                    "MESSAGE=%s", evt.im.text);
#endif
        }

#ifdef LOST_DATA_EVENT     /* only available in V2.1 or later DLL */
      if(i == LOST_DATA_EVENT)   /* marks lost data in stream */
	alert_printf("Some link data was lost");
#endif

            /* CODE FOR PLOTTING GAZE CURSOR  */
      if(eyelink_newest_float_sample(NULL)>0)  /* new sample? */
		{
			eyelink_newest_float_sample(&evt);  /* get the sample data */
			x = evt.fs.gx[eye_used];   /* get gaze position from sample  */
			y = evt.fs.gy[eye_used];

			if(x!=MISSING_DATA && y!=MISSING_DATA &&
             evt.fs.pa[eye_used]>0)  /* plot if not in blink */
            {                        /* plot in local coords */
              draw_gaze_cursor((int)track2local_x(x), 
                               (int)track2local_y(y));
                      /* report gaze position (tracker coords) */
              if(ox!=x || oy!=y)   /* only draw if changed */
                {
				  SDL_Rect r = {(Sint16)(SCRWIDTH*0.87), 0, (Sint16)(window->w -SCRWIDTH*0.87), 50};
				  SDL_FillRect(window,&r,SDL_MapRGB(window->format,target_background_color.r, target_background_color.g, target_background_color.b));
                  graphic_printf(window, target_foreground_color, NONE, (int)(SCRWIDTH*0.87), 0, " %4.0f  ", x);
                  graphic_printf(window,target_foreground_color, NONE, (int)(SCRWIDTH*0.93), 0, " %4.0f  ", y);
                }
              ox = x;
              oy = y;
            }
          else
            {
				erase_gaze_cursor();   /* hide cursor during blink */
			}
              /* print time from start of trial */
		  {
			SDL_Rect r = {(Sint16)(SCRWIDTH*0.75), 0, (Sint16)(SCRWIDTH*0.87 -SCRWIDTH*0.75), 50};
			SDL_FillRect(window,&r,SDL_MapRGB(window->format,target_background_color.r, target_background_color.g, target_background_color.b));
			graphic_printf(window, target_foreground_color,NONE, (int)(SCRWIDTH*0.75), 0, " % 8d ", 
				             evt.fs.time-trial_start_time);
		  }
        }
    }
  erase_gaze_cursor();   /* erase gaze cursor if visible */
  return 0;
}

