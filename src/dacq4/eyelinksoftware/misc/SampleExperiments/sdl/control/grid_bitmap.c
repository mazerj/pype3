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
 

#include "control.h"
#include <sdl_text_support.h>


/*********** DRAW GRID OF LETTERS ************/

                          /* 5 colors used to draw the grid of letters */
SDL_Color lettercolor[5] = { 
	{ 0xFF, 0xFF, 0x60 },
	{ 0x60, 0xcF, 0xFF },
	{ 0xFF, 0x00, 0xFF },  
	{ 0x00, 0xFF, 0x40 },  
	{ 0xFF, 0xFF, 0xFF } };

/* Draws a grid of letters to a DDB bitmap                
This can be rapidly copied to the display
Also draw boxes to the EyeLink tracker display for feedback
Returns: Handle of bitmap 
*/
SDL_Surface * draw_grid_to_bitmap(void)
{
  short i, j, x, y;
  char b[2] = "A";  /* The character */
  SDL_Surface *hbm = NULL;
  SDL_Rect r = {0,0,0,0};


  hbm = SDL_CreateRGBSurface(SDL_SWSURFACE,SCRWIDTH,SCRHEIGHT,dispinfo.bits,0,0,0,0);
  eyecmd_printf("clear_screen 0");     /* clear eye tracker display */
                  
  /* SET UP TEXT FOR DRAWING */
  get_new_font("Arial Bold", SCRWIDTH/25, 0);   /* set up the font */
  x = SCRWIDTH/5;          /* set grid spacing */
  y = SCRHEIGHT/5;
  for(j=y/2;j<5*y;j+=y)    /* step through 5x5 grid of a-y */
    for(i=x/2;i<5*x;i+=x)   
      {
        r.y = j - (SCRHEIGHT/36);        /* Rectangle centered on character */
        r.h = r.y + (SCRHEIGHT/18);
        r.x = i - (SCRWIDTH/50);
        r.w = r.x + (SCRWIDTH/25);
		graphic_printf(hbm,lettercolor[(i/x+j/y)%5],NONE, r.x, r.y,b);
        b[0]++;                                          /* Next letter */
		
		eyecmd_printf("draw_box %d %d %d %d 15",         /* Reference box on EyeLink tracker display */
                       r.x, r.y, r.w, r.h);
       }
  return hbm;                                            /* Return handle to new bitmap */
}

       /* Draws a grid of letters to a DDB bitmap */               
       /* This can be rapidly copied to the display */
       /* Also draw boxes to the EyeLink tracker display for feedback */
       /* Returns: Handle of bitmap */
SDL_Surface * draw_grid_to_bitmap_segment(char *filename, char*path, int dotrack)
{
  short i, j, x, y, count=1;
  char b[2] = "A";  /* The character */
  SDL_Rect r = {0,0,0,0};           /* RECT to draw character in */
  FILE *seg_file; 
  char com_fname[100];
  SDL_Surface *hbm = NULL;

  create_path(path, 1, 1);			/* Create path if it does not exist */
  splice_fname(filename, path, com_fname);   /* Splice 'path' to 'fname', store in 'com_fname' */

  seg_file = fopen(com_fname, "wt");		/* open segmentation file; overwrites if previous such file exists */
  if(!seg_file) 
	eyemsg_printf("Error in opening the file to record segments");

  /* CREATE THE BITMAP */
  hbm = SDL_CreateRGBSurface(SDL_SWSURFACE,SCRWIDTH,SCRHEIGHT,dispinfo.bits,0,0,0,0);
                     
  get_new_font("Arial Bold", SCRWIDTH/25, 0);   /* set up the font */

  x = SCRWIDTH/5;          /* set grid spacing */
  y = SCRHEIGHT/5;
  for(j=y/2;j<5*y;j+=y)    /* step through 5x5 grid of a-y */
    for(i=x/2;i<5*x;i+=x)   
      {
        r.y = j - (SCRHEIGHT/36);                      /* Rectangle centered on character */ 
        r.h = r.y + (SCRHEIGHT/18);
        r.x = i - (SCRWIDTH/50);
        r.w = r.x + (SCRWIDTH/25);
		graphic_printf(hbm,lettercolor[(i/x+j/y)%5],NONE, r.x, r.y,b);
		if (dotrack)									 /* Reference box on EyeLink tracker display */
			eyecmd_printf("draw_box %d %d %d %d 15",        
                       r.x, r.y, r.w, r.h);
      
		fprintf(seg_file, "TEXT\t%d\t%d\t%d\t%d\t%d\t%s\n",
			count, (count-1)%5*SCRWIDTH/5, (count-1)/5*SCRHEIGHT/5, 
			((count-1)%5+1)*SCRWIDTH/5, ((count-1)/5+1)*SCRHEIGHT/5, b);  
					/* write to the segmentation file; */
        
		b[0]++;  
		count ++; /* Next letter */
	
	}
  fclose(seg_file);
  return hbm;                                      /* Return handle to new bitmap */
}

