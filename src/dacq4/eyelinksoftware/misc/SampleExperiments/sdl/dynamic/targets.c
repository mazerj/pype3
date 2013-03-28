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



#include "dynamic.h"
#ifdef MACOSX
#include <SDL_gfx/SDL_gfxPrimitives.h>
#else
#include <SDL/SDL_gfxPrimitives.h>
#endif

/************** CREATE TARGET BITMAPS *************/

#undef NTARGETS
#undef NSHAPES

/*
	NOTES: targets are bitmaps copied to screen directly
	they are erased by restoring background saved before drawing
*/

#define NSHAPES 4   /* up to 4 patterns (0..3), target 0 is invisible */

typedef struct {
       SDL_Surface *bitmap;  /* bitmap */
       int h, w;        /* height and width */
       int xo, yo;      /* offset of top-left from plot position */
  } SHAPE;

SHAPE shapes[NSHAPES];


#define NTARGETS 2   /* up to 2 targets for saccadic tasks */

typedef struct {
       int shape;   /* which bitmap */
       int drawn;   /* is is drawn? */
       int x, y;  /* top-left motion detect */
  } TARGET;

TARGET targets[NTARGETS];





/*
	Create the target patterns
	Targets: 0=none (used to clear), 1=0.5 degree disk, 2=\, 3=/
	redfine as eeded for your targets
*/
int create_shape(int n, SDL_Color fgcolor, SDL_Color bgcolor)
{
	SDL_Surface *hbm = NULL;
	int width  = (int )((SCRWIDTH/30.0)*0.5);   /* all targets are 0.5 by 0.5 degrees */
	int height = (int)((SCRHEIGHT/22.5)*0.5);

  shapes[n].w = width;      /* initialize shape data */
  shapes[n].h = height;
  shapes[n].xo = width/2;
  shapes[n].yo = height/2;

  /* create target bitmap */
#ifndef MACOSX /* no hwsurface in mac */
  hbm = SDL_CreateRGBSurface(SDL_HWSURFACE,width, height, dispinfo.bits,0,0,0,0);  /*  create bitmap */
#else
  hbm = SDL_CreateRGBSurface(SDL_SWSURFACE,width, height, dispinfo.bits,0,0,0,0);  /*  create bitmap */
#endif
  if(!hbm)
    {
      return -1;
    }
  shapes[n].bitmap = hbm;

  /* clear bitmap background */
  SDL_FillRect(hbm,NULL,SDL_MapRGB(hbm->format,bgcolor.r,  bgcolor.g, bgcolor.b));
  switch(n)                     /* draw the target bitmap */
    {
      case 0:       /* invisible target */
      default:
        break;
      case 1:       /* filled circle */
		  /* draw filled ellipse */
        filledCircleRGBA(hbm, (Sint16) (width/2), (Sint16)(height/2),
					(Sint16)(min(width/2, height/2)-1), fgcolor.r,fgcolor.g,fgcolor.b,255);
        break;
      case 2:        /* "\" line */
		aalineRGBA(hbm,0,2,(Sint16)(width-2),(Sint16)height,fgcolor.r,fgcolor.g,fgcolor.b,255);
		aalineRGBA(hbm,0,1,(Sint16)(width-1),(Sint16)height,fgcolor.r,fgcolor.g,fgcolor.b,255);
		aalineRGBA(hbm,0,0,(Sint16)width,(Sint16)height,fgcolor.r,fgcolor.g,fgcolor.b,255);
		aalineRGBA(hbm,1,0,(Sint16)width,(Sint16)(height-1),fgcolor.r,fgcolor.g,fgcolor.b,255);
		aalineRGBA(hbm,2,0,(Sint16)width,(Sint16)(height-2),fgcolor.r,fgcolor.g,fgcolor.b,255);

        break;
      case 3:        /* "/" line */
		aalineRGBA(hbm,0,(Sint16)(height-2),(Sint16)(width-2),0,fgcolor.r,fgcolor.g,fgcolor.b,255);
		aalineRGBA(hbm,0,(Sint16)(height-1),(Sint16)(width-1),0,fgcolor.r,fgcolor.g,fgcolor.b,255);

		aalineRGBA(hbm,0,(Sint16)height,(Sint16)width,0,fgcolor.r,fgcolor.g,fgcolor.b,255);

		aalineRGBA(hbm,1,(Sint16)height,(Sint16)width,1,fgcolor.r,fgcolor.g,fgcolor.b,255);
		aalineRGBA(hbm,2,(Sint16)height,(Sint16)width,2,fgcolor.r,fgcolor.g,fgcolor.b,255);
        break;
    }
  return 0;
}


