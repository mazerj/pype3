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



#ifndef  __COMM_SAMPLE__H__
#define  __COMM_SAMPLE__H__
#ifdef MACOSX
#include <eyelink_core_graphics/sdl_expt.h>
#else
#include <sdl_expt.h>
#endif

/* function declarations */
void clear_full_screen_window(SDL_Color c);
int simple_recording_trial(char *text, UINT32 time_limit);
int run_trials(void);;


/*global variable externs */
extern DISPLAYINFO dispinfo;
extern SDL_Surface *window;
extern SDL_Color target_foreground_color;
extern SDL_Color target_background_color;


/* convenient macros */
#define SETCOLOR(x,red,green,blue) x.r =red; x.g = green; x.b =blue; 

/* porting macros */
#ifndef WIN32
#define _stricmp strcasecmp
#endif
#endif

