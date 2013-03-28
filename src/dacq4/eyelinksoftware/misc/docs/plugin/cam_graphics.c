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


/*!
In this file, we perform all camera setup features.  
*/

#include "eyelink.h"
#include "graphics_global.h"

/*!
	This function is responsible for initializing any resources that are 
	required for camera setup.
	
	@param width width of the source image to expect.
	@param height height of the source image to expect.
	@return -1 if failed,  0 otherwise.
 */
INT16 ELCALLBACK setup_image_display(INT16 width, INT16 height)
{
  return 0;
}


/*!
	This is called to notify that all camera setup things are complete.  Any
	resources that are allocated in setup_image_display can be released in this
	function.
*/
void ELCALLBACK exit_image_display(void)
{

}


/*!
  This function is called to update any image title change.
  @param threshold if -1 the entire tile is in the title string
				   otherwise, the threshold of the current image.
  @param title     if threshold is -1, the title contains the whole title 
				   for the image. Otherwise only the camera name is given.
 */
void ELCALLBACK image_title(INT16 threshold, char *title)
{
	
}



/*!
	This function is called after setup_image_display and before the first call to 
	draw_image_line. This is responsible to setup the palettes to display the camera
	image.

    @param ncolors number of colors in the palette.
	@param r       red component of rgb.
	@param g       blue component of rgb.
	@param b       green component of rgb.

    

*/
void ELCALLBACK set_image_palette(INT16 ncolors, byte r[130], byte g[130], byte b[130])
{

}


/*!
	This function is called to supply the image line by line from top to bottom.
	@param width  width of the picture. Essentially, number of bytes in \c pixels.
	@param line   current line of the image
	@param totlines total number of lines in the image. This will always equal the height of the image.
	@param pixels pixel data.

    Eg. Say we want to extract pixel at position (20,20) and print it out as rgb values.  

	@code
    if(line == 19) // y = 20
	{
		byte pix = pixels[19];
		// Note the r,g,b arrays come from the call to set_image_palette
		printf("RGB %d %d %d\n",r[pix],g[pix],b[pix]); 
	}
	@endcode

	@remark certain display draw the image up side down. eg. GDI.
*/
void ELCALLBACK draw_image_line(INT16 width, INT16 line, INT16 totlines, byte *pixels)
{

}


