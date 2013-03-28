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

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "broadcast.h"
#include <sdl_text_support.h>


           
/*  display information: size, colors, refresh rate */
DISPLAYINFO dispinfo;
SDL_Surface *window = NULL;

/*	The colors of the target and background for 
	calibration and drift correction */
SDL_Color target_foreground_color = {255,255,255};   // targets
SDL_Color target_background_color = {128,128,128};   // background
SDL_Color transparent_key_color = {0,0,0};       // transparent video key color


/***************************** PREVIEW TRACKER STATE ************************
	checks link state of tracker
	DLL must have been started with open_eyelink_connection(-1)
	to allow unconnected time and message communication
	RETURNS: -1 if no reply
           0 if tracker free
          LINK_CONNECTED if connected to another computer
          LINK_BROADCAST if already broadcasting
*/
int preview_tracker_connection(void)
{
  UINT32 t, tt;
  ILINKDATA *idata = eyelink_data_status();  /* access link status info */
  eyelink_request_time();         /* force tracker to send status and time */
  t = current_msec();
  while(current_msec()-t < 500)   /* wait for response */
    {
      tt = eyelink_read_time();   /* will be nonzero if reply */
      if(tt != 0)
        {                         /* extract connection state */
          if(idata->link_flags & LINK_BROADCAST) return LINK_BROADCAST;
          if(idata->link_flags & LINK_CONNECTED) return LINK_CONNECTED;
          else return 0;
        }
      message_pump();         /* keep Windows happy */
      if(break_pressed()) return 1;  /* stop if program terminated */
    }
  return -1;  /* failed (timed out) */
}


/********* WAIT FOR A CONNECTION TO TRACKER **********/

int wait_for_connection(void)
{
  int i;
  int first_pass = 1;   /* draw display only after first failure */

  while(1)          /* loop till a connection happens */
    {               /* check if tracker is connected */
      i = preview_tracker_connection();
      if(i == -1)
        {
          alert_printf("Cannot find tracker");
          return -1;
        }
      else if(i > 0)
        return 0;  /* we have a connection! */

      if(first_pass)   /*If not, draw title screen */
        {
		  SDL_Color bg = {192,192,192};
		  SDL_Color fg = {0,0,0};
          first_pass = 0;  /*don't draw more than once */

          clear_full_screen_window(bg);
          get_new_font("Times Roman", SCRHEIGHT/32, 1);   /*select a font */
          i = 1;
          graphic_printf(window, fg, NONE, SCRWIDTH/15, i++*SCRHEIGHT/26,
                    "EyeLink Broadcast Listening Demonstration");
          graphic_printf(window, fg, NONE, SCRWIDTH/15, i++*SCRHEIGHT/26,
                    "Copyright 2002 SR Research Ltd.");
          i++;
          graphic_printf(window, fg, NONE, SCRWIDTH/15, i++*SCRHEIGHT/26,
                    "Waiting for another computer to connect to tracker...");
          graphic_printf(window, fg, NONE, SCRWIDTH/15, i++*SCRHEIGHT/26,
                    "Press ESC to exit from this screen");
          graphic_printf(window, fg, NONE, SCRWIDTH/15, i++*SCRHEIGHT/26,
                    "Press ALT-F4 to exit while connected");
		  SDL_Flip(window);
        }

      i = getkey();         /*check for exit */
      if(i==ESC_KEY || i==TERMINATE_KEY) return 1;

      Sleep(500);   /*go to background, don't flood the tracker */
    }
}


/******* MAP TRACKER TO LOCAL DISPLAY ************/

int can_read_pixel_coords = 1;    /*does tracker support read? */
float tracker_pixel_left = 0;     /*tracker gaze coord system */
float tracker_pixel_top = 0;      /*used to remap gaze data */
float tracker_pixel_right = 0;    /*to match our display resolution */
float tracker_pixel_bottom = 0;

        /* 
			Read setting of "screen_pixel_coords" from tracker
			This allows remapping of gaze data if our display
			has a different resolution than the connected computer
			The read may fail with older tracker software
		 */
int read_tracker_pixel_coords(void)
{
  char buf[100] = "";
  UINT32 t;

  if(!eyelink_is_connected() || break_pressed()) return 1;    /* not connected */
  eyelink_read_request("screen_pixel_coords");
  t = current_msec();
  while(current_msec()-t < 500)
    {
      if(eyelink_read_reply(buf) == OK_RESULT)
        {
          sscanf(buf, "%f,%f,%f,%f",
                  &tracker_pixel_left, &tracker_pixel_top,
                  &tracker_pixel_right, &tracker_pixel_bottom );
          return 0;
        }
      message_pump();  /* keep Windows happy */
      if(!eyelink_is_connected) return 1;
      if(break_pressed()) return 1;
    }
  return -1;  /* timed out */
}

         /* remap X, Y gaze coordinates to local display */
