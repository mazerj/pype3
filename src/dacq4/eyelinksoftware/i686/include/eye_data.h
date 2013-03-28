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

#ifndef __SRRESEARCH__EYE_DATA_H__
#define __SRRESEARCH__EYE_DATA_H__

#ifndef BYTEDEF
  #include "eyetypes.h"
#endif

#ifndef SIMTYPESINCL
#define SIMTYPESINCL

#ifdef __cplusplus 	/* For C++ compilation */
extern "C" {
#endif

/*********** EYE DATA FORMATS **********/

/**********************************************************************************
 * ALL fields use MISSING_DATA when value was not read, EXCEPT for <buttons>,     *
 * <time>, <sttime> and <entime>, which use 0. This is true for both floating     *
 * point or integer variables. Both samples and events may have several fields    *
 * that have not been updated. These fields may be detected from the content      *
 * flags, or by testing the field value against these constants:                  *
 **********************************************************************************/

#define MISSING_DATA -32768     /* data is missing (integer) */
#define MISSING -32768
#define INaN -32768

/**********************************************************************************
 * binocular data needs to ID the eye for events  
 * samples need to index the data 
 * These constants are used as eye identifiers 
 **********************************************************************************/

#define LEFT_EYE  0   /* index and ID of eyes */
#define RIGHT_EYE 1
#define LEFTEYEI  0
#define RIGHTEYEI 1
#define LEFT      0
#define RIGHT     1
#define BINOCULAR 2   /* data for both eyes available */


/********* EYE SAMPLE DATA FORMATS *******/

/**********************************************************************************
 * The SAMPLE struct contains data from one 4-msec eye-tracker sample. The <flags> 
 * field has a bit for each type of data in the sample. Fields not read have 0 
 * flag bits, and are set to MISSING_DATA flags to define what data is included 
 * in each sample.  There is one bit for each type.  Total data for samples 
 * in a block is indicated by these bits in the <sam_data> field of ILINKDATA or 
 * EDF_FILE, and is updated by the STARTSAMPLES control event. 
 **********************************************************************************/

#define SAMPLE_LEFT      0x8000  /* data for these eye(s) */
#define SAMPLE_RIGHT     0x4000

#define SAMPLE_TIMESTAMP 0x2000  /* always for link, used to compress files */

#define SAMPLE_PUPILXY   0x1000  /* pupil x,y pair */
#define SAMPLE_HREFXY    0x0800  /* head-referenced x,y pair */
#define SAMPLE_GAZEXY    0x0400  /* gaze x,y pair */
#define SAMPLE_GAZERES   0x0200  /* gaze res (x,y pixels per degree) pair */
#define SAMPLE_PUPILSIZE 0x0100  /* pupil size */
#define SAMPLE_STATUS    0x0080  /* error flags */
#define SAMPLE_INPUTS    0x0040  /* input data port */
#define SAMPLE_BUTTONS   0x0020  /* button state: LSBy state, MSBy changes */

#define SAMPLE_HEADPOS   0x0010  /* * head-position: byte tells # words */
#define SAMPLE_TAGGED    0x0008  /* * reserved variable-length tagged */
#define SAMPLE_UTAGGED   0x0004  /* * user-defineabe variable-length tagged */


#ifndef ISAMPLEDEF	/* INTEGER SAMPLE DATA */
#define ISAMPLEDEF
typedef struct {
	UINT32 time;			/* time of sample */
	INT16  type;			/* always SAMPLE_TYPE */
	UINT16 flags;			/* flags to indicate contents */
	INT16  px[2], py[2];    /* pupil xy */
	INT16  hx[2], hy[2];    /* headref xy */
	UINT16 pa[2]; 			/* pupil size or area */
	INT16 gx[2], gy[2];		/* screen gaze xy */
	INT16 rx, ry;			/* screen pixels per degree */
	UINT16 status;			/* tracker status flags    */
	UINT16 input;			/* extra (input word)      */
	UINT16 buttons;			/* button state & changes  */
	INT16  htype;			/* head-tracker data type (0=none) */
	INT16  hdata[8];		/* head-tracker data */
} ISAMPLE;
#endif


#ifndef FSAMPLEDEF		/* FLOATING-POINT SAMPLE */
#define FSAMPLEDEF 1    /* gaze, resolution prescaling removed */
typedef struct {
	UINT32 time;			/* time of sample */
	INT16  type;			/* always SAMPLE_TYPE */
	UINT16 flags;			/* flags to indicate contents */
	float  px[2], py[2];	/* pupil xy */
	float  hx[2], hy[2];    /* headref xy */
	float  pa[2]; 			/* pupil size or area */
	float gx[2], gy[2];		/* screen gaze xy */
	float rx, ry;			/* screen pixels per degree */
	UINT16 status;			/* tracker status flags    */
	UINT16 input;			/* extra (input word)      */
	UINT16 buttons;			/* button state & changes  */
	INT16  htype;			/* head-tracker data type (0=none)   */
	INT16  hdata[8];		/* head-tracker data (not prescaled) */
} FSAMPLE;
#endif




/******** EVENT DATA FORMATS *******/

/**********************************************************************************
 * ALL fields use MISSING_DATA when value was not read, 
 * EXCEPT for <buttons>, <time>, <sttime> and <entime>, which use 0. 
 * This is true for both floating point or integer variables. 
 **********************************************************************************/

			/* INTEGER EYE-MOVEMENT EVENTS */
#ifndef IEVENTDEF
#define IEVENTDEF
typedef struct  {
	UINT32 time;			/* effective time of event */
	INT16  type;			/* event type */
	UINT16 read;			/* flags which items were included */
	INT16  eye;				/* eye: 0=left,1=right */
	UINT32 sttime, entime;	/* start, end times */
	INT16  hstx, hsty;		/* starting points */
	INT16  gstx, gsty;		/* starting points */
	UINT16 sta;
	INT16  henx, heny;		/* ending points */
	INT16  genx, geny;		/* ending points */
	UINT16 ena;
	INT16  havx, havy;		/* averages */
	INT16  gavx, gavy;		/* averages */
	UINT16 ava;				/* also used as accumulator */
	INT16 avel;				/* avg velocity accum */
	INT16 pvel;				/* peak velocity accum */
	INT16 svel, evel;       /* start, end velocity */
	INT16 supd_x, eupd_x;   /* start, end units-per-degree */
	INT16 supd_y, eupd_y;   /* start, end units-per-degree */
	UINT16 status;          /* error, warning flags */
} IEVENT;
#endif


			/* FLOATING-POINT EYE EVENT */
#ifndef FEVENTDEF       /* gaze, resolution, velocity prescaling removed */
#define FEVENTDEF 1
typedef struct  {
	UINT32 time;			/* effective time of event */
	INT16  type;			/* event type */
	UINT16 read;			/* flags which items were included */
	INT16  eye;				/* eye: 0=left,1=right */
	UINT32 sttime, entime;  /* start, end times */
	float  hstx, hsty;      /* starting points */
	float  gstx, gsty;      /* starting points */
	float  sta;
	float  henx, heny;      /* ending points */
	float  genx, geny;      /* ending points */
	float  ena;
	float  havx, havy;      /* averages */
	float  gavx, gavy;      /* averages */
	float  ava;
	float  avel;            /* avg velocity accum */
	float  pvel;            /* peak velocity accum */
	float  svel, evel;      /* start, end velocity */
	float  supd_x, eupd_x;  /* start, end units-per-degree */
	float  supd_y, eupd_y;  /* start, end units-per-degree */
	UINT16 status;          /* error, warning flags */
} FEVENT;
#endif


			/* message events: usually text */
			/* but may contain binary data  */
#ifndef IMESSAGEDEF
#define IMESSAGEDEF
typedef struct  {
	UINT32 time;       /* time message logged */
	INT16  type;       /* event type: usually MESSAGEEVENT */
	UINT16 length;	   /* length of message */
	byte   text[260];  /* message contents (max length 255) */
} IMESSAGE;
#endif

			/* button, input, other simple events */
#ifndef IOEVENTDEF
#define IOEVENTDEF
typedef struct  {
	UINT32 time;       /* time logged */
	INT16  type;       /* event type: */
	UINT16 data;	   /* coded event data */
} IOEVENT;
#endif


/************ COMPOSITE DATA BUFFERS ***********/

			/* BUFFER to store all read types: integer */
#ifndef ALLDATADEF
#define ALLDATADEF
typedef union {
	IEVENT    ie;
	IMESSAGE  im;
	IOEVENT   io;
	ISAMPLE   is;
} ALL_DATA ;
#endif

			/* FLOATING POINT TYPES for eye event, sample */
#ifndef EDFDATADEF
#define EDFDATADEF
typedef union {
	FEVENT    fe;
	IMESSAGE  im;
	IOEVENT   io;
	FSAMPLE   fs;
} ALLF_DATA ;
#endif


/********** SAMPLE, EVENT BUFFER TYPE CODES ***********/
		/* the type code for samples */
#define SAMPLE_TYPE 200

/**********************************************************************************
 * This type can help in detecting event type or in allocating storage, but does 
 * not differentiate between integer and floating-point versions of data. 
 * BUFFER TYPE id's: in "last_data_buffer_type" 
**********************************************************************************/
#define ISAMPLE_BUFFER   SAMPLE_TYPE      /* old alias */
#define IEVENT_BUFFER     66
#define IOEVENT_BUFFER     8
#define IMESSAGE_BUFFER  250
#define CONTROL_BUFFER    36
#define ILINKDATA_BUFFER  CONTROL_BUFFER  /* old alias */



/************* EVENT TYPE CODES ************/
			/* buffer = IEVENT, FEVENT, btype = IEVENT_BUFFER */
#define STARTPARSE 1 	/* these only have time and eye data */
#define ENDPARSE   2
#define BREAKPARSE 10

			/* EYE DATA: contents determined by evt_data */
#define STARTBLINK 3    /* and by "read" data item */
#define ENDBLINK   4    /* all use IEVENT format */
#define STARTSACC  5
#define ENDSACC    6
#define STARTFIX   7
#define ENDFIX     8
#define FIXUPDATE  9

  /* buffer = (none, directly affects state), btype = CONTROL_BUFFER */
			 /* control events: all put data into */
			 /* the EDF_FILE or ILINKDATA status  */
#define STARTSAMPLES 15  /* start of events in block */
#define ENDSAMPLES   16  /* end of samples in block */
#define STARTEVENTS  17  /* start of events in block */
#define ENDEVENTS    18  /* end of events in block */


	/* buffer = IMESSAGE, btype = IMESSAGE_BUFFER */
#define MESSAGEEVENT 24  /* user-definable text or data */


	/* buffer = IOEVENT, btype = IOEVENT_BUFFER */
#define BUTTONEVENT  25  /* button state change */
#define INPUTEVENT   28  /* change of input port */

#define LOST_DATA_EVENT 0x3F   /* NEW: Event flags gap in data stream */

/************* CONSTANTS FOR EVENTS ************/

	/* "read" flag contents in IEVENT */
	/* time data */
#define READ_ENDTIME 0x0040     /* end time (start time always read) */

			    /* non-position eye data: */
#define READ_GRES    0x0200     /* gaze resolution xy */
#define READ_SIZE    0x0080     /* pupil size */
#define READ_VEL     0x0100     /* velocity (avg, peak) */
#define READ_STATUS  0x2000     /* status (error word) */

#define READ_BEG     0x0001     /* event has start data for vel,size,gres */
#define READ_END     0x0002     /* event has end data for vel,size,gres */
#define READ_AVG     0x0004     /* event has avg pupil size, velocity */

			    /* position eye data */
#define READ_PUPILXY 0x0400    /* pupilxy REPLACES gaze, href data if read */
#define READ_HREFXY  0x0800
#define READ_GAZEXY  0x1000

#define READ_BEGPOS  0x0008    /* position data for these parts of event */
#define READ_ENDPOS  0x0010
#define READ_AVGPOS  0x0020


		       /* RAW FILE/LINK CODES: REVERSE IN R/W */
#define FRIGHTEYE_EVENTS  0x8000 /* has right eye events */
#define FLEFTEYE_EVENTS   0x4000 /* has left eye events */

	/* "event_types" flag in ILINKDATA or EDF_FILE */
	/* tells what types of events were written by tracker */

#define LEFTEYE_EVENTS   0x8000 /* has left eye events */
#define RIGHTEYE_EVENTS  0x4000 /* has right eye events */
#define BLINK_EVENTS     0x2000 /* has blink events */
#define FIXATION_EVENTS  0x1000 /* has fixation events */
#define FIXUPDATE_EVENTS 0x0800 /* has fixation updates */
#define SACCADE_EVENTS   0x0400 /* has saccade events */
#define MESSAGE_EVENTS   0x0200 /* has message events */
#define BUTTON_EVENTS    0x0040 /* has button events */
#define INPUT_EVENTS     0x0020 /* has input port events */


	/* "event_data" flags in ILINKDATA or EDF_FILE */
	/* tells what types of data were included in events by tracker */

#define EVENT_VELOCITY  0x8000  /* has velocity data */
#define EVENT_PUPILSIZE 0x4000  /* has pupil size data */
#define EVENT_GAZERES   0x2000  /* has gaze resolution */
#define EVENT_STATUS    0x1000  /* has status flags */

#define EVENT_GAZEXY    0x0400  /* has gaze xy position */
#define EVENT_HREFXY    0x0200  /* has head-ref xy position */
#define EVENT_PUPILXY   0x0100  /* has pupil xy position */

#define FIX_AVG_ONLY    0x0008  /* only avg. data to fixation evts */
#define START_TIME_ONLY 0x0004  /* only start-time in start events */

#define PARSEDBY_GAZE   0x00C0  /* how events were generated */
#define PARSEDBY_HREF   0x0080
#define PARSEDBY_PUPIL  0x0040



/************ LINK STATE DATA ************/

	/* the data on current state of link read and SIMTSR   */
	/* For EDF file state, see EDFFILE.H for EDF_FILE type */

#ifndef ILINKDATADEF
#define ILINKDATADEF
#define ILINKDATAVERSION 2

#define ELNAMESIZE    40    /* max. tracker or remote name size   */
#define ELREMBUFSIZE  420   /* max. remote-to-remote message size */
#define ELINKADDRSIZE 16    /* Node address (format varies) */

typedef byte ELINKADDR[ELINKADDRSIZE];  /* all-purpose address for link */

typedef struct  {           /* name and address for connection or ping */
	ELINKADDR addr;
	char name[ELNAMESIZE];
} ELINKNODE;


typedef struct  {

	UINT32 time;        /* time of last control event */
	UINT32 version;     /* structure version */

	UINT16 samrate;     /* 10*sample rate (0 if no samples, 1 if nonconstant) */
	UINT16 samdiv;      /* sample "divisor" (min msec between samples) */

	UINT16 prescaler;   /* amount to divide gaze x,y,res by */
	UINT16 vprescaler;  /* amount to divide velocity by */
	UINT16 pprescaler;  /* pupil prescale (1 if area, greater if diameter) */
	UINT16 hprescaler;  /* head-distance prescale (to mm) */

	UINT16 sample_data;     /* 0 if off, else all flags */
	UINT16 event_data;	/* 0 if off, else all flags */
	UINT16 event_types;     /* if off, else event-type flags */

	byte in_sample_block;   /* set if in block with samples */
	byte in_event_block;    /* set if in block with events */
	byte have_left_eye;     /* set if any left-eye data expected */
	byte have_right_eye;    /* set if any right-eye data expected */

	UINT16 last_data_gap_types;	/* flags what we lost before last item */
	UINT16 last_data_buffer_type;   /* buffer-type code */
	UINT16 last_data_buffer_size;   /* buffer size of last item */

	UINT16 control_read;      /* set if control event read with last data */
	UINT16 first_in_block;    /* set if control event started new block */

	UINT32 last_data_item_time;	/* time field of item */
	UINT16 last_data_item_type;     /* type: 100=sample, 0=none, else event type */
	UINT16 last_data_item_contents; /* content: <read> (IEVENT), <flags> (ISAMPLE) */

	ALL_DATA last_data_item;	/* buffer containing last item */

	UINT32 block_number;	/* block in file */
	UINT32 block_sample;	/* samples read in block so far */
	UINT32 block_event;	/* events (excl. control read in block */

			   /* RESTORES DROPPED SAMPLE DATA */
	UINT16 last_resx;       /* updated by samples only */
	UINT16 last_resy;       /* updated by samples only */
	UINT16 last_pupil[2];	/* updated by samples only */
	UINT16 last_status;     /* updated by samples, events */

			/* LINK-SPECIFIC DATA */

	UINT16 queued_samples;  /* number of items in queue */
	UINT16 queued_events;   /* includes control events */

	UINT16 queue_size;      /* total queue buffer size */
	UINT16 queue_free;      /* unused bytes in queue */

	UINT32 last_rcve_time;  /* time tracker last sent packet */

	byte   samples_on;      /* data type rcve enable (switch) */
	byte   events_on;

	UINT16 packet_flags;    /* status flags from data packet */

	UINT16 link_flags;      /* status flags from link packet header */
	UINT16 state_flags;     /* tracker error state flags */
	byte   link_dstatus;    /* tracker data output state */
	byte   link_pendcmd;    /* tracker commands pending  */
	UINT16 reserved;        /* 0 for EyeLink I or original EyeLink API DLL. */
							/* EYELINK II ONLY: MSB set if read             */
							/* crmode<<8 + file_filter<<4 + link_filter     */
							/* crmode = 0 if pupil, else pupil-CR           */
							/* file_filter, link_filter: 0, 1, or 2         */
							/*   for level of heuristic filter applied      */

			/* zero-term. strings: names for connection */
			/* if blank, connects to any tracker    */
	char our_name[40];      /* a name for our machine       */
	ELINKADDR our_address;
	char eye_name[40];      /* name of tracker connected to */
	ELINKADDR eye_address;

	ELINKADDR ebroadcast_address;   /* TSR exports */
	ELINKADDR rbroadcast_address;

	UINT16 polling_remotes; /* 1 if polling remotes, else polling trackers */
	UINT16 poll_responses;  /* total nodes responding to polling */
	ELINKNODE nodes[4];     /* data on nodes */

} ILINKDATA;
#endif

	/* packet_flags: */
#define PUPIL_DIA_FLAG     0x0001  /* set if pupil is diameter (else area) */
#define HAVE_SAMPLES_FLAG  0x0002  /* set if we have samples */
#define HAVE_EVENTS_FLAG   0x0004  /* set if we have events */

#define HAVE_LEFT_FLAG     0x8000  /* set if we have left-eye data */
#define HAVE_RIGHT_FLAG    0x4000  /* set if we have right-eye data */

	/* dropped events or samples preceding a read item */
	/* are reported using these flag bits in "last_data_gap_types" */
	/* Dropped control events are used to update */
	/* the link state prior to discarding. */
#define DROPPED_SAMPLE  0x8000
#define DROPPED_EVENT   0x4000
#define DROPPED_CONTROL 0x2000

		/* <link_dstatus> FLAGS */
#define DFILE_IS_OPEN    0x80      /* disk file active */
#define DFILE_EVENTS_ON  0x40	   /* disk file writing events */
#define DFILE_SAMPLES_ON 0x20      /* disk file writing samples */
#define DLINK_EVENTS_ON  0x08      /* link sending events */
#define DLINK_SAMPLES_ON 0x04      /* link sending samples */
#define DRECORD_ACTIVE   0x01      /* in active recording mode */

		/* <link_flags> flags */
#define COMMAND_FULL_WARN 0x01     /* too many commands: pause */
#define MESSAGE_FULL_WARN 0x02     /* too many messages: pause */
#define LINK_FULL_WARN    0x04     /* link, command, or message load */
#define FULL_WARN         0x0F     /* test mask for any warning */

#define LINK_CONNECTED    0x10     /* link is connected */
#define LINK_BROADCAST    0x20     /* link is broadcasting */
#define LINK_IS_TCPIP     0x40     /* link is TCP/IP (else packet) */


/************ STATUS FLAGS (samples and events) ****************/

#define LED_TOP_WARNING       0x0080    // marker is in border of image
#define LED_BOT_WARNING       0x0040
#define LED_LEFT_WARNING      0x0020
#define LED_RIGHT_WARNING     0x0010
#define HEAD_POSITION_WARNING 0x00F0    // head too far from calibr???

#define LED_EXTRA_WARNING     0x0008    // glitch or extra markers
#define LED_MISSING_WARNING   0x0004    // <2 good data points in last 100 msec)
#define HEAD_VELOCITY_WARNING 0x0001    // head moving too fast

#define CALIBRATION_AREA_WARNING 0x0002  // pupil out of good mapping area

#define MATH_ERROR_WARNING   0x2000  // math error in proc. sample

/* THESE CODES ONLY VALID FOR EYELINK II */

            /* 
				this sample interpolated to preserve sample rate
                usually because speed dropped due to missing pupil
			 */
#define INTERP_SAMPLE_WARNING 0x1000
            /* 
				pupil interpolated this sample
				usually means pupil loss or
				500 Hz sample with CR but no pupil
			*/
#define INTERP_PUPIL_WARNING  0x8000

            /* all CR-related errors */
#define CR_WARNING       0x0F00
#define CR_LEFT_WARNING  0x0500
#define CR_RIGHT_WARNING 0x0A00

            /* CR is actually lost */
#define CR_LOST_WARNING        0x0300
#define CR_LOST_LEFT_WARNING   0x0100
#define CR_LOST_RIGHT_WARNING  0x0200

            /* this sample has interpolated/held CR */
#define CR_RECOV_WARNING       0x0C00
#define CR_RECOV_LEFT_WARNING  0x0400
#define CR_RECOV_RIGHT_WARNING 0x0800


#ifdef __cplusplus	/* For C++ compilation */
}
#endif

#endif /* SIMTYPESINCL */
#endif /*__SRRESEARCH__EYE_DATA_H__ */
