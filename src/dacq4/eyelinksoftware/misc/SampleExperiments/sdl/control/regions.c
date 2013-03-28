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


REGION rgn[NREGIONS];
int last_region = -1;	  /* region with gaze at last update */
int current_region = -1;  /* region currently accumulating gaze time */
long dwell_threshold = 700;	/* msec of gaze in region required to trigger */



void invert_rect(SDL_Rect *rect, int highlight, int region) 
{     
	
	if(highlight)
	{
		char b[2] = "A";
		get_new_font("Arial Bold", SCRWIDTH/25, 0);
		b[0] += (region%26);
		SDL_FillRect(window,rect,SDL_MapRGB(window->format,192,192,192));
		graphic_printf(window,lettercolor[(region/5 + region%5)%5],NONE, rect->x+(SCRWIDTH/100), rect->y+(SCRHEIGHT/72),b);
		Flip(window);
		SDL_FillRect(window,rect,SDL_MapRGB(window->format,192,192,192));
		graphic_printf(window,lettercolor[(region/5 + region%5)%5],NONE, rect->x+(SCRWIDTH/100), rect->y+(SCRHEIGHT/72),b);
	}
	else
	{
		SDL_BlitSurface(segment_source, rect, window, rect);
		Flip(window);
		SDL_BlitSurface(segment_source, rect, window, rect);
	}
}

void trigger_region(int region)
{
  int i;
  
  for(i=0;i<NREGIONS;i++)   /* scan thru all regions */
    {
      if(i==region)	    /* is this the new region? */
        {
          if(rgn[i].triggered==0)       /* highlight new region */
            invert_rect(&(rgn[i].rdraw), 1, i);
          rgn[i].triggered = 1;  
        }
      else  		
        {
          if(rgn[i].triggered)		/* unhighlight old region */
            invert_rect(&(rgn[i].rdraw), 0, i);
          rgn[i].triggered = 0;  
        }
    }    
} 			


           /* Clear region data when gaze switches to new region	 */
void reset_regions(void)
{
  int i;
  
  for(i=0;i<NREGIONS;i++)   /* reset data for all regions */
    {
      rgn[i].avgxsum = 0;   
      rgn[i].avgysum = 0;
      rgn[i].dwell = 0;
    }
  current_region = -1;      /* no region currently selected */
  last_region = -1;
} 			

void SDL_SetRect(SDL_Rect *rect, int x, int y, int w, int h)
{
	rect->x = x-w;
	rect->y = y-h;
	rect->w = w+w;
	rect->h = h+h;
}
int SDL_PointInRect(SDL_Rect *rect, int x, int y)
{
	if(x >= rect->x  && x <=(rect->x +rect->w)   && y>= rect->y &&  y <= (rect->y + rect->h) )
		return 1;
	return 0;
}
	    /* Initial setup of region data */
void init_regions(void)
{
  int i;
  int x,y;
  
  for(i=0;i<NREGIONS;i++)   /* For all regions: */
    {
      x = (i%5) * (SCRWIDTH / 5) + (SCRWIDTH / 10);    /* compute center of region */
      y = (i/5) * (SCRHEIGHT / 5) + (SCRHEIGHT / 10);
      rgn[i].cx = x;                                   /* record center for drift correction */
      rgn[i].cy = y;
      SDL_SetRect(&(rgn[i].rdraw), x,y,SCRWIDTH/30,SCRHEIGHT/22);
      SDL_SetRect(&(rgn[i].rsense), x,y,SCRWIDTH/10,SCRHEIGHT/10);
    }
} 	


	/* Determine which region gaze is in
	   return 0-24 for a valid region, -1 if not in any region */
int which_region(int x, int y)
{
  int i;
  for(i=0;i<NREGIONS;i++)      /* scan all regions for gaze position match */
    if(SDL_PointInRect(&(rgn[i].rsense), x,y)) return i;
  
  return -1;                   /* not in any region */
}

	/*	
		Process a fixation-update event:
		Detect and handle a switch between regions
		Otherwise, accumulate time and position in region
		Trigger region when time exceeds threshold 
	*/
void process_fixupdate(int x, int y, long dur)
{
   int avgx, avgy;
   int i = which_region(x, y);     /* which region is gaze in */
   
   if(i == -1)		    /* NOT IN ANY REGION: */
     {                          /* allow one update outside of a region before resetting */
       if(last_region == -1)	/* 2 in a row: reset all regions*/
         {
           reset_regions();
         }
     }
   else if(i == current_region)	   /* STILL IN CURRENT REGION  */
     {
       rgn[i].dwell += dur;	      /* accumulate time, position */
       rgn[i].avgxsum += dur * x;
       rgn[i].avgysum += dur * y;
       if(rgn[i].dwell>dwell_threshold && !rgn[i].triggered)  /* did this region trigger yet? */
         {
           trigger_region(i);		        /* TRIGGERED: */
           avgx = rgn[i].avgxsum / rgn[i].dwell;    /* compute avg. gaze position */
           avgy = rgn[i].avgysum / rgn[i].dwell;
                  	                        /* correct for drift (may cause false saccade in data) */
           eyecmd_printf("drift_correction %ld %ld %ld %ld",
                          (long)rgn[i].cx-avgx, (long)rgn[i].cy-avgy,
                          (long)rgn[i].cx, (long)rgn[i].cy); 
	  						/* Log triggering to EDF file */
           eyemsg_printf("TRIGGER %d %ld %ld %ld %ld %ld", 
                          i, avgx, avgy, rgn[i].cx, rgn[i].cy, rgn[i].dwell);
         } 
     }
   else if(i == last_region)	/* TWO UPDATES OUTSIDE OF CURRENT REGION: SWITCH TO NEW REGION */
     {
       reset_regions();              /* clear and initialize accumulators */
       rgn[i].dwell = dur;	      
       rgn[i].avgxsum = dur * x;
       rgn[i].avgysum = dur * y;
       current_region = i;           /* now working with new region */
     }
  last_region = i;
}		