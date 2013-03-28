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


/*!\file
\brief Example implementation of camera image graphics using SDL graphics envoronment

In this file, we perform all camera setup features.
@defgroup cam_example all camera display related functions for SDL Core Graphics Example

*/



#include "graphics_global.h"


//draws a line from (x1,y1) to (x2,y2) - required for all tracker versions.
void drawLine(CrossHairInfo *chi, int x1, int y1, int x2, int y2, int cindex);

//draws shap that has semi-circle on either side and connected by lines.
//Bounded by x,y,width,height. x,y may be negative.
//This only needed for EL1000.
void drawLozenge(CrossHairInfo *chi, int x, int y, int width, int height, int cindex);

//Returns the current mouse position and its state. only neede for EL1000.
void getMouseState(CrossHairInfo *chi, int *rx, int *ry, int *rstate);


static UINT32 image_palmap32[130+2];
static SDL_Surface *image = NULL;
/*!
	@ingroup cam_example
	This function is responsible for initializing any resources that are
	required for camera setup.

	@param width width of the source image to expect.
	@param height height of the source image to expect.
	@return -1 if failed,  0 otherwise.
 */
INT16 ELCALLBACK setup_image_display(INT16 width, INT16 height)
{
  image = SDL_CreateRGBSurface(SDL_SWSURFACE,width,height,32,0,0,0,0);
  return 0;
}


/*!
	@ingroup cam_example
	This is called to notify that all camera setup things are complete.  Any
	resources that are allocated in setup_image_display can be released in this
	function.
*/
void ELCALLBACK exit_image_display(void)
{
	if(image)  // release the image surface that we created in setup_image_display
	{
		SDL_FreeSurface(image);
		image = NULL;
	}
}


/*!
  @ingroup cam_example
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
	@ingroup cam_example
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
	int i =0;
	for(i=0;i<ncolors;i++)
    {
      UINT32 rf = r[i];
      UINT32 gf = g[i];
      UINT32 bf = b[i];
      image_palmap32[i] = (rf<<16) | (gf<<8) | (bf); // we will have an rgba palette setup.
    }
}


/*!
	@ingroup cam_example
	This function is called to supply the image line by line from top to bottom.
	@param width  width of the picture. Essentially, number of bytes in \c pixels.
	@param line   current line of the image
	@param totlines total number of lines in the image. This will always equal
					the height of the image.
	@param pixels pixel data.

    Eg. Say we want to extract pixel at position (20,20) and print it out as rgb values.

	@code
    if(line == 20) // y = 20
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

  short i;
  UINT32 *v0;
  byte *p = pixels;


  v0 = (UINT32 *)(((byte*)image->pixels) + ((line-1)*(image->pitch)));
  for(i=0; i<width; i++)
  {
     *v0++ = image_palmap32[*p++]; // copy the line to image
  }
  if(line == totlines)
  { // at this point we have a complete camera image. This may be very small.
	// we might want to enlarge it. For simplicity reasons, we will skip that.

	// center the camera image on the screen
	SDL_Rect r = {(mainWindow->w-image->w)/2,(mainWindow->h-image->h)/2,0,0};


	// now we need to draw the cursors.

	CrossHairInfo crossHairInfo;
	memset(&crossHairInfo,0,sizeof(crossHairInfo));

	crossHairInfo.w = image->w;
	crossHairInfo.h = image->h;
	crossHairInfo.drawLozenge = drawLozenge;
	crossHairInfo.drawLine = drawLine;
	crossHairInfo.getMouseState = getMouseState;
	crossHairInfo.userdata = image;

	eyelink_draw_cross_hair(&crossHairInfo);

	SDL_BlitSurface(image,NULL,mainWindow,&r);

  }
}


/*!
	@ingroup cam_example
	draws a line from (x1,y1) to (x2,y2) - required for all tracker versions.
*/
void drawLine(CrossHairInfo *chi, int x1, int y1, int x2, int y2, int cindex)
{
  //One can use SDL_gfx to implement this. For ELI and ELII this will always be
  //horizontal and vertical lines.
  //Note, because of rounding, you may get x,y values just off by 1 pixel.
   SDL_Rect r;
   UINT32 color =0;
   SDL_Surface *img = (SDL_Surface *)(chi->userdata);
   switch(cindex)
	{
		case CR_HAIR_COLOR:
		case PUPIL_HAIR_COLOR:
			color = SDL_MapRGB(img->format,255,255,255); break;
		case PUPIL_BOX_COLOR:
			color = SDL_MapRGB(img->format,0,255,0); break;
		case SEARCH_LIMIT_BOX_COLOR:
		case MOUSE_CURSOR_COLOR:
			color = SDL_MapRGB(img->format,255,0,0); break;
	}
  if(x1 == x2) // vertical line
  {
	  if(y1 < y2)
	  {
		  r.x = x1;
		  r.y = y1;
		  r.w = 1;
		  r.h = y2-y1;
	  }
	  else
	  {
		  r.x = x2;
		  r.y = y2;
		  r.w = 1;
		  r.h = y1-y2;
	  }
	  SDL_FillRect(img,&r,color);
  }
  else if(y1 == y2) // horizontal line.
  {
	  if(x1 < x2)
	  {
		  r.x = x1;
		  r.y = y1;
		  r.w = x2-x1;
		  r.h = 1;
	  }
	  else
	  {
		  r.x = x2;
		  r.y = y2;
		  r.w = x1-x2;
		  r.h = 1;
	  }
	  SDL_FillRect(img,&r,color);
  }
  else
  {
	printf("non horizontal/vertical lines not implemented. \n");
  }
}

/*!
	@ingroup cam_example
	draws shap that has semi-circle on either side and connected by lines.
	Bounded by x,y,width,height. x,y may be negative.
	@remark This is only needed for EL1000.	
*/
void drawLozenge(CrossHairInfo *chi, int x, int y, int width, int height, int cindex)
{
	// NOT IMPLEMENTED.
	printf("drawLozenge not implemented. \n");
}

/*!
	@ingroup cam_example
	Returns the current mouse position and its state.
	@remark This is only needed for EL1000.	
*/

void getMouseState(CrossHairInfo *chi, int *rx, int *ry, int *rstate)
{
  int x =0;
  int y =0;
  Uint8 state =SDL_GetMouseState(&x,&y);
  x = x-(mainWindow->w - ((SDL_Surface*)chi->userdata)->w)/2;
  y = y-(mainWindow->h - ((SDL_Surface*)chi->userdata)->h)/2;
  if(x>=0 && y >=0 && x <=((SDL_Surface*)chi->userdata)->w && y <= ((SDL_Surface*)chi->userdata)->h)
  {
    *rx = x;
	*ry = y;
	*rstate = state;
  }
}