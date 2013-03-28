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
#include <stdlib.h>
#include "comm_listener.h"
#include <sdl_text_support.h>



/* the application instance: required to create windows and get resources */
SDL_Surface *window = NULL;  

/* display information: size, colors, refresh rate */
DISPLAYINFO dispinfo;

/* The colors of the target and background for calibration and drift correction */
SDL_Color target_foreground_color = {0,0,0};   /* targets */
SDL_Color target_background_color = {200,200,200}; /* background */

ELINKADDR connected_address;   /* address of comm_simple (from message) */


/********* WAIT FOR A CONNECTION MESSAGE **********
 waits for a inter-application message
 checks message, responds to complete connection
 this is a very simple example of data exchange
 */
int wait_for_connection(void)
{
  int i;
  int first_pass = 1;   /* draw display only after first failure */
  char message[100];

  while(1)          /* loop till a message received */
    {
      i = eyelink_node_receive(connected_address, message);
      if(i > 0)     /* do we have a message? */
        {           /* is it the expected application? */
          if(!_stricmp(message, "NAME comm_simple")) 
            {              /* yes: send "OK" and proceed */
              return 0;
            }
        }

      if(first_pass)   /* If not, draw title screen */
        {
		  SDL_Color colr = { 0,0,0};
          first_pass = 0;  /* don't draw more than once */

          clear_full_screen_window(target_background_color);
          get_new_font("Times Roman", SCRHEIGHT/32, 1);         /* select a font */
          i = 1;
          graphic_printf(window, colr, CENTER, SCRWIDTH/15, i++*SCRHEIGHT/26, 
                    "EyeLink Data Listener and Communication Demonstration");
          graphic_printf(window, colr, CENTER, SCRWIDTH/15, i++*SCRHEIGHT/26, 
                    "Copyright 2002 SR Research Ltd.");
          i++;
          graphic_printf(window, colr, CENTER, SCRWIDTH/15, i++*SCRHEIGHT/26, 
                    "Waiting for COMM_SIMPLE application to send startup message...");
          graphic_printf(window, colr, CENTER, SCRWIDTH/15, i++*SCRHEIGHT/26, 
                    "Press ESC to quit");
		  SDL_Flip(window);
        }

      i = getkey();         /* check for exit */
      if(i==ESC_KEY || i==TERMINATE_KEY) return 1;
    }
}


/*********** MAIN: SETUP, CLAENUP **********/

int app_main(char * trackerip, DISPLAYINFO * disp)
{
  int i;

  if(trackerip)
		set_eyelink_address(trackerip);

  if(init_expt_graphics(NULL, disp))   /* register window for cal/image */
      goto shutdown;  
  window = SDL_GetVideoSurface();


         /* open DLL to allow unconnected communications */
  if(open_eyelink_connection(-1)) 
    return -1;    /* abort if we can't open link */

  eyelink_set_name("comm_listener");  /* set our network name */
  get_display_information(&dispinfo); /* get display size, characteristics */
     /* NOTE: Camera display does not support 16-color modes */
  if(dispinfo.palsize==16)/* 16-color modes not functional */
    {
      alert_printf("This program cannot use 16-color displays");
      goto shutdown;
    }

  flush_getkey_queue();   /* initialize getkey() system */
  
     /* 
		in this simple example, we don't use calibration 
        graphics at all so we don't bother to set them up.
	*/

  while(1)  /* Loop through one or more sessions */
    {
                /* wait for connection to listen to, or aborted */
      if(wait_for_connection()) goto shutdown;  

                /* now we can start to listen in */
      if(eyelink_broadcast_open())
        {
          alert_printf("Cannot open broadcast connection to tracker");
          goto shutdown;     
        }

          /*enable link data reception by EyeLink DLL */
      eyelink_reset_data(1);   
          /*NOTE: this function can discard some link data */
      eyelink_data_switch(RECORD_LINK_SAMPLES | RECORD_LINK_EVENTS);

      pump_delay(500);       // tell COM_SIMPLE it's OK to proceed        
      eyelink_node_send(connected_address, "OK", 10); 

      clear_full_screen_window(target_background_color);
      get_new_font("Times Roman", SCRHEIGHT/32, 1);         // select a font
      i = 1;
      graphic_printf(window, target_foreground_color, NONE, SCRWIDTH/15, i++*SCRHEIGHT/26, 
                    "Listening in on link data and tracker mode...");
	  SDL_Flip(window);

      listening_loop();   // listen and process data and messages
                          // returns when COMM_SIMPLE closes connection to tracker

      if(break_pressed())  // make sure we're still alive
         goto shutdown;   
    }

shutdown:                // CLEANUP
  pump_delay(500);	/* give tracker time to execute all commands */
  close_expt_graphics();           // tell EXPTSPPT to release window
  close_eyelink_connection();        // make sure EYELINK DLL is released
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
	SDL_FillRect(window,NULL,SDL_MapRGB(window->format,c.r, c.g, c.b));
	SDL_Flip(window);
	SDL_FillRect(window,NULL, SDL_MapRGB(window->format,c.r, c.g, c.b));
}