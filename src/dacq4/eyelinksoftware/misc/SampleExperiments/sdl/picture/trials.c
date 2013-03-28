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

#include "picture.h"
#include <sdl_text_support.h>
#ifdef MACOSX
#include <SDL_gfx/SDL_rotozoom.h>
#include <SDL_image/SDL_image.h>
#else
#include <SDL/SDL_image.h>
#include <SDL/SDL_rotozoom.h>
#endif



#define NTRIALS 3
char *imgname[NTRIALS] = {"Normal", "Blurred", "Composite"};
char *images[3] = { "images/sacrmeto.jpg", "images/sac_blur.jpg", "images/composite.jpg" };


/* 
	Adds individual pieces of source bitmap to create a composite picture
	Top-left placed at (x,y)
	If either the width or height of the display is 0, simply copy the bitmap 
	to the display without chaning its size. Otherwise, stretches the bitmap to to 
	fit the dimensions of the destination display area
*/
int add_bitmap(SDL_Surface * src, SDL_Surface * dst, int x, int y, int width, int height)
{
	SDL_Rect dstrect = {x,y,width,height};
	SDL_Rect srcrect = {0,0,width,height};
	if(src->w != srcrect.w || src->h != srcrect.h)
	{
	  double zx = (double)srcrect.w/(double)src->w;
	  double zy = (double)srcrect.h/(double)src->h;
	  SDL_Surface *resized = zoomSurface(src,zx,zy,0);
	  if(resized)
		src = resized;
	}
	SDL_BlitSurface(src,&srcrect,dst,&dstrect);
	return 0;
}

SDL_Surface * image_file_bitmap(char *fname, int keepsize, int dx, int dy,
								int bgcolor)
{
  SDL_Surface *image = NULL;
#if defined(MACOSX) && defined(MACAPP)
  char macfilename[1024];
  if(get_resources_path())
  	{
		strcpy(macfilename, get_resources_path());
		strcat(macfilename,"/");
		strcat(macfilename,fname);
  		fname = macfilename;
	}
#endif
  image = IMG_Load(fname);
  if(!image)
  {
	 printf( "Error opening  Image %s. %s \n", 
		 fname, SDL_GetError());
	 return NULL;
  }
  if(keepsize)
	return image;

  if(!dx || !dy) /* dx or dy is 0 - make it to full screen size */
  {
	  SDL_Surface * mainsurface = SDL_GetVideoSurface();
	  dx = mainsurface->w;
	  dy = mainsurface->h;
  }

  if(dx && dy && dx != image->w && dy != image->h)
  {
	  double zx = (double)dx/(double)image->w;
	  double zy = (double)dy/(double)image->h;
	  SDL_Surface *zoomed = zoomSurface(image,zx,zy,0);

	  if(zoomed)
	  {
#ifndef MACOSX
		  SDL_Surface *hwsurface = SDL_CreateRGBSurface(SDL_HWSURFACE,zoomed->w, zoomed->h, dispinfo.bits,0,0,0,0);
		  if(hwsurface->flags & SDL_HWSURFACE)
		  {
			  SDL_BlitSurface(zoomed,NULL,hwsurface,NULL);
			  SDL_FreeSurface(zoomed);
			  zoomed = hwsurface;
		  }
#endif
		  SDL_FreeSurface(image);
		  return zoomed;
	  }
  }
  return image;

}

