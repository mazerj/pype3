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
\file cal_graphics.c
\brief Example implementation of calibration graphics using SDL graphics envoronment

In this file, we perform all calibration displays.
@defgroup cal_example all functions related to calibration presentation for SDL Core Graphics Example

*/

#include "eyelink.h"
#include "graphics_global.h"


#define TARGET_SIZE 20 /*!< @ingroup cal_example Target size in pixels.*/
/*!
	@ingroup cal_example
	Setup the calibration display. This function called before any
	calibration routines are called.
*/
INT16  ELCALLBACK  setup_cal_display(void)
{
	/* If you would like to use custom targets, you might want to initialize here
	   and release it in exit_cal_display. For our demonstration, we are going to use
	   rectangle targets, that can easily be drawn on the display.

	   So, nothing to do here.
	*/
  return 0;
}


/*!
  @ingroup cal_example
  This is called to release any resources that are not required beyond calibration.
  Beyond this call, no calibration functions will be called.
 */
void ELCALLBACK exit_cal_display(void)
{
	/*
	Since we did nothing in setup_cal_display, we don't have much here either.
	*/
}

/*!
  @ingroup cal_example
  This function is responsible for the drawing of the target for calibration,validation
  and drift correct at the given coordinate.
  @param x x coordinate of the target.
  @param y y coordinate of the target.
  @remark The x and y are relative to what is sent to the tracker for the
  		  command screen_pixel_coords.
 */
void ELCALLBACK  draw_cal_target(INT16 x, INT16 y)
{
	SDL_Rect r = {x,y,TARGET_SIZE,TARGET_SIZE};
	SDL_FillRect(mainWindow,&r,0); // draw the rectangle
	SDL_UpdateRect(mainWindow,0,0,0,0); //update the entire window
}

/*!
	@ingroup cal_example
	This function is responsible for erasing the target that was drawn by the
	last call to draw_cal_target.
*/
void ELCALLBACK erase_cal_target(void)
{
	/*
	Technically, we should keep the last drawn x,y position and erace only the
	piece that we drawn in the last call to draw_cal_target. For simplicity reasons,
	we will clear the entire the screen
	*/
	clear_cal_display();
}


/*!
	@ingroup cal_example
  Called to clear the calibration display.
 */
void ELCALLBACK clear_cal_display(void)
{
	// clear the window
  	SDL_FillRect(mainWindow,NULL,SDL_MapRGB(mainWindow->format,192,192,192));
	SDL_UpdateRect(mainWindow,0,0,0,0); //update the entire window
}



#define CAL_TARG_BEEP   1 /*!< @ingroup cal_example Calibration target beep*/
#define CAL_GOOD_BEEP   0 /*!< @ingroup cal_example Calibration good beep*/
#define CAL_ERR_BEEP   -1 /*!< @ingroup cal_example Calibration error beep*/
#define DC_TARG_BEEP    3 /*!< @ingroup cal_example Drift correct target beep*/
#define DC_GOOD_BEEP    2 /*!< @ingroup cal_example Drift correct good beep*/
#define DC_ERR_BEEP    -2 /*!< @ingroup cal_example Drift correct error beep*/
/*!
	@ingroup cal_example
	In most cases on can implement all four (cal_target_beep,
	cal_done_beep,dc_target_beep,dc_done_beep) beep callbacks
	using just one function.

	This function is responsible for selecting and playing the audio clip.
	@param sound sound id to play.
*/
void ELCALLBACK  cal_sound(INT16 sound)
{
  char *wave =NULL;
  switch(sound) // select the appropriate sound to play
  {
    case CAL_TARG_BEEP: /* play cal target beep */
		wave ="type.wav";
    	break;
    case CAL_GOOD_BEEP: /* play cal good beep */
		wave ="qbeep.wav";
        break;
    case CAL_ERR_BEEP:  /* play cal error beep */
		wave ="error.wav";
        break;
    case DC_TARG_BEEP:  /* play drift correct target beep */
		wave ="type.wav";
       	break;
    case DC_GOOD_BEEP:  /* play drift correct good beep */
		wave ="qbeep.wav";
      	break;
    case DC_ERR_BEEP:  /* play drift correct error beep */
		wave ="error.wav";
      	break;
  }
  if(wave)
  {
	  PlaySound(wave,NULL,SND_FILENAME);
  }
}

/*!
@ingroup cal_example
 This function is called to signal new target.
 */
void ELCALLBACK cal_target_beep(void)
{
	cal_sound(CAL_TARG_BEEP);
}

/*!
@ingroup cal_example
  This function is called to signal end of calibration.
  @param error if non zero, then the calibration has error.
 */
void ELCALLBACK cal_done_beep(INT16 error)
{
if(error)
    {
      cal_sound(CAL_ERR_BEEP);
    }
  else
    {
      cal_sound(CAL_GOOD_BEEP);
    }
}

/*!
@ingroup cal_example
  This function is called to signal a new drift correct target.
 */
void ELCALLBACK dc_target_beep(void)
{
	cal_sound(DC_TARG_BEEP);
}

/*!
@ingroup cal_example
  This function is called to singnal the end of drift correct.
  @param error if non zero, then the drift correction failed.
 */
void ELCALLBACK dc_done_beep(INT16 error)
{
 if(error)
    {
      cal_sound(DC_ERR_BEEP);
    }
  else
    {
      cal_sound(DC_GOOD_BEEP);
    }
}




