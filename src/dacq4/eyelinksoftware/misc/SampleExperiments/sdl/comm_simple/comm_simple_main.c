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
#include "comm_simple.h"
#include <sdl_text_support.h>


DISPLAYINFO dispinfo;  /*display information: size, colors, refresh rate */
SDL_Surface *window = NULL;

/*	The colors of the target and background for
	calibration and drift correction */
SDL_Color target_foreground_color = {0,0,0};
SDL_Color target_background_color = {192,192,192};

/* Name for experiment: goes in task bar, and in EDF file */
char program_name[100] = "Windows Sample Experiment 2.0";
ELINKADDR listener_address;   /* Network address of listerner application */



void clear_full_screen_window(SDL_Color c)
{
	SDL_FillRect(window, NULL, SDL_MapRGB(window->format, c.r,  c.g, c.b));
	SDL_Flip(window);
	SDL_FillRect(window, NULL, SDL_MapRGB(window->format, c.r,  c.g, c.b));

}

/******** OPEN COMMUNICATION WITH LISTENER (NEW) **********/

/*
	node reception "helper" function
	receives text message from another application
	checks for time out (max wait of 'time' msec)
*/
int get_node_response(char *buf, UINT32 time)
{
  UINT32 t = current_msec();
  ELINKADDR msgaddr;   /* address of message sender */

  /* wait with timeout */
  while(current_time()-t < time)
    {
      int i = eyelink_node_receive(msgaddr, buf); /* check for data */
      if(i > 0) return i;
    }
  return -1;   /* timeout failure */
}


/*
	finds listener application
	sends it the experiment name and our display resolution
	returns 0 if OK, -1 if error
*/
int check_for_listener(void)
{
  INT16 i, n;
  char message[100];
  ELINKNODE node;  /*  this will hold application name and address */

  eyelink_poll_remotes();  /* poll network for any EyeLink applications */
  pump_delay(500);         /* give applications time to respond */

  n = eyelink_poll_responses();  /* how many responses? */
  for(i=1;i<=n;i++)      /* responses 1 to n are from other applications */
    {
      if(eyelink_get_node(i, &node) < 0) return -1;  /*/ error: no such data */
      if(!_stricmp(node.name, "comm_listener"))
        {           /* Found COMM_LISTENER: now tell it we're ready */
          memcpy(listener_address, node.addr, sizeof(ELINKADDR));
          eyelink_node_send(listener_address, "NAME comm_simple", 40);
                                /* wait for "OK" reply */
          if(get_node_response(message, 1000) <= 0) return -1;
          if(_stricmp(message, "OK")) return -1;   /* wrong response? */
          return 0;   /* all communication checks out. */
        }
    }
  return -1;    /* no listener node found */
}

/**************** ORIGINAL SIMPLE CODE ***********/


int get_tracker_sw_version(char* verstr)
{
	int ln = 0;
	int st =0;
	ln = strlen(verstr);
	while(ln>0 && verstr[ln -1]==' ')  
		verstr[--ln] = 0; // trim 

	// find the start of the version number
	st = ln;
	while(st>0 && verstr[st -1]!=' ')  st --; 
	return atoi(&verstr[st]);
	
}