/* 
	Creates a composite bitmap based on individual pieces
*/
SDL_Surface * composite_image(void)
{
  int i = 0;
  /* Handle to the background and forground bitmaps */
  SDL_Surface*	bkgr;
  SDL_Surface*  img;				
	
  /* Filenames of the four small images */
  char *small_images[4]={"images/hearts.jpg", "images/party.jpg", 
					     "images/squares.jpg", "images/purses.jpg"}; 
  
  /* 
	The x,y coordinates of the top-left corner of the region where
	the individual small image is displayed
	*/
  SDL_Rect points[4]={
	  {0, 0},
	  {SCRWIDTH/2, 0}, 
	  {0, SCRHEIGHT/2}, 
	  {SCRWIDTH/2, SCRHEIGHT/2}
  }; 
	


  /* Create a blank bitmap on which the smaller images are overlaid */
  bkgr = SDL_CreateRGBSurface(SDL_SWSURFACE,SCRWIDTH,SCRHEIGHT,
								dispinfo.bits,0,0,0,0);
  if(!bkgr) 
	  return NULL;
  SDL_FillRect(bkgr,NULL,SDL_MapRGB(bkgr->format, 128,128,128));
  

  /* loop through four small images */
  for (i=0; i<4; i++)  
  {	
	
	/* 
	   Load the small images, keep the original size
	   If the image can not be loaded, delete the created blank bitmap;
	*/
	img = image_file_bitmap(small_images[i], 1, 0, 0, 0);		
	if(!img)
	{
		SDL_FreeSurface(bkgr);
		return NULL;
	}

	/* 
	Add the current bitmap to the blank bitmap at x, y position, 
	resizing the bitmap to the specified width and height
	If the original size is to be kept, set the width and 
	height paremeters to 0
	*/
	add_bitmap(img, bkgr, points[i].x, points[i].y, SCRWIDTH/2, SCRHEIGHT/2);	
		
	/* IMGLOAD command is recorded for EyeLink Data Viewer analysis
       It displays a default image on the overlay mode of the trial viewer screen. 
       Writes the image filename + path info
	   The IMGLOAD TOP_LEFT command specifies an image to use as a segment of the 
	   spatial overlay view with specific top left x,y coordinates and image width and height 					
	*/
	eyemsg_printf("!V IMGLOAD TOP_LEFT %s %d %d %d %d", small_images[i], 
		points[i].x, points[i].y, SCRWIDTH/2, SCRHEIGHT/2); 
 	
	/* IAREA command is recorded for EyeLink Data Viewer analysis
	   Another way of handling segment information by recording the content field 
	   in IAREA RECTANGLE command.
	   The fields are: segment id, (x, y) coordinate of top-left and bottom-right positions
	*/
	eyemsg_printf("!V IAREA RECTANGLE %d %d %d %d %d %s", 
	       i+1, points[i].x, points[i].y, 
		   points[i].x + SCRWIDTH/2, points[i].y + SCRHEIGHT/2, small_images[i]);
 
	/* Be sure to delete bitmap handle before re-using it. */
	SDL_FreeSurface(img);
  }

  /* If the operation is successful, the background image is now 
	 overlaid with the smaller images */
  return bkgr;
 
}

/* 
	Create foreground and background bitmaps of picture
	EyeLink graphics: blank display with box at center
	type: 
		0 = blank background, 
		1 = blank fovea (mask), 
		2 = blurred background
*/
SDL_Surface * create_image_bitmap(int type)
{ 

  set_calibration_colors(&target_foreground_color, &target_background_color); /* tell EXPTSPPT the colors */
  clear_full_screen_window(target_background_color);

  eyecmd_printf("clear_screen 0");         /* clear EyeLink display */
  eyecmd_printf("draw_box %d %d %d %d 15", /* Box around fixation point */
           SCRWIDTH/2-16, SCRHEIGHT/2-16, SCRWIDTH/2+16, SCRHEIGHT/2+16);

/* NOTE:*** THE FOLLOWING TEXT SHOULD NOT APPEAR IN A REAL EXPERIMENT!!!!***/
  get_new_font("Arial", 24, 1);
  graphic_printf(window, target_foreground_color, CENTER, SCRWIDTH/2, SCRHEIGHT/2, 
					"Loading image...");
  Flip(window);
  switch(type)
    {  
      case 0:     /* normal image */
        eyemsg_printf("!V IMGLOAD FILL images/sacrmeto.jpg");
		return image_file_bitmap("images/sacrmeto.jpg",
									0,SCRWIDTH,SCRHEIGHT,0);
      case 1:     /* blurred image */
        eyemsg_printf("!V IMGLOAD FILL images/sac_blur.jpg");
        return image_file_bitmap("images/sac_blur.jpg",
									0, SCRWIDTH,SCRHEIGHT,0);
      case 2:     /* composite image */
        return composite_image();
    }

  return NULL;
}

