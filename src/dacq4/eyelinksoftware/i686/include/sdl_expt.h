/**********************************************************************************
 * EYELINK PORTABLE EXPT SUPPORT      (c) 1996, 2003 by SR Research               *
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

#ifndef __SRRESEARCH__SDL_EXPT_H__
#define __SRRESEARCH__SDL_EXPT_H__
#ifdef __SRRESEARCH__GDI_EXPT_H__
#error sdl_expt.h should not be used with gdi_expt.h
#endif

#include <SDL/SDL.h>
#include "eyelink.h"
#include "exptsppt.h"

#ifdef __cplusplus 	/* For C++ compilation */
extern "C" {
#endif


/**************************Convenient Macros *********************************/
#define	SDLRGB(x,y)   SDL_MapRGB(x->format,(y).r,(y).g,(y).b)
#define SCREEN_LEFT   dispinfo.left
#define SCREEN_TOP    dispinfo.top
#define SCREEN_RIGHT  dispinfo.right
#define SCREEN_BOTTOM dispinfo.bottom
#define SCRHEIGHT     dispinfo.height
#define SCRWIDTH      dispinfo.width


/*****************************************************************************
 * Function: set_calibration_colors
 * Parameters:
 *		fg: foreground color
 *		bg: background color
 * Purpose:
 *		To reset the calibration colors
 *****************************************************************************/
void  ELCALLTYPE  set_calibration_colors(SDL_Color *fg, SDL_Color* bg);

/*****************************************************************************
 * Function: set_target_size
 * Parameters:
 *		diameter: diameter of the target circle
 *		holesize: diamtere of the inner circle
 * Purpose:
 *		To reset the calibration target size
 *****************************************************************************/
void  ELCALLTYPE  set_target_size(UINT16 diameter, UINT16 holesize);

/*****************************************************************************
 * Function: set_cal_sounds
 * Parameters:
 *		ontarget: sound file to use on ontarget- use "off" to turn off 
 *		ongood: sound file to use on ongood- use "off" to turn off 
 *		onbad:	sound file to use on bad- use "off" to turn off 
 * Purpose:
 *		To reset the calibration sounds
 *****************************************************************************/
void  ELCALLTYPE  set_cal_sounds(char *ontarget, char *ongood, char *onbad);

/*****************************************************************************
 * Function: set_dcorr_sounds
 * Parameters:
 *		ontarget: sound file to use on ontarget- use "off" to turn off 
 *		ongood: sound file to use on ongood- use "off" to turn off 
 *		onbad:	sound file to use on bad- use "off" to turn off 
 * Purpose:
 *		To reset the drift correct sounds
 *****************************************************************************/
void  ELCALLTYPE  set_dcorr_sounds(char *ontarget, char *ongood, char *onbad);


/*****************************************************************************
 * Function: set_camera_image_position
 * Parameters:
 *		left: left position 
 *		top:  top position
 *		right:right position
 *		bottom: bottom position
 * Purpose:
 *		To adjust camera image position. By default the camera is placed 
 *		at the centre of the screen
 *****************************************************************************/
INT16 ELCALLTYPE  set_camera_image_position(INT16 left, INT16 top, 
										  INT16 right, INT16 bottom);


/*****************************************************************************
 * Function: get_display_information
 * Parameters:
 *		di: memory location pointer to fillin.
 * Purpose:
 *		Function returns display information.
 *****************************************************************************/
void  ELCALLTYPE  get_display_information(DISPLAYINFO *di);

/*****************************************************************************
 * Function: init_expt_graphics
 * Parameters:
 *		hwnd: window handle to the full screen. If this null, 
 *			the surface is created.
 *		info: display info
 * Purpose:
 *		function to initialize the expt graphics
 *****************************************************************************/
INT16 ELCALLTYPE  init_expt_graphics(SDL_Surface * hwnd, DISPLAYINFO *info);

/*****************************************************************************
 * Function: close_expt_graphics
 * Parameters:
 *		none
 * Purpose:
 *		function to close the expt graphics
 *****************************************************************************/
void  ELCALLTYPE  close_expt_graphics(void);


/*****************************************************************************
 * Function: gdi_bitmap_core
 * Parameters:
 *	hbm:		Bitmap to save or transfer or both
 *  xs:			x position 
 *	ys:			y position
 *	w:			width
 *	h:			height
 *	fname:		file name to save as
 *	path:		path to save
 *	sv_options: save options
 *	xd:			x positon
 *	yd:			y positon
 *	xferoptions:transfer options
 * Purpose:
 *		function to save or send image to tracker or both
 *****************************************************************************/
INT16 ELCALLTYPE sdl_bitmap_core(SDL_Surface *  hbm, INT16 xs, INT16 ys, 
								 INT16 w, INT16 h,
		       char *path, char *fname,  INT16 sv_options,
		       INT16 xd, INT16 yd, UINT16 xferoptions);



/* convenient and compatibility macros*/
#define bitmap_core(a,b,c,d,e,f,g,h,i,j,k) sdl_bitmap_core(a,b,c,d,e,f,h,i,j,k)
#define bitmap_save_and_backdrop(a,b,c,d,e,f,g,h,i,j,k) \
										sdl_bitmap_core(a,b,c,d,e,f,\
		g,h? h:SV_NOREPLACE|SV_MAKEPATH ,i,j,k|BX_DOTRANSFER)
#define bitmap_to_backdrop(a,b,c,d,e,f,g,i)  sdl_bitmap_core(a,b,c,d,e,NULL,\
		NULL,0,f,g,i|BX_DOTRANSFER)
#define gdi_bitmap_save(a,b,c,d,e,f,g)     sdl_bitmap_core(a,b,c,d,e,f,g? g:SV_NOREPLACE|SV_MAKEPATH,0,0,0)

/*
	Some video cards blocks the second flip if there is already one flip is 
	scheduled, eg.  most nvidia cards.  However, some video cards do not do this.  
	That is, if they cannot schedule a flip, they return an error. eg. most ATI cards.
	This flip macro checks whether the flip is not scheduled, if it is not scheduled,
	try till a flip can be scheduled. 
*/
#ifdef WIN32
#define Flip(x) while(SDL_FlipEx(x)<0)
#else
#define Flip(x) while(SDL_Flip(x)<0)
#endif

#ifdef __cplusplus 	/* For C++ compilation */
};
#endif
#endif
