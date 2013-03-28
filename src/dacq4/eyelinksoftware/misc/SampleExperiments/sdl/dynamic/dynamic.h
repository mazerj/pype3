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

#ifndef __SR_RESEARCH__DYNAMIC_H__
#define __SR_RESEARCH__DYNAMIC_H__
#ifdef MACOSX
#include <eyelink_core_graphics/sdl_expt.h>
#else
#include <sdl_expt.h>
#endif

#ifndef WIN32
#define min(x, y) (x>y)? y:x
#define __cdecl 
#define _stricmp strcasecmp
#endif

extern DISPLAYINFO dispinfo;  /* display information: size, colors, refresh rate*/
extern SDL_Surface *window;   /* SDL surface for drawing */
extern SDL_Color target_background_color;   /* SDL color for the background */
extern SDL_Color target_foreground_color;   /* SDL color for the foreground drawing (text, calibration target, etc)*/



int run_trials(void);   /* This code sequences trials within a block. */
void clear_full_screen_window(SDL_Color c);  /* Clear the window with a specific color */

void target_reset(void);
int initialize_targets(SDL_Color fgcolor, SDL_Color bgcolor);
void move_target(int n, int x, int y, int shape);
void free_targets(void);

/* Runs a single dynamic trial */ 
int run_dynamic_trial(SDL_Surface* hbm, UINT32 time_limit, 
                      int ( * drawfn)(UINT32 t, UINT32 dt, int *x, int *y));

/* convenient macros */
#define SETCOLOR(x,red,green,blue) x.r =red; x.g = green; x.b =blue; 

#endif