INT16 track2local_x(float x)
{
  return (INT16)(SCREEN_LEFT +
           (x - tracker_pixel_left) * SCRWIDTH /
             (tracker_pixel_right - tracker_pixel_left + 1));
}

INT16 track2local_y(float y)
{
  return (INT16)(SCREEN_TOP +
           (y - tracker_pixel_top) * SCRHEIGHT /
             (tracker_pixel_bottom - tracker_pixel_top + 1));
}


/************ CALIBRATION TARGET REMAP ************/

           /*	
				callback for calibration target drawing 
				this moves target to match position on other displays
		   */
static HOOKFCNS hfcns;
void ELCALLBACK remap_cal_target(INT16 x, INT16 y)
{
  x = track2local_x(x);
  y = track2local_y(y);
  if(hfcns.draw_cal_target_hook)
	  hfcns.draw_cal_target_hook(x,y);
}


  // setup "hook" function to be called before calibration targets drawn
void setup_remap_hooks(void)
{
	HOOKFCNS *hooks = get_all_hook_functions();
	memcpy(&hfcns,hooks,sizeof(HOOKFCNS));
	
	hooks->draw_cal_target_hook = remap_cal_target;
    setup_graphic_hook_functions(hooks);
}


/*********** FOLLOW TRACKER MODES **********/

/* 
	external funtion to handle record mode
	returns non-zero to terminate
*/
extern int record_mode_display(void);

/* 
	Follow and process tracker modes
	Displays calibration and drift correction targets
	Also detects start of recording
	Black backgrounds would be transparent as video overlay
 */
void track_mode_loop(void)
{
  int oldmode = -1;  /* to force initial mode setup */

  while(eyelink_is_connected())
    {
      int mode = eyelink_tracker_mode();
      UINT16 key = getkey();

      if(key==27 || break_pressed() || !eyelink_is_connected()) return;
      else if(key)                  	/* echo to tracker */
        eyelink_send_keybutton(key,0,KB_PRESS);

      if(mode == oldmode) continue;
      switch(mode)
        {
          case EL_RECORD_MODE:        /* Record mode: show gaze cursor */
            clear_full_screen_window(transparent_key_color);
            record_mode_display();
            clear_full_screen_window(transparent_key_color);
            break;

          case EL_IMAGE_MODE:     /* IMAGE NOT AVAILABLE IN BROADCAST */
            break;

          case EL_SETUP_MENU_MODE:  /* setup menu: just blank display */
            clear_full_screen_window(target_background_color);
                                    /* read gaze coords in case changed */
            if(eyelink_is_connected() && can_read_pixel_coords)
               read_tracker_pixel_coords();
            break;

          case EL_CALIBRATE_MODE:    /* show calibration targets */
            if(eyelink_is_connected() && can_read_pixel_coords)
               read_tracker_pixel_coords();
          case EL_VALIDATE_MODE:
          case EL_DRIFT_CORR_MODE:
            target_mode_display();
            break;

          case EL_OPTIONS_MENU_MODE:  /* no change in visibility */
            break;

          default:                    /* any other mode: transparent key (black) */
            clear_full_screen_window(transparent_key_color);
            break;
        }
      oldmode = mode;
    }
}


/*********** MAIN: SETUP, CLAENUP **********/