int app_main(char * trackerip, DISPLAYINFO * disp)
{
  UINT16 i, j;
  char our_file_name[260] = "TEST";
  char verstr[50];
  int eyelink_ver = 0;
  int tracker_software_ver = 0;
  
  if(trackerip)
		set_eyelink_address(trackerip);
  if(open_eyelink_connection(0)) return -1;    /* abort if we can't open link */
  set_offline_mode();
  flush_getkey_queue();                        /* initialize getkey() system */

  eyelink_ver = eyelink_get_tracker_version(verstr);
  if (eyelink_ver == 3)
	  tracker_software_ver = get_tracker_sw_version(verstr);



  if(init_expt_graphics(NULL, disp))
	  goto shutdown;   /* register window with EXPTSPPT */


  window = SDL_GetVideoSurface();
  get_display_information(&dispinfo);          /* get window size, characteristics */

    /*
		NOTE: Camera display does not support 16-color modes
		NOTE: Picture display examples don't work well with 256-color modes
		However, all other sample programs should work well.
	*/

  if(dispinfo.palsize)     /* 256-color modes: palettes not supported by this example */
      alert_printf("This program is not optimized for 256-color displays");


 

  
  i = SCRWIDTH/60;		  /* select best size for calibration target */
  j = SCRWIDTH/300;       /* and focal spot in target */
  if(j < 2) j = 2;
  set_target_size(i, j);  /* tell DLL the size of target features */


  /* color of calibration target */
  SETCOLOR(target_foreground_color, 0,0,0);
  /* background for calibration and drift correction */
  SETCOLOR(target_background_color, 128,128,128);
  /* tell EXPTSPPT the colors */
  set_calibration_colors(&target_foreground_color, &target_background_color);

  set_cal_sounds("", "", "");
  set_dcorr_sounds("", "off", "off");

  /* draw a title screen */
  clear_full_screen_window(target_background_color);    /* clear screen */
  get_new_font("Times Roman", SCRHEIGHT/32, 1);         /* select a font */
                                                        /* Draw text */
  graphic_printf(window, target_foreground_color,  CENTER, SCRWIDTH/2, 1*SCRHEIGHT/30,
                 "EyeLink Demonstration Experiment: Communicate with Listener");
  graphic_printf(window, target_foreground_color,  CENTER, SCRWIDTH/2, 2*SCRHEIGHT/30,
                 "Included with the Experiment Programming Kit for Windows");
  graphic_printf(window, target_foreground_color,  CENTER, SCRWIDTH/2, 3*SCRHEIGHT/30,
                 "All code is Copyright (c) 1997-2002 SR Research Ltd.");
  graphic_printf(window, target_foreground_color,  CENTER, SCRWIDTH/5, 4*SCRHEIGHT/30,
                 "Source code may be used as template for your experiments.");
  SDL_Flip(window);

  eyelink_set_name("comm_simple");  /* NEW: set our network name */

  if(check_for_listener())   /* check for COMM_LISTENER application */
    {
      alert_printf("Could not communicate with COMM_LISTENER application.");
      goto shutdown;
    }

  if(i==1)  our_file_name[0] = 0;   /* Cancelled: No file name */
  if(our_file_name[0])    /* If file name set, open it */
    {
      if(!strstr(our_file_name, ".")) strcat(our_file_name, ".EDF");  /* add extension   */
      i = open_data_file(our_file_name);                              /* open file       */
      if(i!=0)                                                        /* check for error */
        {
          alert_printf("Cannot create EDF file '%s'", our_file_name);
          goto shutdown;
        }
	  /* add title to preamble */
      eyecmd_printf("add_file_preamble_text 'RECORDED BY %s' ", program_name);
    }
  /*
		SET UP TRACKER CONFIGURATION
		NOTE: set contents before sending messages!
		set EDF file contents
  */
   if(eyelink_ver>=2)
    {
      eyecmd_printf("select_parser_configuration 0");  // 0 = standard sensitivity
	  if(eyelink_ver == 2) //turn off scenelink camera stuff
	  {
		eyecmd_printf("scene_camera_gazemap = NO");
	  }
    }
  else
    {
      eyecmd_printf("saccade_velocity_threshold = 35");
      eyecmd_printf("saccade_acceleration_threshold = 9500");
    }
  // NOTE: set contents before sending messages!
		     // set EDF file contents 
  eyecmd_printf("file_event_filter = LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON");
  eyecmd_printf("file_sample_data  = LEFT,RIGHT,GAZE,AREA,GAZERES,STATUS%s",(tracker_software_ver>=4)?",HTARGET":"");
		      // set link data (used for gaze cursor) 
  eyecmd_printf("link_event_filter = LEFT,RIGHT,FIXATION,SACCADE,BLINK,BUTTON");
  eyecmd_printf("link_sample_data  = LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS%s",(tracker_software_ver>=4)?",HTARGET":"");

  /* NEW: Allow EyeLink I (v2.1+) to echo messages back to listener */
  eyecmd_printf("link_nonrecord_events = BUTTONS, MESSAGES");

  /* Program button #5 for use in drift correction */
  eyecmd_printf("button_function 5 'accept_target_fixation'");

  /* Now configure tracker for display resolution */
  eyecmd_printf("screen_pixel_coords = %ld %ld %ld %ld",    /* Set display resolution */
                 dispinfo.left, dispinfo.top, dispinfo.right, dispinfo.bottom);
  eyecmd_printf("calibration_type = HV9");       /* Setup calibration type */
  eyemsg_printf("DISPLAY_COORDS %ld %ld %ld %ld",/* Add resolution to EDF file */
                 dispinfo.left, dispinfo.top, dispinfo.right, dispinfo.bottom);
  if(dispinfo.refresh>40)
    eyemsg_printf("FRAMERATE %1.2f Hz.", dispinfo.refresh);

  

  /* make sure we're still alive */
  if(!eyelink_is_connected() || break_pressed()) goto end_expt;

  /*
	 RUN THE EXPERIMENTAL TRIALS (code depends on type of experiment)
     Calling run_trials() performs a calibration followed by trials
     This is equivalent to one block of an experiment
     It will return ABORT_EXPT if the program should exit
   */
  i = run_trials();

end_expt:                /* END: close, transfer EDF file */
  set_offline_mode();    /* set offline mode so we can transfer file */
  pump_delay(500);       /* delay so tracker is ready */
  eyecmd_printf("close_data_file"); /* close data file */

  if(break_pressed()) goto shutdown;/* don't get file if we aborted experiment */
  if(our_file_name[0])              /* make sure we created a file */
    receive_data_file(our_file_name, "", 0);  /* transfer the file, ask for a local name */

shutdown:                /* CLEANUP */
  close_expt_graphics();           /* tell EXPTSPPT to release window */
  close_eyelink_connection();      /* disconnect from tracker */
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
