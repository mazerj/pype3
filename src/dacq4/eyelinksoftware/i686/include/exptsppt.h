/**********************************************************************************
 * EYELINK PORTABLE EXPT SUPPORT      (c) 1996, 2003 by SR Research               *
 *     8 June '97 by Dave Stampe       For non-commercial use only                * 
 * Greately modified by Suganthan Subramaniam, 11 March 2003			          *
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

#ifndef __SRRESEARCH__EXPT_SPPT_H__
#define __SRRESEARCH__EXPT_SPPT_H__
#ifdef __cplusplus 	/* For C++ compilers */
extern "C" {
#endif
#ifndef BYTEDEF
  #include "eyetypes.h"
  #include "eyelink.h"
#endif




/***************************************KEY SCANNING*******************************
 * some useful keys returned by getkey()                                          *
 * These keys allow remote control of tracker during setup.                       *
 * on non-DOS platforms, you should produce these codes and                       *
 * all printable (0x20..0x7F) keys codes as well.                                 *
 * Return JUNK_KEY (not 0) if untranslatable key pressed.                         *
 * TERMINATE_KEY can be to break out of EXPTSPPT loops.                           *
 **********************************************************************************/

#define CURS_UP    0x4800
#define CURS_DOWN  0x5000
#define CURS_LEFT  0x4B00
#define CURS_RIGHT 0x4D00

#define ESC_KEY   0x001B
#define ENTER_KEY 0x000D

#define PAGE_UP   0x4900
#define PAGE_DOWN 0x5100

/*****************************************************************************
 * This structure holds information on the display
 * Call get_display_infomation() to fill this with data
 * Check mode before running experiment!
 *****************************************************************************/
#ifndef DISPLAYINFODEF
  #define DISPLAYINFODEF
  typedef struct {
           INT32 left;      // left of display
           INT32 top;       // top of display
           INT32 right;     // right of display
           INT32 bottom;    // bottom of display
           INT32 width;     // width of display
           INT32 height;    // height of display
           INT32 bits;      // bits per pixel
           INT32 palsize;   // total entries in palette (0 if not indexed display mode)
           INT32 palrsvd;   // number of static entries in palette (0 if not indexed display mode)
           INT32 pages;     // pages supported
           float refresh;   // refresh rate in Hz
           INT32 winnt;     // 0 if Windows 95, 1 if Windows NT
              } DISPLAYINFO;
#endif
/************ SYSTEM SETUP *************/
/******************************************************************************
 * Set up the EyeLink system and connect to tracker
 * If <dummy> not zero, will create a dummy connection
 * where eyelink_is_connected() will return -1
 * Returns: 0 if success, else error code
 ******************************************************************************/
INT16 ELCALLTYPE open_eyelink_connection(INT16 dummy);

/*******************************************************************************
 * Close any EyeLink connection, release EyeLink system
 *******************************************************************************/
void ELCALLTYPE close_eyelink_connection(void);

/*******************************************************************************
 * Sets IP address for connection to EyeLink tracker
 * Argument is IP address (default is "100.1.1.1")  
 * An address of "255.255.255.255" will broadcast 
 * (broadcast may not work with multiple Ethernet cards) 
 * Returns: 0 if success, -1 if could not parse address string
 *******************************************************************************/
INT16 ELCALLTYPE set_eyelink_address(char *addr);

/*******************************************************************************
 * Changes the multitasking proirity of current application
 * Using THREAD_PRIORITY_ABOVE_NORMAL may reduce latency
 * Reset priority with THREAD_PRIORITY_NORMAL
 * Too high priority will stop the link from functioning!
 *******************************************************************************/
INT32 ELCALLTYPE set_application_priority(INT32 priority);


/************* SET CALIBRATION WINDOW ***********/



/*******************************************************************************
 * set the window to be used for calibration and drift correction
 * This window must not be destroyed during experiment!
 *******************************************************************************/
void release_eyelink_window(void);



/************* MESSAGE PUMP ************/

/*******************************************************************************
 * allows messages to operate in loops
 * returns nonzero if app terminated
 * eats key events, places on key queue for getkey()
 * getkey() and echo_key() also call this function
 *
 * calling this in loops allows Windows to process messages
 * returns nonzero if application terminated (ALT-F4 sent to window)
 * set <dialog_hook> to handle of modeless dialog
 * in order to properly handle its messages as well
 *******************************************************************************/
INT16 ELCALLTYPE message_pump();

/*******************************************************************************
 * similar to message_pump(), but only processes keypresses
 * this may help reduce latency
 *******************************************************************************/
INT16 ELCALLTYPE key_message_pump(void);


/*******************************************************************************
 * Similar to msec_delay(), but allows Widows message process
 * only allows message processing if delay > 20 msec
 * does not process dialog box messages
 *******************************************************************************/
void ELCALLTYPE pump_delay(UINT32 del);

/*********** KEYBOARD SUPPORT **********/


/*******************************************************************************
 * Initializes and empties local key queue
 *******************************************************************************/
void ELCALLTYPE flush_getkey_queue(void);

/*******************************************************************************
 * Similar to getkey(), but doesnt call message pump
 * Use to build message pump for your own window
 *******************************************************************************/
UINT16 ELCALLTYPE read_getkey_queue(void);


/*******************************************************************************
 * Similar to getkey(), bt also sends key to tracker
 * Supports reporting of repeating keys
 *******************************************************************************/
#define JUNK_KEY      1       /* returns this code if untranslatable key */
#define TERMINATE_KEY 0x7FFF  /* returns this code if program should exit */


/**********************************************************************************
 * Calls getkey(), also sends keys to tracker for remote control                  *
 * User implementation allows filtering of keys before sending                    *
 * returns same codes as getkey()                                                 *
 **********************************************************************************/
UINT16 ELCALLTYPE echo_key(void);

/*******************************************************************************
 * EYELINK tracker (MS-DOS) key scan equivalent
 * Processes Windows messages, records key events
 * Returns 0 if no key pressed 
 * returns 1-255 for non-extended keys 
 * returns 0x##00 for extended keys (##=hex code) 
 *******************************************************************************/
UINT16 ELCALLTYPE getkey(void);






/**************************** LINK FORMATTED COMMANDS *****************************/

/**********************************************************************************
 * link command formatting                                                        *
 * use just like printf()                                                         *
 * returns command result                                                         *
 * allows 500 msec. for command to finish                                         *
 **********************************************************************************/
INT16 ELCALLTYPE eyecmd_printf(char *fmt, ...);

/**********************************************************************************
 * link message formatting														  *
 * use just like printf()														  *
 * returns any send error														  *
 **********************************************************************************/
INT16 ELCALLTYPE eyemsg_printf(char *fmt, ...);





/***************************** RECORDING SUPPORT FUNCTIONS ************************
 * RETURN THESE CODES FROM YOUR RECORDING FUNCTIONS                               *
 * These codes are returned by all these functions                                *
 **********************************************************************************/

#define DONE_TRIAL   0  /* return codes for trial result */
#define TRIAL_OK     0
#define REPEAT_TRIAL 1
#define SKIP_TRIAL   2
#define ABORT_EXPT   3
#define TRIAL_ERROR  -1 /* Bad trial: no data, etc. */
#define  BX_DOTRANSFER  256

/*******************************************************************************
 * Call this to stop calibration/drift correction in progress
 * This could be called from a Windows message handler
 *******************************************************************************/
void ELCALLTYPE exit_calibration(void);


/********** ALERT BOX ************/

/*******************************************************************************
 * displays general STOP-icon alert box
 * text is formatted via printf-like arguments
 *******************************************************************************/
void ELCALLTYPE alert_printf(char *fmt, ...);


/********** VIDEO DISPLAY INFORMATION **********/
/*******************************************************************************
 * get information on video driver and current mode
 * use this to determine if in proper mode for experiment.
 * If <di> not NULL, copies data into it
 *******************************************************************************/
void ELCALLTYPE get_display_information(DISPLAYINFO *di);

/**********************************************************************************
 * Start recording with data types requested                                      *
 * Check that all requested link data is arriving                                 *
 * return 0 if OK, else trial exit code                                           *
 **********************************************************************************/
INT16 ELCALLTYPE start_recording(INT16 file_samples, INT16 file_events,
		   			  INT16 link_samples, INT16 link_events);

/**********************************************************************************
 * Check if we are recording: if not, report an error							  *
 * Also calls record_abort_hide() if recording aborted							  *
 * Returns 0 if recording in progress											  *
 * Returns ABORT_EXPT if link disconnected										  *
 * Handles recors abort menu if trial interrupted								  *
 * Returns TRIAL_ERROR if other non-recording state								  *
 * Typical use is																  *
 *   if((error=check_recording())!=0) return error;								  *
 **********************************************************************************/
INT16 ELCALLTYPE check_recording(void);

/**********************************************************************************
 * halt recording, return when tracker finished mode switch 
 **********************************************************************************/
void ELCALLTYPE stop_recording(void);

/**********************************************************************************
 * enter tracker idle mode, wait  till finished mode switch						  *
 **********************************************************************************/
void ELCALLTYPE set_offline_mode(void);

/**********************************************************************************
 * call at end of trial, return result											  *
 * check if we are in Abort menu after recording stopped						  *	
 * returns trial exit code														  *
 **********************************************************************************/
INT16 ELCALLTYPE check_record_exit(void);


/**********************************************************************************
 *CALIBRATION, DRIFT CORRECTION CONTROL
 **********************************************************************************/



/************** HOOKS FOR CAL GRAPHICS ****************/

/**********************************************************************************
 *PERFORM SETUP ON TRACKER
 * Sets a function to be called to before drawing
 * NULL can be used to disable hook
 * Hook function <hookfn> should return:
 **********************************************************************************/

/**********************************************************************************
 * Starts tracker into Setup Menu.												  *
 * From this the operator can do camera setup, calibrations, etc.				  *
 * Pressing ESC on the tracker exits.											  *
 * Leaving the setup menu on the tracker (ESC) key) also exits.					  *
 * RETURNS: 0 if OK, 27 if aborted, TERMINATE_KEY if pressed					  *
 **********************************************************************************/
INT16 ELCALLTYPE do_tracker_setup(void);
#define HOOK_ERROR    -1  /* if error occurred								*/
#define HOOK_CONTINUE  0  /* if drawing to continue after return from hook	*/
#define HOOK_NODRAW    1  /* if drawing should not be done after hook		*/



/***********************************************************************************
 * These are the constants in the argument to cal_sound_hook():
 ***********************************************************************************/

#define CAL_TARG_BEEP   1
#define CAL_GOOD_BEEP   0
#define CAL_ERR_BEEP   -1
#define DC_TARG_BEEP	3
#define DC_GOOD_BEEP	2
#define DC_ERR_BEEP	   -2





/**********************************************************************************
 *PERFORM DRIFT CORRECTION ON TRACKER
 **********************************************************************************/
/**********************************************************************************
 * Performs a drift correction, with target at (x,y).							  *
 * If operator aborts with ESC, we assume there's a setup						  *
 * problem and go to the setup menu (which may clear the						  *
 * display).  Redraw display if needed and repeat the							  *
 * call to  do_drift_correct() in this case.									  *
 * ARGS: x, y: position of target												  *
 *       draw: draws target if 1, 0 if you draw target first					  *
 *       allow_setup: 0 disables ESC key setup mode entry						  *
 * RETURNS: 0 if OK, 27 if Setup was called, TERMINATE_KEY if pressed             *
 **********************************************************************************/

INT16 ELCALLTYPE do_drift_correct(INT16 x, INT16 y, INT16 draw, INT16 allow_setup);

/**********************************************************************************
 *FILE TRANSFER
 **********************************************************************************/

/**********************************************************************************
 * THIS ROUTINE MAY NEED TO BE CREATED FOR EACH PLATFORM						  *
 * This call should be implemented for a standard programming interface			  *
 * Copies tracker file <src> to local file <dest>.								  *
 * If specifying full file name, be sure to add ".edf"							  *
 * extensions for data files.													  *
 * If <src> = "", tracker will send last opened data file.						  *
 * If <dest> is NULL or "", creates local file with source file name.			  *
 * Else, creates file using <dest> as name.  If <dest_is_path> != 0				  *
 * uses source file name but adds <dest> as directory path.						  *
 * returns: file size if OK, negative =  error code								  *
 **********************************************************************************/

INT32 ELCALLTYPE receive_data_file(char *src, char *dest, INT16 dest_is_path);


/**********************************************************************************
 * EXPTSPPT INTERNAL ROUTINES
 **********************************************************************************/

/**********************************************************************************
 * THESE FUNCTIONS IN XPT_GETF.C ARE USED FOR CROSS-PLATFORM SUPPORT			  *
 * If required, these may be used to develop alternatives or to					  *
 * implement the receive_data_file() code for specific platforms.				  *
 * Prepares for file receive: gets name											  *
 * <srch> has request name, if "" gets last opened EDF file						  *
 * <name> will contain actual file name,										  *
 * set <full_name> if you want DOS path included								  *
 * Returns: negative if error, else file size									  *
 **********************************************************************************/
INT32 start_file_receive(char *srch, char *name, int full_name);

/**********************************************************************************
 * receive next file block, at <offset> in file									  *
 * return size of block (less than FILE_BLOCK_SIZE if last)						  *
 * returns negative error code if can't receive									  *
 * FILE_XFER_ABORTED if can't recover											  *
 **********************************************************************************/
INT32 receive_file_block(INT32 offset, void *buf);


/**********************************************************************************
 * INTERNAL FUNCTION: YOU DO NOT NEED TO CALL									  *
 * If the trial is aborted (CTRL-ALT-A on the tracker)							  *
 * we go to user menu 1.  This lets us perform a setup,							  *
 * repeat this trial, skip the trial or quit.									  *
 * Requires the user menu 1 (Abort) to be set up								  *
 * on tracker (the default is preset in KEYS.INI).								  *
 * RETURNS: One of REPEAT_TRIAL, SKIP_TRIAL, ABORT_EXPT.						  *
 **********************************************************************************/
INT16 record_abort_handler(void);


/**********************************************************************************
 * (USED BY do_tracker_setup(), YOU DO NOT NEED TO CALL							  *
 * This handles display of the EyeLink camera images							  *
 * While in imaging mode, it contiuously requests								  *
 * and displays the current camera image										  *
 * It also displays the camera name and threshold setting						  *
 * Keys on the subject PC keyboard are sent to the tracker						  *
 * so the experimenter can use it during setup.									  *
 * It will exit when the tracker leaves											  *
 * imaging mode or discannects													  *
 * RETURNS: 0 if OK, TERMINATE_KEY if pressed, -1 if disconnect					  *
 **********************************************************************************/
INT16 ELCALLTYPE image_mode_display(void);


/**********************************************************************************
 * (USED BY do_tracker_setup(), YOU DO NOT NEED TO CALL						  	  *
 * While tracker is in any mode with fixation targets...						  *
 * Reproduce targets tracker needs.												  *
 * Called for you by do_tracker_setup() and do_drift_correct()					  *
 * (if allow_local_trigger) Local Spacebar acts as trigger						  *
 * (if allow_local_control) Local keys echoes to tracker						  *
 * RETURNS: 0 if OK, 27 if aborted, TERMINATE_KEY if pressed					  *
 **********************************************************************************/
INT16 ELCALLTYPE target_mode_display(void);


/**********************************************************************************
 * EDF OPEN, CLOSE 
 **********************************************************************************/

/**********************************************************************************
 * These functions were added as future revisions of EyeLink
 * might require significant time to open and close EDF files
 * Opens EDF file on tracker hard disk
 * Returns 0 if success, else error code
 **********************************************************************************/
INT16 ELCALLTYPE open_data_file(char *name);

/**********************************************************************************
 * Closes EDF file on tracker hard disk
 * Returns 0 if success, else error code
 **********************************************************************************/
INT16 ELCALLTYPE close_data_file(void);

/**********************************************************************************
 * NEW STANDARD FUNCTIONS
 * Checks state of aplication in message-passing GUI environments
 **********************************************************************************/
INT16 ELCALLTYPE application_terminated(void);







/**************************Convenient Macros *********************************/



#define  BX_AVERAGE     0   /* average combined pixels                 */
#define  BX_DARKEN      1   /* choose darkest (keep thin dark lines)   */
#define  BX_LIGHTEN     2   /* choose darkest (keep thin white lines)  */

#define  BX_MAXCONTRAST 4   /* stretch contrast to black->white        */
#define  BX_NODITHER    8   /* No dither, just quantize                */
#define  BX_GRAYSCALE   16  
#define SV_NOREPLACE	1   /* do not replace if the file already exists */
#define SV_MAKEPATH		2   /* make destination path if does not already exists */



/************* BREAK TESTS *********/

/*******************************************************************************
 * returns non-zero if ESC key held down
 *******************************************************************************/
INT16 ELCALLTYPE escape_pressed(void);

/*******************************************************************************
 * returns non-zero if Ctrl-C held down
 *******************************************************************************/
INT16 ELCALLTYPE break_pressed(void);


/********* ASYNCHRONOUS BREAKOUTS *********/
/*******************************************************************************
 * Because Windows is multi-tasking, some other event (i.e. a timer event or 
 * ALT-TAB) may affect your application during loops or calibration.
 * Your event handlers can call these functions to stop ongoing operations
 *
 * call from Windows event handlers when application must exit
 * forces calibration or drift correction to exit with result=27
 * when <assert> is nonzero,  will caused break_pressed() to test true 
 * continuously, also causes getkey() to return TERMINATE_KEY
 * If <assert> is 0, will restore break_pressed() and getkey() to normal
 *******************************************************************************/
void ELCALLTYPE terminal_break(INT16 assert);



/********** VIDEO DISPLAY INFORMATION **********/


/************ FILENAME SUPPORT **************/

#define BAD_FILENAME -2222
#define BAD_ARGUMENT -2223

/************************************************************************************
 * Splice 'path' to 'fname', store in 'ffname'
 * Tries to create valid concatenation
 * If 'fname' starts with '\', just adds drive from 'path'
 * If 'fname' contains drive specifier, it is not changed
 ************************************************************************************/
void ELCALLTYPE splice_fname(char *fname, char *path, char *ffname);

/************************************************************************************
 * Checks file name for legality
 * Attempts to ensure cross-platform for viewer
 * No spaces allowed as this interferes with messages 
 * assume viewer will translate forward/backward slash  
 * Windows: don't allow "<>?*:|,
 ************************************************************************************/
int ELCALLTYPE check_filename_characters(char *name);

/************************************************************************************
 * checks if file and/or path exists
 * returns 0 if does not exist
 *         1 if exists
 *        -1 if cannot overwrite   
 ************************************************************************************/
int ELCALLTYPE file_exists(char *path);

/************************************************************************************
 * Checks if path exists
 * Will create directory if 'create'
 * Creates directory from last name in 'path, unless
 * ends with '\' or 'is_dir' nonzero.
 * Otherwise, last item is assumed to be filename and is dropped   
 * Returns 0 if exists, 1 if created, -1 if failed
 ************************************************************************************/
int ELCALLTYPE create_path(char *path, INT16 create, INT16 is_dir);




 
/************************************************************************************
 * Sets up for realtime execution (minimum delays)
 * This may take some time (assume up to 100 msec)
 * <delay> sets min time so delay may be useful
 * Effects vary by operating system
 * Keyboard, mouse, and sound may be disabled in some OS
 * Has little effect in Win9x/ME
 ************************************************************************************/
void ELCALLTYPE begin_realtime_mode(UINT32 delay);

/************************************************************************************
 * Exits realtime execution mode
 * Typically just lowers priority
 ************************************************************************************/
void ELCALLTYPE end_realtime_mode(void);

/************************************************************************************
 * Raise application priority
 * May interfere with other applications
 ************************************************************************************/
void ELCALLTYPE set_high_priority(void);

/************************************************************************************
 * Sets application priority to system normal
 ************************************************************************************/
void ELCALLTYPE set_normal_priority(void);

/************************************************************************************
 * returns 1 if in realtime mode, else 0
 ************************************************************************************/
INT32 ELCALLTYPE in_realtime_mode(void);

#define KEYINPUT_EVENT              0x1
#define MOUSE_INPUT_EVENT			0x4
#define MOUSE_MOTION_INPUT_EVENT    0x5
#define MOUSE_BUTTON_INPUT_EVENT    0x6
typedef struct {
	byte type;
	byte  state;	    /* KEYDOWN = 0 or KEYUP    = 1 */
	short key;      /* keys */
} KeyInput;
/* Mouse motion event structure */
typedef struct {
	byte type;	/* MOUSE_MOTION_INPUT_EVENT */
	byte which;	/* The mouse device index */
	byte state;	/* The current button state */
	UINT16 x, y;	/* The X/Y coordinates of the mouse */
	UINT16 xrel;	/* The relative motion in the X direction */
	UINT16 yrel;	/* The relative motion in the Y direction */
} MouseMotionEvent;

/* Mouse button event structure */
typedef struct {
	byte type;	/* MOUSE_BUTTON_INPUT_EVENT */
	byte which;	/* The mouse device index */
	byte button;	/* The mouse button index */
	byte state;	/* BUTTONDOWN = 0 or BUTTONUP    = 1 */
	UINT16 x, y;	/* The X/Y coordinates of the mouse at press time */
} MouseButtonEvent;

typedef union
{
	byte type;
	KeyInput  key;
	MouseMotionEvent motion;
	MouseButtonEvent button;
	
}InputEvent;

typedef struct
{
	INT16  (ELCALLBACK * setup_cal_display_hook)(void);
	void   (ELCALLBACK * exit_cal_display_hook)(void) ;
	//void   (ELCALLBACK * cal_sound_hook)(INT16  error);
	void   (ELCALLBACK * record_abort_hide_hook)(void) ;
	INT16  (ELCALLBACK * setup_image_display_hook)(INT16 width, INT16 height) ;
	void   (ELCALLBACK * image_title_hook)(INT16 threshold, char *cam_name) ;
	void   (ELCALLBACK * draw_image_line_hook)(INT16 width, INT16 line, INT16 totlines, byte *pixels) ;
	void   (ELCALLBACK * set_image_palette_hook)(INT16 ncolors, byte r[], byte g[], byte b[]) ;
	void   (ELCALLBACK * exit_image_display_hook)(void) ;
	void   (ELCALLBACK * clear_cal_display_hook)() ;
	void   (ELCALLBACK * erase_cal_target_hook)();
	void   (ELCALLBACK * draw_cal_target_hook)(INT16 x, INT16 y);
	void   (ELCALLBACK * cal_target_beep_hook)(void) ;
	void   (ELCALLBACK * cal_done_beep_hook)(INT16 error) ;
	void   (ELCALLBACK * dc_done_beep_hook)(INT16 error) ;
	void   (ELCALLBACK * dc_target_beep_hook)(void) ;
	short  (ELCALLBACK * get_input_key_hook)(InputEvent * event);
	void   (ELCALLBACK * alert_printf_hook)(const char *);
}HOOKFCNS;
/*
setup the hook functions 
*/
void ELCALLTYPE setup_graphic_hook_functions( HOOKFCNS *hooks);
/*
get  all hook functions. 
*/
HOOKFCNS * ELCALLTYPE get_all_hook_functions();


int ELCALLTYPE eyelink_peep_input_event(InputEvent *event, int mask);
int ELCALLTYPE eyelink_get_input_event(InputEvent *event,int mask);
int ELCALLTYPE eyelink_peep_last_input_event(InputEvent *event, int mask);
void ELCALLTYPE eyelink_flush_input_event();

typedef struct
{
	byte r;
	byte g;
	byte b;
	byte unused;
}EYECOLOR;
typedef struct {
	int       ncolors;
	EYECOLOR *colors;
}EYEPALETTE;

typedef struct 
{

	byte colorkey;
	INT32 Rmask;
	INT32 Gmask;
	INT32 Bmask;
	INT32 Amask;
	EYEPALETTE *palette;
}EYEPIXELFORMAT;
typedef struct
{
	INT32 w;
	INT32 h;
	INT32 pitch;/* this can be 0. if this is 0, then ((depth+7)/8)*width is used */
	INT32 depth;/*8,15,16,24,32*/
	void *pixels; /* uncompressed pixel data */
	EYEPIXELFORMAT *format;
}EYEBITMAP;

typedef enum 
{
  JPEG,
  PNG,
  GIF,
  BMP,
  XPM,
}IMAGETYPE;
int ELCALLTYPE set_write_image_hook(int (ELCALLBACK * hookfn)(char *outfilename, int format, EYEBITMAP *bitmap), int options );
int ELCALLTYPE bitmap_save_and_backdrop(EYEBITMAP *hbm, INT16 xs, INT16 ys, INT16 width, INT16 height,
                             char *fname, char *path, INT16 save_options,
			     INT16 xd, INT16 yd, UINT16 bmp_options);
int ELCALLTYPE bitmap_save(EYEBITMAP *hbm, INT16 xs, INT16 ys, INT16 width, INT16 height,
                char *fname, char *path, INT16 sv_options);
int ELCALLTYPE bitmap_to_backdrop(EYEBITMAP *hbm, INT16 xs, INT16 ys, INT16 width, INT16 height,
                       INT16 xd, INT16 yd, UINT16 bx_options);
/*
	preliminary work functions. Do not use these
*/
INT16 timemsg_printf(UINT32 t, char *fmt, ...);

/* To get and set error messages  */
char *ELCALLTYPE eyelink_get_error(int id, char *function_name);
void ELCALLTYPE eyelink_set_error(int id, char *function_name, char *message);

int ELCALLTYPE eyelink_bitmap_core(EYEBITMAP * hbm, INT16 xs, INT16 ys, INT16 width, INT16 height,
		       char *fname, char *path, INT16 sv_options,
		       INT16 xd, INT16 yd, UINT16 xferoptions);


#define eyelink_bitmap_save_and_backdrop(a,b,c,d,e,f,g,h,i,j,k) \
										eyelink_bitmap_core(a,b,c,d,e,f,g,h,i,j,k|BX_DOTRANSFER)
#define eyelink_bitmap_to_backdrop(a,b,c,d,e,f,g,i)  eyelink_bitmap_core(a,b,c,d,e,NULL,NULL,0,f,g,i|BX_DOTRANSFER)
#define eyelink_gdi_bitmap_save(a,b,c,d,e,f,g)     eyelink_bitmap_core(a,b,c,d,e,f,g,0,0,0)


#endif
#ifdef __cplusplus 	/* For C++ compilation */
}
#endif

