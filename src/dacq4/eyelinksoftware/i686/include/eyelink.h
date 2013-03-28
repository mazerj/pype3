/**********************************************************************************
 * EYELINK PORTABLE EXPT SUPPORT      (c) 1996, 2003 by SR Research               *
 *     8 June '97 by Dave Stampe       For non-commercial use only                * 
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

#ifndef __SRRESEARCH__EYELINK_H__
#define __SRRESEARCH__EYELINK_H__

#ifndef SIMTYPESINCL
  #include "eye_data.h"
#endif

#ifndef SIMLINKINCL
#define SIMLINKINCL

#ifdef __cplusplus 	/* For C++ compilation */
extern "C" {
#endif

/****** ERROR AND RETURN CODES *********/
/* LINK RETURN CODES 			      */
/* These are produced from the link interface */
#define OK_RESULT      				0 /* OK */
#define NO_REPLY     	         1000 /* no reply yet (for polling test) */
#define LINK_TERMINATED_RESULT   -100 /* can't send or link closed */

	/* EyeLink TRACKER RETURN CODES */
#define ABORT_RESULT     	27		  /* operation aborted (calibration) */
	/* COMMAND PARSE ERRORS: */
#define UNEXPECTED_EOL_RESULT   -1   /* not enough data */
#define SYNTAX_ERROR_RESULT     -2   /* unknown command, unknown variable etc. */
#define BAD_VALUE_RESULT		-3   /* value is not right for command or tracker state */
#define EXTRA_CHARACTERS_RESULT -4   /* bad format or too many values */

#ifndef ELCALLTYPE      /* ELCALLTYPE used for Windows platform or other special calling formats */
 #if defined(WIN32) || defined(WIN16)  /* some sort of Windows: using DLL */
  #include <windows.h>
  #define ELCALLTYPE __cdecl  
 #else
  #define ELCALLTYPE    /* delete if not used */
 #endif
#endif

#ifndef ELCALLBACK      /* ELCALLTYPE used for Windows platform or other special calling formats */
 #if defined(WIN32) || defined(WIN16)  /* some sort of Windows: using DLL */
  #include <windows.h>
  #define ELCALLBACK CALLBACK
 #else
  #define ELCALLBACK    /* delete if not used */
 #endif
#endif


/****** INITIALIZE EYELINK TSR/LIBRARY ******/
/* MUST BE FIRST CALL TO LINK INTERFACE */
/* <bufsize> is desired buffer size (0 for default) */
/* <options> depends on implementation (NULL or "" for defaults) */
/* returns: 0 if failed, nonzero (-1 or TSR SWI number) if success */
UINT16 ELCALLTYPE open_eyelink_system(UINT16 bufsize, char FARTYPE *options);

/* set our EyeLink node name (up to 40 characters) */
void ELCALLTYPE eyelink_set_name(char FARTYPE *name);

/* shut down system (MUST do before exiting) */
void ELCALLTYPE close_eyelink_system(void);


/****** MICROSECOND CLOCK ******/
/* These time features are available with the TSR. */
/* On some platforms, the millisecond timing may   */
/* be coarse, and there is no microsecond timing   */

#define current_msec() current_time()

UINT32 ELCALLTYPE current_time(void);       /* current milliseconds (modulo 2^32) */
UINT32 ELCALLTYPE current_micro(MICRO FARTYPE *m);  /* rtns current milliseconds (modulo 2^32) */
UINT32 ELCALLTYPE current_usec(void);       /* rtns current microseconds (modulo 2^32) */
void ELCALLTYPE msec_delay(UINT32 n);       /* delays n msec using current_msec() */

/* returns current microseconds as double (56 bits) */
/* NOTE: not in SIMTSR--introduced for v3.0 of Windows DLL */
double current_double_usec(void);


/****** INITIALIZE EYE TRACKER CONNECTION ******/

/* ELINKADDR: a 16-byte address, works with any link type */

/* the broadcast address for the eye trackers */
extern ELINKADDR eye_broadcast_address;

/* the broadcast address for the remotes */
extern ELINKADDR rem_broadcast_address;

/* this node's address for the link implementation */
extern ELINKADDR our_address;

/* ERROR CODES returned by connection functions */
#define LINK_INITIALIZE_FAILED -200   /* can't use link */
#define CONNECT_TIMEOUT_FAILED -201   /* timed out waiting for reply */
#define WRONG_LINK_VERSION     -202   /* wrong TSR or source version */
#define TRACKER_BUSY           -203   /* tracker already connected   */

/* make connection using an ELINKADDR tracker node address */
/* can be broadcast_address to connect to single tracker   */
/* connect will fail if <busytest> is 1                    */
/* and tracker is connected to another remote              */
INT16 ELCALLTYPE eyelink_open_node(ELINKADDR node, INT16 busytest);

/* simple connect to single Eyelink tracker          */
/* equiv. to eyelink_open_node(broadcast_address, 0) */
INT16 ELCALLTYPE eyelink_open(void);

/* used by second remote to eavedrop on tracker */
/* disables all control functions               */
/* can only be used with single tracker on link */
INT16 ELCALLTYPE eyelink_broadcast_open(void);

/* used for debugging: all functions return a valid code */
/* does not connect to tracker */
INT16 ELCALLTYPE eyelink_dummy_open(void);

/* close connection to tracker.                                */
/* <send_msg> must be 0 if broadcast (eavedropping) connection */
INT16 ELCALLTYPE eyelink_close(INT16 send_msg);

/* start/stop timing resources             */
/* ONLY USED BY TSR INTERFACE UNDER MS-DOS */
INT16 ELCALLTYPE eyelink_reset_clock(INT16 enable);

/* returns 1 if connected,  */
/* -1 if dummy-connected    */ 
/* 2 if broadcast-connected (WIN v2.1 and later) */ 
/* 0 if not connected */
INT16 ELCALLTYPE eyelink_is_connected(void);


/* sets quiet mode (for use with broadcast)							*/
/* 0 = normal (send all)											*/
/* 1 = no commands (only messages, keys, read vars, time requests)  */
/* 2 = no sends at all												*/
/* -1 = just return current setting									*/
INT16 ELCALLTYPE eyelink_quiet_mode(INT16 mode);

/********** LINK NODE FUNCTIONS *********/

/* sends polling request to all trackers for ID */
/* returns: OK_RESULT or LINK_TERMINATED_RESULT */
INT16 ELCALLTYPE eyelink_poll_trackers(void);

/* sends polling request to all remotes for ID  */
/* returns: OK_RESULT or LINK_TERMINATED_RESULT */
INT16 ELCALLTYPE eyelink_poll_remotes(void);

/* checks for polling responses received    */
/* returns: 0 if no responses,              */
/* else number of responses received so far */
INT16 ELCALLTYPE eyelink_poll_responses(void);

/* gets copy of node data (in order of reception)            */
/* <resp> selects data: 0 gets our data, 1 get first RX, etc */
/* -1 gets eye tracker broadcast address  */
/* -2 gets remote broadcast address  */
/* <data> points to buffer to receive ELINKNODE data         */
/* returns: OK_RESULT if node data exists, else -1           */
INT16 ELCALLTYPE eyelink_get_node(INT16 resp, void FARTYPE *data);


/********** INTER-REMOTE COMMUNICATIONS ********/

/* NOTE: old packets are discarded if new packet received before reading! */

/* send an unformatted packet to another remote     */
/* <dsize> is data size: maximum ELREMBUFSIZE bytes */
/* returns: OK_RESULT or LINK_TERMINATED_RESULT     */
INT16 ELCALLTYPE eyelink_node_send(ELINKADDR node, void FARTYPE *data, UINT16 dsize);

/* checks for packet from another remote        */
/* packet data is copied into <data> buffer     */
/* sender address is copied into <addr> buffer  */
/* returns: 0 if no data, else packet size      */
INT16 ELCALLTYPE eyelink_node_receive(ELINKADDR node, void FARTYPE *data);


/********* MESSAGES AND COMMANDS *******/

/* See error return codes above */
/* in general, 0 or OK_RESULT means success */
/* and LINK_TERMINATED_RESULT means data could not be sent */

/* send text command string to tracker */
/* returns: OK_RESULT or LINK_TERMINATED_RESULT */
INT16 ELCALLTYPE eyelink_send_command(char FARTYPE *text);

/* checks for result from command execution         */
/* rtns: NO_REPLY if no result yet, OK_RESULT if OK */
/* negative return value is tracker error code      */
INT16 ELCALLTYPE eyelink_command_result(void);

/* send command string to tracker, wait for reply */
/* returns: OK_RESULT, NO_REPLY, or error code */
INT16 ELCALLTYPE eyelink_timed_command(UINT32 msec, char FARTYPE *text);

/* use to get more information on tracker result */
/* returns 0 if no message, else message length */
/* copies text result of command to <buf> */
INT16 ELCALLTYPE eyelink_last_message(char FARTYPE *buf);



/* send a data file message string to connected tracker */
/* returns: OK_RESULT or LINK_TERMINATED_RESULT */
INT16 ELCALLTYPE eyelink_send_message(char FARTYPE *msg);

/* send a data file message to any or all trackers */
/* returns: OK_RESULT or LINK_TERMINATED_RESULT    */
INT16 ELCALLTYPE eyelink_node_send_message(ELINKADDR node, char FARTYPE *msg);



/* send variable name to tracker for read */
/* returns: OK_RESULT or LINK_TERMINATED_RESULT */
INT16 ELCALLTYPE eyelink_read_request(char FARTYPE *text);

/* checks for reply to eyelink_read_request()     */
/* returns OK_RESULT if we have it, else NO_REPLY */
/* copies result to <buf> */
INT16 ELCALLTYPE eyelink_read_reply(char FARTYPE *buf);


/* sends request for tracker time update */
/* returns: OK_RESULT or LINK_TERMINATED_RESULT */
UINT32 ELCALLTYPE eyelink_request_time(void);

/* sends request to specific tracker for time update */
/* broadcast requests are not allowed                */
/* check for response with eyelink_read_time()       */
/* returns: OK_RESULT or LINK_TERMINATED_RESULT      */
UINT32 ELCALLTYPE eyelink_node_request_time(ELINKADDR node);

/* checks for reply to eyelink_request_time() */
/* returns: 0 if no reply, else time */
UINT32 ELCALLTYPE eyelink_read_time(void);



/********* CALIBRATION, SETUP, DRIFT CORRECT *********/

/* stop data flow, by returning tracker to offline mode  */
/* also aborts any other operations (setup, drift corr.) */
INT16 ELCALLTYPE eyelink_abort(void);

/* enters setup mode */
INT16 ELCALLTYPE eyelink_start_setup(void);

/* checks if in setup/val/cal/dc mode, or if done */
INT16 ELCALLTYPE eyelink_in_setup(void);

/* gets pixel X, Y of target */
/* returns 1 if visible, 0 if not */
INT16 ELCALLTYPE eyelink_target_check(INT16 FARTYPE *x, INT16 FARTYPE *y);

/* call to trigger acceptance of target fixation */
INT16 ELCALLTYPE eyelink_accept_trigger(void);

/* start drift correction, specify target position */
INT16 ELCALLTYPE eyelink_driftcorr_start(INT16 x, INT16 y);

/* check if drift correction, calibration done */
/* returns OK_RESULT, ABORT_RESULT, NO_REPLY   */
/* Reading result resets it to NO_REPLY */
INT16 ELCALLTYPE eyelink_cal_result(void);

/* apply correction from last drift correction */
INT16 ELCALLTYPE eyelink_apply_driftcorr(void);

/* copies last message from drift correction */
/* returns message length */
INT16 ELCALLTYPE eyelink_cal_message(char FARTYPE *msg);


/********* TRACKER MODE AND STATE **********/

/* Tracker state bit: AND with flag word to test functionality */

#define IN_DISCONNECT_MODE 16384   /* disconnected */
#define IN_UNKNOWN_MODE    0    /* mode fits no class (i.e setup menu) */
#define IN_IDLE_MODE       1    /* off-line */

#define IN_SETUP_MODE      2    /* setup or cal/val/dcorr */

#define IN_RECORD_MODE     4    /* data flowing */

#define IN_TARGET_MODE     8    /* some mode that needs fixation targets */
#define IN_DRIFTCORR_MODE  16   /* drift correction */
#define IN_IMAGE_MODE      32   /* image-display mode */

#define IN_USER_MENU       64   /* user menu */

#define IN_PLAYBACK_MODE  256   /* tracker sending playback data */

/* returns current tracker state as bit flags */
/* -1 = disconnect, 0 = unknown */
INT16 ELCALLTYPE eyelink_current_mode(void);


/* EYELINK RAW MODE CODES */
/* These specify modes, not functionality */

#define EL_IDLE_MODE         1
#define EL_IMAGE_MODE        2
#define EL_SETUP_MENU_MODE   3

#define EL_USER_MENU_1       5
#define EL_USER_MENU_2       6
#define EL_USER_MENU_3       7

#define EL_OPTIONS_MENU_MODE  8  // NEW FOR EYELIKN II

#define EL_OUTPUT_MENU_MODE  9

#define EL_DEMO_MENU_MODE    10
#define EL_CALIBRATE_MODE    11
#define EL_VALIDATE_MODE     12
#define EL_DRIFT_CORR_MODE   13
#define EL_RECORD_MODE       14

#define USER_MENU_NUMBER(mode) ((mode)-4)

/* returns raw mode number (0 if not connected) */
INT16 ELCALLTYPE eyelink_tracker_mode(void);

/* waits till new mode is finished setup */
/* maxwait = 0 to just test flag         */
/* rtns current state of switching flag: 0 if not ready */
INT16 ELCALLTYPE eyelink_wait_for_mode_ready(UINT32 maxwait);

/* returns number of last user-menu selection */
/* cleared on entry to user menu, or on reading */
INT16 ELCALLTYPE eyelink_user_menu_selection(void);



/************* DATA CHANNEL *************/

#define SAMPLE_TYPE 200

/* returns data (sample-to-pixels) prescaler */
INT16 ELCALLTYPE eyelink_position_prescaler(void);

/* resets data flow at start */
/* if <clear> deletes all queued data; */
INT16 ELCALLTYPE eyelink_reset_data(INT16 clear);

/* Update all data items */
/* return pointer to TSR/link state (ILINKDATA type) */
#ifndef MSORDER    /* some Microsoft function call extensions need different order */
  void FARTYPE * ELCALLTYPE eyelink_data_status(void);
#else
  void ELCALLTYPE FARTYPE * eyelink_data_status(void);
#endif

/* tests for block with samples or events (or both) */
/* rtns 1 if any of the selected types on, 0 if none on */
INT16 ELCALLTYPE eyelink_in_data_block(INT16 samples,INT16 events);

/* waits till a block of samples, events, or both is begun */
/* maxwait = 0 to just test */
/* rtns 1 if in block, 0 if not ready */
INT16 ELCALLTYPE eyelink_wait_for_block_start(UINT32 maxwait,
				   INT16 samples, INT16 events);

/* makes copy of next queue item */
/* if <buff> is NULL, just gets type */
/* returns item type: */
/* SAMPLE_TYPE if sample, 0 if none, else event code */
INT16 ELCALLTYPE eyelink_get_next_data(void FARTYPE *buf);

/* makes copy of last item from eyelink_get_next_data */
/* returns item type: */
/* SAMPLE_TYPE if sample, 0 if none, else event code */
INT16 ELCALLTYPE eyelink_get_last_data(void FARTYPE *buf);

/* makes copy of most recent sample received */
/* if <buff> is NULL, just checks if new */
/* returns -1 if none or error, 0 if old, 1 if new */
INT16 ELCALLTYPE eyelink_newest_sample(void FARTYPE *buf);


/* FLOATING-POINT DATA TYPES (ALLF_DATA type buffer) */
/* makes copy of last item from edf_get_next_data    */
/* returns item type: 				     */
/* SAMPLE_TYPE if sample, 0 if none, else event code */
INT16 ELCALLTYPE eyelink_get_float_data(void FARTYPE *buf);

/* makes FSAMPLE copy of most recent sample */
/* returns -1 if none or error, 0 if old, 1 if new */
INT16 ELCALLTYPE eyelink_newest_float_sample(void FARTYPE *buf);


/* returns LEFT_EYE, RIGHT_EYE or BINOCULAR */
/* depending on what data is available */
/* returns -1 if none available */
/* ONLY VALID AFTER STARTSAMPLES EVENT READ */
INT16 ELCALLTYPE eyelink_eye_available(void);

/* gets sample data content flag (0 if not in sample block) */
/* ONLY VALID AFTER STARTSAMPLES EVENT READ */
UINT16 ELCALLTYPE eyelink_sample_data_flags(void);

/* gets event data content flag (0 if not in event block) */
/* ONLY VALID AFTER STARTEVENTS EVENT READ */
UINT16 ELCALLTYPE eyelink_event_data_flags(void);

/* gets event type content flag (0 if not in event block) */
/* ONLY VALID AFTER STARTEVENTS EVENT READ */
UINT16 ELCALLTYPE eyelink_event_type_flags(void);

/* returns number of items remaining (samples+events) */
INT16 ELCALLTYPE eyelink_data_count(INT16 samples, INT16 events);

/* waits till a sample or event is available */
/* maxwait = 0 to just test */
/* rtns 1 if available, 0 if not */
INT16 ELCALLTYPE eyelink_wait_for_data(UINT32 maxwait,
			    INT16 samples, INT16 events);

/* get sample: skips any events */
/* rtns: 0 if none, 1 if found */
INT16 ELCALLTYPE eyelink_get_sample(void FARTYPE *sample);


#define RECORD_FILE_SAMPLES  1
#define RECORD_FILE_EVENTS   2
#define RECORD_LINK_SAMPLES  4
#define RECORD_LINK_EVENTS   8

/* controls what is accepted from link */
/* use eyelink_data_start() if tracker mode must be changed */
INT16 ELCALLTYPE eyelink_data_switch(UINT16 flags);

/* start data flow */
/* also aborts any other operations (setup, drift corr.) */
/* <flags> bits set data output types */
/* <lock> disables "esc" exit from tracking */
INT16 ELCALLTYPE eyelink_data_start(UINT16 flags, INT16 lock);

/* stop data flow */
/* also aborts any other operations (setup, drift corr.) */
INT16 ELCALLTYPE eyelink_data_stop(void);


/************* DATA PLAYBACK *************/
/* Start playback of last recording block */
/* Data file must still be open           */
/* All data in file is played back over link, */
/* with file (not link) data selected. */
/* During playback, the IN_PLAYBACK_MODE bit is set */
/* End of playback is signalled when there is no data */
/* available AND the IN_PLAYBACK_MODE bit is cleared */
INT16 ELCALLTYPE eyelink_playback_start(void);

/* stop playback of data file */
INT16 ELCALLTYPE eyelink_playback_stop(void);


/************ READ IMAGE DATA **********/

/* IMAGE TYPES: */
/* 0 = monochrome, packed (8 pixels/byte) */
/* 1 = 16 color, packed (2 pixels/byte) */
/* 2 = 16 color, 4 planes (8 pixels/byte, 4 planes of data in seq per line) */
/* 3 = 256 color, (1 pixel/byte) */

#define ELIMAGE_2   0	/* 1 plane, 1 bit per pixel (2 colors)   */
#define ELIMAGE_16  1   /* 4 bits per pixel, packed (16 colors)  */
#define ELIMAGE_16P 2   /* 1 bit per pixel, 4 planes (16 colors) */
#define ELIMAGE_256 3   /* 8 bits per pixel (16 or 256 colors)   */


/* request an image of <type> (see above) */
/* with size less than or eqaul to <xsize> and <ysize> */
/* rtn: 0 if sent OK, else error code */
INT16 ELCALLTYPE eyelink_request_image(INT16 type, INT16 xsize, INT16 ysize);

/* Test image-reception status: */
/*  0  = not receiving */
/* -1  = aborted */
/*  1  = receiving */
INT16 ELCALLTYPE eyelink_image_status(void);

/* forces image transmissin to halt */
void ELCALLTYPE eyelink_abort_image(void);

/* get data at start of new image */
/* -1 = aborted/not in rcve */
/* 0 = old palette, 1 = new palette */
/* ptrs to size: may be NULL */
INT16 ELCALLTYPE eyelink_image_data(INT16 FARTYPE *xsize, INT16 FARTYPE *ysize, INT16 FARTYPE *type);

/* gets unpacked line data */
/* rtns: -1 if error/not rx */
/* else rtns line number */
INT16 ELCALLTYPE eyelink_get_line(void FARTYPE *buf);


/* image data and palette structure */
/* uses brightness ramp plus special colors */
/* to compress and make remapping easier */
/* fits in old palette's 48-byte area */
#ifndef PALDATADEF
				/* NEW palette def: max 48 bytes */
typedef struct {
	byte palette_id;	/* palette id number */
	byte ncolors;		/* colors-1 (256 colors = 255) */

	byte camera;            /* camera: 1-3 */
	byte threshold;         /* image threshold */
	UINT16 flags;           /* flags: polarity, pupil present, etc. */
	UINT16 image_number;    /* sequence mod 65536 */
	byte extra[10];         /* future expansion */

	byte rfirst_color;		/* brightness ramp */
	byte rfirst_brite;      /* brite is 0-255 */
	byte rlast_color;
	byte rlast_brite;
	INT16 nspecial;         /* number of special colors */

	struct {
		 byte index;        /* palette entry */
		 byte r;			/* rgb is 0-255 */
		 byte g;
		 byte b;
	} spcolors[6];			/* up to 6 special colors */
} IMAGE_PALDATA;

#define PALDATADEF
#endif

/* get palette: always ramp definition */
/* rtn: -1 if no image in progress     */
/* 0 if old, 1 if new palette          */
/* non-palette data in *pal may change even if 0 returned */
INT16 ELCALLTYPE eyelink_get_palette(void FARTYPE *pal);


/********** KEYS/BUTTONS **********/

/* key/button state flag indicates type of key/button action: */
#define KB_PRESS   10
#define KB_RELEASE -1
#define KB_REPEAT  1

/* Key modifiers are similar to BIOS INT 16h function 2 */
/* DOS key modifiers: a set of flag bits.  By using these */
/* to test the <mods> flag, you can tell if special */
/* key combinations were used. */

#define NUM_LOCK_ON      0x20
#define CAPS_LOCK_ON     0x40
#define ALT_KEY_DOWN     0x08
#define CTRL_KEY_DOWN    0x04
#define SHIFT_KEY_DOWN   0x03   /* left, right shift keys */

/* The key code itself is what BIOS INT 16h function 0 */
/* reads: ASCII for most keys, with other codes for ENTER,ESC etc. */
/* For the extended DOS keys, the code has the extended */
/* code in the MSByte, with the LSbyte 0 */

/* A SPECIAL CASE: */
/* codes of either 0 or 0xFF00 mean the mod is a button number */

#define KB_BUTTON 0xFF00U

#define F1_KEY    0x3B00    /* some samples */
#define F2_KEY    0x3C00
#define F3_KEY    0x3D00
#define F4_KEY    0x3E00
#define F5_KEY    0x3F00
#define F6_KEY    0x4000
#define F7_KEY    0x4100
#define F8_KEY    0x4200
#define F9_KEY    0x4300
#define F10_KEY   0x4400

#define PAGE_UP    0x4900
#define PAGE_DOWN  0x5100
#define CURS_UP    0x4800
#define CURS_DOWN  0x5000
#define CURS_LEFT  0x4B00
#define CURS_RIGHT 0x4D00

#define ESC_KEY   0x001B
#define ENTER_KEY 0x000D

/* reads any queued key or button events */
/* returns: 0 if none, keycode if key, */
/* KB_BUTTON (mods=button number) if button */
/* mods are extra keys (shift, ctrl, alt etc) */
/* state is KB_PRESS, KB_RELEASE, or KB_REPEAT */
/* <kcode> is key scan code */
UINT16 ELCALLTYPE eyelink_read_keybutton(INT16 FARTYPE *mods,
			      INT16 FARTYPE *state, UINT16 *kcode, UINT32 FARTYPE *time);

/* sends key/button state chane to tracker */
/* code = KB_BUTTON, mods = number for button */
/* state is KB_PRESS, KB_RELEASE, or KB_REPEAT */
/* Returns: OK_RESULT or LINK_TERMINATED_RESULT */
INT16 ELCALLTYPE eyelink_send_keybutton(UINT16 code, UINT16 mods, INT16 state);

/* reads the currently-known state of all buttons */
/* the bits in the returned value will be */
/* set (1) if corresponding button is pressed */
/* LSB is button 1, MSB is button 16 */
/* currently only 8 buttons available */
UINT16 ELCALLTYPE eyelink_button_states(void);

/* returns the last button pressed (1-16, 0 if none) */
/* if "time" is not NULL, stores time here           */
/* clears button so reads 0 till another pressed     */
UINT16 ELCALLTYPE eyelink_last_button_press(UINT32 FARTYPE *time);

/* flushes any waiting keys or buttons */
/* also updates button state flags, but these */
/*  may not be valid for several milliseconds */
/* if <enable_buttons> also stores buttons */
/*  otherwise just updates for last_button_press() */
INT16 ELCALLTYPE eyelink_flush_keybuttons(INT16 enable_buttons);



/************* FILE TRANSFER ************/

/* request send of file "src" */
/* if "", gets last data file */
/* rtns: 0 if OK, else send error */
INT16 ELCALLTYPE eyelink_request_file_read(char FARTYPE *src);

/* error codes returned  in size field */
#define FILE_XFER_ABORTED  -110
#define FILE_CANT_OPEN     -111
#define FILE_NO_REPLY      -112  /* no-data returned */
#define FILE_BAD_DATA      -113

#define FILEDATA_SIZE_FLAG  999  /* start block has name, offset=total size */
#define FILE_BLOCK_SIZE     512  /* full block size: if less, it's last block */

/* get next block of file */
/* if *<offset> if not NULL, will be */
/* filled with block-start offset in file */
/* returns: negative if error */
/* NO_REPLY if waiting for packet */
/* else block size (0..512) */
/* size is < 512 (can be 0) if at EOF */
INT16 ELCALLTYPE eyelink_get_file_block(void FARTYPE *buf, INT32 FARTYPE *offset);

/* ask for next block of file */
/* reads from <offset>        */
INT16 ELCALLTYPE eyelink_request_file_block(UINT32 offset);

/* aborts send of file */
/* rtns: 0 if OK, else send error */
INT16 ELCALLTYPE eyelink_end_file_transfer(void);


/***************** EYELINK II EXTENSIONS *****************/

/* returns tracker version                     */
/* if not yet connected, c will be ""          */
/* for EyeLink I,  c will be "EYELINK I"       */
/* for EyeLink II, c will be "EYELINK II x.xx" */
/*    where x.xx is version number             */
/* RETURNS: 0 if unknown, 1 or 2 for EyeLink I or II */
INT16 ELCALLTYPE eyelink_get_tracker_version(char FARTYPE *c);

/**********************************************************************************
 * Get EyeLink II extended block information
 * Returns 0 if available, 
 *       -1 if not (not in data block or not EyeLink II tracker)
 * copies data if pointers not NULL:
 *   *sample_rate = samples per second
 *   *crmode = 0 if pupil-only, else pupil-CR
 *   *file_filter = 0 if file sample filter off, 1 for std, 2 for double filter
 *   *link_filter = 0 if link sample filter off, 1 for std, 2 for double filter
 **********************************************************************************/
INT16 ELCALLTYPE eyelink2_mode_data(INT16 *sample_rate, INT16 *crmode, 
								  INT16 *file_filter, INT16 *link_filter);

/************ BITMAP TRANSFER ***************/

/* send bitmap data packet to tracker */
/* seq is 1 for forst packet, increases thereafter */
INT16 ELCALLTYPE eyelink_bitmap_packet(void *data, UINT16 size, UINT16 seq);

/* get bitmap ack count */
/* negative: special code or sequence number to restart at */
/* reading resets count to 0 */
INT16 ELCALLTYPE eyelink_bitmap_ack_count(void);

/* codes returned by ACK */
#define ABORT_BX -32000  /* signal to abort bitmap send */
#define PAUSE_BX -32001  /* signal that last packet dropped (full queue) */
#define DONE_BX  -32002  /* last block received OK */


/*********** NEW CONNECTION ADDRESS ************/
/**********************************************************************************
 * Address used for non-connected time requests and message sends. the "proper" 
 * way to do this is with the "node" type of functions but we allow a "back door" 
 * to simplify higher level support functions.  This is also the address used 
 * under Windows for looking for tracker (an IP broadcast is used on all 
 * other platforms). There is a bug in the Windows networking, causing broadcasts 
 * sent on all cards to have the IP source addres of only the first card. This 
 * means the tracker sends its connection reply to the wrong address. So the exact 
 * address or a subnet broadcast address (i.e. 100.1.1.255 for a subnet mask of 
 * 255.255.255.0) needs to be set to that of the tracker.
 **********************************************************************************/
void ELCALLTYPE eyelink_set_tracker_node(ELINKADDR node);
double ELCALLTYPE eyelink_time_offset(void);
double ELCALLTYPE eyelink_tracker_time(void);
#ifdef __cplusplus	/* For C++ compilation */
}
#endif

#endif /* SIMLINKINCL */
#endif /* __SRRESEARCH__EYELINK_H__*/

