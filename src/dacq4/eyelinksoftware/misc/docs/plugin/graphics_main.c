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
In this file, we detect display information, initialize graphics or close graphics,
write image and save image to disk.
*/

#include <string.h>
#include "graphics_global.h"



/*!
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
}



/*!

  This is an optional function to initialze graphics and calibration system.
  Although, this is optional, one should do the innerds of this function elsewhere in a proper manner.

  @remark The prototype of this function can be modified to suit ones needs. Eg.
  The init_expt_graphics of eyelink_core_graphics.dll takes in 2 parameters.
  
*/
INT16 ELCALLTYPE init_expt_graphics()
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

  return 0;
}



/*!
  This is an optional function to properly close and release any resources
  that are not required beyond calibration needs.
  @remark the prototype of this function can be modified to suit ones need.
 */
void ELCALLTYPE close_expt_graphics()
{
	
}




/*!
	This is called to check for keyboard input. 
	In this function:
	\arg check if there are any input events
	\arg if there are input events, fill key_input and return 1.
		 otherwise return 0. If 1 is returned this will be called
	     again to check for more events.
	@param[out] key_input  fill in the InputEvent structure to return
		 key,modifier values.
	@return if there is a key, return 1 otherwise return 0.
*/

INT16 ELCALLBACK get_input_key(InputEvent *key_input)
{
	
	return 0;
}



/*!
	This function provides support to writing images to disk. Upon calls to el_bitmap_save_and_backdrop or
	el_bitmap_save this function is requested to do the write operaiton in the preferred format.

	@param[in] outfilename Name of the file to be saved.
	@param[in] format  format to be saved as.
	@param[in] bitmap bitmap data to be saved.
	@return if successful, return 0.
*/
int ELCALLBACK writeImage(char *outfilename, IMAGETYPE format, EYEBITMAP *bitmap)
{

	return 0;
}