/***************************TRIAL SETUP AND RUN*******************************/
/* 
	FOR EACH TRIAL:
		- set title, TRIALID
		- Create bitmaps and EyeLink display graphics
		- Check for errors in creating bitmaps
		- Run the trial recording loop
		- Delete bitmaps
		- Return any error code
 */

/* 
	Given trial number, execute trials
	Returns trial result code
*/
int do_picture_trial(int num)
{
  SDL_Surface * bitmap;
  int i;

  /* This supplies the title at the bottom of the eyetracker display  */
  eyecmd_printf("record_status_message '%s, TRIAL %d/%d' ", 
				imgname[num-1],num, NTRIALS);

  /* Always send a TRIALID message before starting to record. 
     It should contain trial condition data required for analysis.
   */
  eyemsg_printf("TRIALID PIX%d %s", num, imgname[num-1]);

  /* TRIAL_VAR_DATA message is recorded for EyeLink Data Viewer analysis
     It specifies the list of trial variables value for the trial 
     This must be specified within the scope of an individual trial (i.e., after 
	 "TRIALID" and before "TRIAL_RESULT") 
  */
  eyemsg_printf("!V TRIAL_VAR_DATA %s", imgname[num-1]);	

  set_offline_mode();/* Must be offline to draw to EyeLink screen */

  bitmap = create_image_bitmap(num-1); 
  if(!bitmap)
    {
      alert_printf("ERROR: could not create image %d", num);
      return SKIP_TRIAL;
    }

  /*NOTE:** THE FOLLOWING TEXT SHOULD NOT APPEAR IN A REAL EXPERIMENT!!!! **/
  clear_full_screen_window(target_background_color);
  get_new_font("Arial", 24, 1);
  graphic_printf(window,target_foreground_color, CENTER, SCRWIDTH/2, 
					SCRHEIGHT/2, "Sending image to EyeLink...");
  Flip(window);

  /* Transfer bitmap to tracker as backdrop for gaze cursors */
	bitmap_to_backdrop(bitmap, 0, 0, 0, 0,0, 0, 
		(UINT16)(BX_MAXCONTRAST|((eyelink_get_tracker_version(NULL)>=2)?0:BX_GRAYSCALE)));  

  

  /* record the trial */
  i = bitmap_recording_trial(bitmap, 20000L); 
  SDL_FreeSurface(bitmap);
  return i;
}

/******************************* TRIAL LOOP ********************************/


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
  
  SETCOLOR(target_background_color,128,128,128);   /* This should match the display  */
  set_calibration_colors(&target_foreground_color, &target_background_color); 
  /*	TRIAL_VAR_LABELS message is recorded for EyeLink Data Viewer analysisIt specifies the list of trial variables for the trial 
		This should be written once only and put before the recording of individual trials
  */
  eyemsg_printf("TRIAL_VAR_LABELS TYPE");

  /* PERFORM CAMERA SETUP, CALIBRATION */
  do_tracker_setup();

  /* loop through trials */
  for(trial=1;trial<=NTRIALS;trial++)
    {
	  /* drop out if link closed */
      if(eyelink_is_connected()==0 || break_pressed())    
		return ABORT_EXPT;
	
				/* RUN THE TRIAL */
      i = do_picture_trial(trial);
      end_realtime_mode();

      switch(i)         	/* REPORT ANY ERRORS */
		{
		  case ABORT_EXPT:/* handle experiment abort or disconnect */
			eyemsg_printf("EXPERIMENT ABORTED");
			return ABORT_EXPT;
		  case REPEAT_TRIAL:	  /* trial restart requested */
			eyemsg_printf("TRIAL REPEATED");
			trial--;
			break;
		  case SKIP_TRIAL:	  /* skip trial */
			eyemsg_printf("TRIAL ABORTED");
			break;
		  case TRIAL_OK:          // successful trial
			eyemsg_printf("TRIAL OK");
			break;
		  default:                // other error code
			eyemsg_printf("TRIAL ERROR");
			break;
		}
    }  // END OF TRIAL LOOP
  return 0;
}

