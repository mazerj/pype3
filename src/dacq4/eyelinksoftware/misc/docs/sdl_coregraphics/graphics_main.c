/**********************************************************************************
 * EYELINK PORTABLE EXPT SUPPORT      (c) 1996- 2006 by SR Research               *
 *     15 July 2003 by Suganthan Subramaniam       For non-commercial use only    *
 * Header file for standard functions                                             *
 * This module is for user applications   Use is granted for non-commercial       *
 * applications by Eyelink licencees only                                         *
 *                                                                                *
 *                                                                                *
 ******************************************* WARNING ******************************
 *                                                                                *
 * UNDER NO CIRCUMSTANCES SHOULD PARTS OF THESE FILES BE COPIED OR COMBINED.      *
 * This will make your code impossible to upgrade to new releases in the future,  *
 * and SR Research will not give tech support for reorganized code.               *
 *                                                                                *
 * This file should not be modified. If you must modify it, copy the entire file  *
 * with a new name, and change the the new file.                                  *
 *                                                                                *
 **********************************************************************************/




/*!
\file
\brief Example implementation of  graphics initialization using SDL grapphics
environment.

In this file, we detect display information, initialize graphics or close graphics,
write image and save image to disk.

@defgroup misc_example miscellaneous functions
*/


#include "graphics_global.h"
SDL_Surface *mainWindow = NULL; //!< full screen window for all our drawings.




/*!
@ingroup misc_example
  This is an optional function to get information
  on video driver and current mode use this to determine
  if in proper mode for experiment.

  @param[out] di  A valid pointer to DISPLAYINFO is passed in to return values.
  @remark The prototype of this function can be changed to match one's need or
  if it is not necessary, one can choose not to implement this function also.

 */
void ELCALLTYPE get_display_information(DISPLAYINFO *di)
{
  /*
  1. detect the current display mode
  2. fill in values into di
  */

  /* For the demonstration purposes, we assume windows. Other operating systems
     may provide other means of finding the same information.
  */

#ifdef _WIN32
  if(di)
  {
	  HDC hdc = GetDC(NULL);
	  memset(di,0, sizeof(DISPLAYINFO)); // clear everything to 0
	  di->bits = GetDeviceCaps(hdc,BITSPIXEL); // depth
	  di->width = GetDeviceCaps(hdc,HORZRES);  // width
	  di->height = GetDeviceCaps(hdc,VERTRES); // height
	  di->refresh = (float)GetDeviceCaps(hdc,VREFRESH); // refresh rate
  }
#endif
}



/*!
  @ingroup misc_example
  This is an optional function to initialze graphics and calibration system.
  Although, this is optional, one should do the innerds of this function
  elsewhere in a proper manner.

  @remark The prototype of this function can be modified to suit ones needs. Eg.
  The init_expt_graphics of eyelink_core_graphics.dll takes in 2 parameters.

*/
INT16 ELCALLTYPE sdl_init_expt_graphics()
{

  HOOKFCNS fcns;
  memset(&fcns,0,sizeof(fcns)); /* clear the memory */

  /* setup the values for HOOKFCNS */
  fcns.setup_cal_display_hook = setup_cal_display;
  fcns.exit_cal_display_hook  = exit_cal_display;
  fcns.setup_image_display_hook = setup_image_display;
  fcns.image_title_hook       = image_title;
  fcns.draw_image_line_hook   = draw_image_line;
  fcns.set_image_palette_hook = set_image_palette;
  fcns.exit_image_display_hook= exit_image_display;
  fcns.clear_cal_display_hook = clear_cal_display;
  fcns.erase_cal_target_hook  = erase_cal_target;
  fcns.draw_cal_target_hook   = draw_cal_target;
  fcns.cal_target_beep_hook   = cal_target_beep;
  fcns.cal_done_beep_hook     = cal_done_beep;
  fcns.dc_done_beep_hook      = dc_done_beep;
  fcns.dc_target_beep_hook    = dc_target_beep;
  fcns.get_input_key_hook     = get_input_key;


  /* register the call back functions with eyelink_core library */
  setup_graphic_hook_functions(&fcns);

  /* register the write image function */
  set_write_image_hook(writeImage,0);

  /*
  	1. initalize graphics
  	2. if graphics initalization suceeds, return 0 otherewise return 1.
  */

  if ( SDL_Init(SDL_INIT_VIDEO) < 0 ) // Initialize SDL
  {
	  printf( "Couldn't initialize SDL: %s\n",SDL_GetError());
	  return -1;
  }
  else
  {
	DISPLAYINFO di;
	SDL_Surface *screen;
	get_display_information(&di);

	// set the display mode to our current display mode.
	screen= SDL_SetVideoMode(di.width,di.height,di.bits, SDL_FULLSCREEN);
	if(screen)
	{
		SDL_ShowCursor(SDL_DISABLE);
		mainWindow = screen;
	}
	else
	{
		printf("Failed to set video mode %dx%d@%d\n",di.width,di.height,di.bits);
		return -1;
	}
  }

  return 0;
}