int app_main(char * trackerip, DISPLAYINFO * disp)
{
  int i, j;

  if(trackerip)
		set_eyelink_address(trackerip);
  else
	  	set_eyelink_address("100.1.1.1");
  


       /* open DLL to allow unconnected communications */
  if(open_eyelink_connection(-1))
    return -1;    /* abort if we can't open link */

  eyelink_set_name("broadcast");  /* set our network name */

  if(init_expt_graphics(NULL, disp))   /* register window for cal/image */
      goto shutdown;

  window = SDL_GetVideoSurface();

  get_display_information(&dispinfo);     /* get display size, characteristics */

     /* NOTE: Camera display does not support 16-color modes */
  if(dispinfo.palsize==16)      /* 16-color modes not functional */
    {
      alert_printf("This program cannot use 16-color displays");
      goto shutdown;
    }

  flush_getkey_queue();                 /* initialize getkey() system */


  i = SCRWIDTH/60;      /* select best size for calibration target */
  j = SCRWIDTH/300;       /* and focal spot in target */
  if(j < 2) j = 2;
  set_target_size((UINT16)i, (UINT16)j);  /* tell DLL the size of target features */

  /* 
	calibration should be on gray background
	in order to overlay any video 
  */
  set_calibration_colors(&target_foreground_color, &target_background_color);

  set_cal_sounds("", "", "");           /* default sounds */
  set_dcorr_sounds("", "off", "off");   /* disable drift correction sounds */

  setup_remap_hooks();

  while(1)  /* Loop through one or more sessions */
    {
                /* wait for connection to listen to, or aborted */
      if(wait_for_connection()) goto shutdown;
      pump_delay(1000);   /* give remote and tracker time for setup */
                      /* now we can start to listen in */
      if(eyelink_broadcast_open())
        {
          alert_printf("Cannot open broadcast connection to tracker");
          goto shutdown;
        }

      clear_full_screen_window(transparent_key_color);

      can_read_pixel_coords = 1;           /* first try to read coords */
      tracker_pixel_left = (float)SCREEN_LEFT;    /* set defaults in case fails */
      tracker_pixel_top = (float)SCREEN_TOP;
      tracker_pixel_right = (float)SCREEN_RIGHT;
      tracker_pixel_bottom = (float)SCREEN_BOTTOM;
      if(eyelink_is_connected())
	if(read_tracker_pixel_coords()==-1)
	  {
            alert_printf("Cannot determine tracker pixel coords: assuming %dx%d", SCRWIDTH, SCRHEIGHT);
            can_read_pixel_coords = 0;
	  }

      track_mode_loop();   /* listen and process by tracker mode */
      if(break_pressed())  /* make sure we're still alive */
         goto shutdown;
    }

shutdown:                /* CLEANUP */
  pump_delay(500);	/* give tracker time to execute all commands */ 
  close_expt_graphics();           /* tell EXPTSPPT to release window */
  close_eyelink_connection();      /* make sure EYELINK DLL is released */

  return 0;
}

   
int parseArgs(int argc, char **argv, char **trackerip, DISPLAYINFO *disp )
{
	int i =0;
	int displayset =0;
	memset(disp,0,sizeof(DISPLAYINFO));
	for( i =1; i < argc; i++)
	{
		if(_stricmp(argv[i],"-tracker") ==0 && argv[i+1])
		{
			*trackerip = argv[i+1];
			i++;
		}
		else if(strcmp(argv[i],"-width") ==0 && argv[i+1])
		{
			i++;
			disp->width = atoi(argv[i]);
			displayset = 1;
		}
		else if(_stricmp(argv[i],"-height") ==0 && argv[i+1])
		{
			i++;
			disp->height = atoi(argv[i]);
			displayset = 1;
		}
		else if(_stricmp(argv[i],"-bpp") ==0 && argv[i+1])
		{
			i++;
			disp->bits = atoi(argv[i]);
		}
		else if(_stricmp(argv[i],"-refresh") ==0 && argv[i+1])
		{
			i++;
			disp->refresh = (float)atoi(argv[i]);
		}
		else
		{
			printf("%d \n", i);
			printf("usage %s \n", argv[0]);
			printf("\t options: \n");
			printf("\t[-tracker <tracker address > ] eg. 100.1.1.1 \n");
			printf("\t[-width   <screen width>]  eg. 640, 800, 1280\n");
			printf("\t[-height  <screen height>] eg. 480, 600, 1024\n");
			printf("\t[-bpp     <color depth>]   eg. 16,24,32\n");
			printf("\t[-refresh refresh value]   eg. 60, 85, 85 \n");
			return 1;
		}

	}
	if(displayset && !disp->width && !disp->height)
		return 1;
	return 0;
}
#if  defined(WIN32) && !defined(_CONSOLE)
/* WinMain - Windows calls this to execute application */
int PASCAL WinMain( HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow)
{
	app_main(NULL,NULL);/* call our real program */
	return 0;
}
#else
/* non windows application or win32 console application. */
int main(int argc, char ** argv)
{
	DISPLAYINFO disp;
	char *trackerip = NULL;
	int rv = parseArgs(argc,argv, &trackerip, &disp);
	if(rv) return rv;

	if(disp.width)
		app_main(trackerip, &disp);/* call our real program */
	else
		app_main(trackerip, NULL);/* call our real program - no display parameters set*/
	return 0;
}
#endif

void clear_full_screen_window(SDL_Color c)
{
	SDL_FillRect(window, NULL, SDL_MapRGB(window->format, c.r, c.g, c.b));
	SDL_Flip(window);
	SDL_FillRect(window, NULL, SDL_MapRGB(window->format, c.r, c.g, c.b)); /* to the background */
}
