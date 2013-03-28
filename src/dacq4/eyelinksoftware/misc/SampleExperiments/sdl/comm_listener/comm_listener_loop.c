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
 

#include "comm_listener.h"
#include <string.h>
#include <sdl_text_support.h>


extern int listener_record_display(void);

/* #define PRINT_MESSAGES */ /* uncomment to see all messages for debugging */

/******* MAP TRACKER TO LOCAL DISPLAY ************/

float tracker_pixel_left =   0;   /* tracker gaze coord system */
float tracker_pixel_top =    0;   /* used to remap gaze data */
float tracker_pixel_right =  0;   /* to match our display resolution */
float tracker_pixel_bottom = 0;

/* remap X, Y gaze coordinates to local display */
float track2local_x(float x)
{
  return SCREEN_LEFT + 
           (x - tracker_pixel_left) * SCRWIDTH / 
             (tracker_pixel_right - tracker_pixel_left + 1);
}

float track2local_y(float y)
{
  return SCREEN_TOP + 
           (y - tracker_pixel_top) * SCRHEIGHT / 
             (tracker_pixel_bottom - tracker_pixel_top + 1);
}


/*********** LISTENING LOOP **************/

void listening_loop(void)
{
  int i;

  char trial_word[40];  /* Trial stimulus word (from TRIALID message) */
  char first_word[40];  /* first word in message (determines processing) */

  tracker_pixel_left = (float)SCREEN_LEFT;    /* set default display mapping */
  tracker_pixel_top = (float)SCREEN_TOP;
  tracker_pixel_right = (float)SCREEN_RIGHT;
  tracker_pixel_bottom = (float)SCREEN_BOTTOM;

      /* 
			Now we loop through processing any link data and messages
			The link will be closed when the COMM_SIMPLE application exits
			This will also close our broadcast connection and exit this loop
	   */
  while(eyelink_is_connected())
    {
      ALLF_DATA data;   /* link data or messages */
                        /* exit if ESC or ALT-F4 pressed */
      if(escape_pressed() || break_pressed()) return; 
                        
      i = eyelink_get_next_data(NULL);   /* check for new data item */
      if(i == 0) continue;

      if(i == MESSAGEEVENT)   /* message: check if we need the data */
        {
	  eyelink_get_float_data(&data);
#ifdef PRINT_MESSAGES   /* optionally, show messages for debugging */
          get_new_font("Times Roman", SCRHEIGHT/55, 1);         /* select a font */
          graphic_printf(window, target_foreground_color, NONE, SCRWIDTH/15, j++*SCRHEIGHT/55, 
                    "MESSAGE=%s", data.im.text);
#endif
          sscanf(data.im.text, "%s", first_word);  /* get first word */
          if(!_stricmp(first_word, "DISPLAY_COORDS"))
            {         /* get COMM_SIMPLE computer display size */
              sscanf(data.im.text, "%*s %f %f %f %f", 
                     &tracker_pixel_left, &tracker_pixel_top,
                     &tracker_pixel_right, &tracker_pixel_bottom);
            }
          else if(!_stricmp(first_word, "TRIALID"))
            { 
	              /* get TRIALID information */
              sscanf(data.im.text, "%*s %s", trial_word);
                      /* Draw stimulus (exactly as was done in COMM_SIMPLE) */
#ifndef PRINT_MESSAGES
	      clear_full_screen_window(target_background_color);  
#endif
                      /* We scale font size for difference in display resolutions */
              get_new_font("Times Roman", 
                            (int) (SCRWIDTH/25.0 * 
                              SCRWIDTH/(tracker_pixel_right-tracker_pixel_left+1)), 1);        
              graphic_printf(window, target_foreground_color,  NONE,      
                             (int) (SCRWIDTH/2), (int)(SCRHEIGHT/2), "%s", trial_word);
			  Flip(window); // 
			  graphic_printf(window, target_foreground_color,  NONE,      
                             SCRWIDTH/2, SCRHEIGHT/2, "%s", trial_word); /* to the back buffer */
            }
        }
                 /* link data block opened for recording? */
      if(eyelink_in_data_block(1, 1))
        {   
          listener_record_display(); /* display gaze cursor on stimulus */
                                     /* clear display at end of trial */
#ifndef PRINT_MESSAGES
          clear_full_screen_window(target_background_color);  
#endif
        }
    }
}