/*!
 @ingroup misc_example
  This is an optional function to properly close and release any resources
  that are not required beyond calibration needs.
  @remark the prototype of this function can be modified to suit ones need.
 */
void ELCALLTYPE sdl_close_expt_graphics()
{
	mainWindow = NULL;
	SDL_Quit(); // quit sdl
}




/*!
    @ingroup misc_example
	This is called to check for keyboard input.
	In this function:
	\arg check if there are any input events
	\arg if there are input events, fill key_input and return 1.
		 otherwise return 0. If 1 is returned this will be called
	     again to check for more events.
	@param[out] key_input  fill in the InputEvent structure to return
		 key,modifier values.
	@return if there is a key, return 1 otherwise return 0.

	@remark Special keys and modifiers should match the following code
	Special keys:
	@code

#define F1_KEY    0x3B00
#define F2_KEY    0x3C00
#define F3_KEY    0x3D00
#define F4_KEY    0x3E00
#define F5_KEY    0x3F00
#define F6_KEY    0x4000
#define F7_KEY    0x4100
#define F8_KEY    0x4200
#define F9_KEY    0x4300
#define F10_KEY   0x4400

#define PAGE_UP    0x4900
#define PAGE_DOWN  0x5100
#define CURS_UP    0x4800
#define CURS_DOWN  0x5000
#define CURS_LEFT  0x4B00
#define CURS_RIGHT 0x4D00

#define ESC_KEY   0x001B
#define ENTER_KEY 0x000D

	@endcode

	Modifier: If you are using SDL you do not need to modify the
	modifier value as they match the value.

	@code
#define ELKMOD_NONE   0x0000
#define ELKMOD_LSHIFT 0x0001
#define ELKMOD_RSHIFT 0x0002
#define ELKMOD_LCTRL  0x0040
#define ELKMOD_RCTRL  0x0080
#define ELKMOD_LALT   0x0100
#define ELKMOD_RALT   0x0200
#define ELKMOD_LMETA  0x0400
#define ELKMOD_RMETA  0x0800,
#define ELKMOD_NUM    0x1000
#define ELKMOD_CAPS   0x2000
#define ELKMOD_MODE   0x4000
	@endcode
*/

INT16 ELCALLBACK get_input_key(InputEvent *key_input)
{
	return 0;
}



/*!
	@ingroup misc_example
	This function provides support to writing images to disk. Upon calls
	to el_bitmap_save_and_backdrop or el_bitmap_save this function is
	requested to do the write operaiton in the preferred format.

	@param[in] outfilename Name of the file to be saved.
	@param[in] format  format to be saved as.
	@param[in] bitmap bitmap data to be saved.
	@return if successful, return 0.
*/
int ELCALLBACK writeImage(char *outfilename, IMAGETYPE format, EYEBITMAP *bitmap)
{
	// for our demonstration purposes, we will only use bmp format.


	// create an sdl surface from EYEBITMAP
	SDL_Surface * surf = SDL_CreateRGBSurfaceFrom(bitmap->pixels,
		bitmap->w, bitmap->h, bitmap->depth,bitmap->pitch,0,0,0,0);
	if(surf)
	{
		SDL_SaveBMP(surf,outfilename); // save the bitmap
		SDL_FreeSurface(surf); // release the surface
		return 0;
	}
	return -1;
}