/*
	Create the target patterns
	set all targets as not drawn, pattern 0
	redefine as eeded for your targets
*/
int initialize_targets(SDL_Color fgcolor, SDL_Color bgcolor)
{
  int i;

  for(i=0;i<NSHAPES;i++)      /* mark targets as uninitialized */
    shapes[i].bitmap = NULL;
  for(i=0;i<NSHAPES;i++)   /* create 0.5 degree targets */
    create_shape(i, fgcolor, bgcolor);

  for(i=0;i<NTARGETS;i++)  /* initialize targets to invisible */
    {
	   targets[i].x = targets[i].y = -1;
       targets[i].drawn = 0;
       targets[i].shape = 0;
    }
  return 0;
}


/* clean up targets after trial */
void free_targets(void)
{
  int i;

  for(i=0;i<NSHAPES;i++)
    if(shapes[i].bitmap)
      {
        SDL_FreeSurface(shapes[i].bitmap);
        shapes[i].bitmap = NULL;
      }
}


/************** TARGET DRAW/ERASE/MOVE **************/


/*
	 draw target n, centered at x, y, using shape
	 will only draw if target is erased
*/
void draw_target(int n, int x, int y, int shape)
{
#ifndef MACOSX
	static  int oldx[NTARGETS] = {-1,-1};
	static  int oldy[NTARGETS] = {-1,-1};
	static  int oldshape[NTARGETS] = {-1,-1};
#endif
  if(shapes[n].bitmap == NULL) return;  /* check if valid shape */




  if(shape != 0)    /* shape 0 = not visible */
  {
	SDL_Rect dest = {x-shapes[shape].xo, y-shapes[shape].yo, shapes[shape].w,shapes[shape].h};
	SDL_BlitSurface(shapes[shape].bitmap,NULL,window,&dest);/* copy shape to dispaly  */
	targets[n].drawn = 1;         /* mark as drawn */
#ifndef MACOSX
	targets[n].shape = oldshape[n];     /* record drawing information */
	targets[n].x = oldx[n];
	targets[n].y = oldy[n];

	oldx[n] =x;
	oldy[n] = y;
	oldshape[n] = shape;
#else
	targets[n].shape = shape;     /* record drawing information */
	targets[n].x = x;
        targets[n].y = y;
#endif
  }
}

/*
	erase target by copying back background bitmap
	will only erase if target is drawn
*/
void erase_target(int n)
{
  SDL_Rect dest;
  if(targets[n].drawn == 0) return;  /* check if drawn */
  if(targets[n].x == -1 && targets[n].y == -1)
	  return;
  targets[n].drawn = 0;              /* mark as erased */

  dest.x = targets[n].x-shapes[targets[n].shape].xo;
  dest.y = targets[n].y-shapes[targets[n].shape].yo;
  dest.w = shapes[targets[n].shape].w;
  dest.h = shapes[targets[n].shape].h;

  SDL_FillRect(window,&dest,SDL_MapRGB(window->format, target_background_color.r,target_background_color.g,target_background_color.b));
}


/*
	call after screen erased so targets know they're not visible
	this will permit them to be redrawn
*/
void target_reset(void)
{
  int i;

  for(i=0;i<NTARGETS;i++)
    targets[i].drawn = 0;
}


/*
	handles moving target, changing shape
	target will be hidden it if shape = 0
*/
void move_target(int n, int x, int y, int shape)
{
	if(shape ==0)
	{
		targets[n].drawn = 1;
		erase_target(n);              /* erase old target */
	}
	else
#ifdef MACOSX /*no flipping supported in mac. */
		if(targets[n].drawn ==0 || targets[n].x != x || targets[n].y != y)
#endif

    {
		erase_target(n);              /* erase old target */
        draw_target(n, x, y, shape);  /* draw with new information */
    }

}


