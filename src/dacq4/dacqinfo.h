/* title:   dacqinfo.h
** author:  jamie mazer
** created: Wed Jan  6 23:14:57 1999 mazer 
** info:    generic dacq interface structure
** history:
**
** Wed Jan  6 23:15:08 1999 mazer 
**   This is a generalized version of the original das_server.h
**   file.  The idea is to encapsulate a more general purpose
**   driver abstraction, not so directly tied to the das1600's
**   capabilities.  New devices will be able to use the same
**   interface.
**
** Thu Jan  6 11:14:34 2000 mazer
**   added adc_gain & adc_offset support
**
** Tue May 16 20:43:40 2000 mazer 
**   added support for ISCAN via serial input
**
** Sun Mar  9 13:21:02 2003 mazer 
**   Added din_changes[] to DACQINFO structure to act as latches
**   on the digital input lines.
**
** Mon Jan 23 10:01:22 2006 mazer 
**   Added FIXWIN.vbias for vertical elongation of the fixation window.
**
** Thu Apr 13 09:40:47 2006 mazer 
**   eliminated iscan_server specific members from the main data
**   structures.
**
** Tue Nov 28 16:58:07 2006 mazer 
**   added support for a ms-resolution alarm that sends interupts
**   the client/parent process
**  
** Wed Oct 20 15:40:02 2010 mazer 
**   adbuf_t changed from unsigned long -> double
**
** Tue Apr 26 13:03:58 2011 mazer 
**   added support for on-line affine transform matrix
**
*/

#define SHMKEY	0xDA01
#define SEMKEY	0xF0F0

#define NDIGIN	8
#define NDIGOUT	8
#define NADC	4
#define NDAC	2
#define NFIXWIN	1
#define SAMP_RATE 1000		/* sampling rate in Hz */
#define ADBUFLEN ((SAMP_RATE) * 60)
#define MAXSMOOTH 100
#define NJOYBUT	10

/* pseudo-interupt codes */
#define INT_DIN		1
#define INT_FIXWIN	2
#define INT_ALARM	3
#define INT_JOYBUT	4
#define INT_FATAL	666

#include <unistd.h>		/* for pid_t */

typedef struct {
  int active;			/* active or idle flag */
  int xchn, ychn;		/* channels to read */
  int cx, cy;			/* center of window */
  float vbias;			/* vertical elongation factor */
  int rad2;			/* window radius ^ 2 (squared for speed) */
  int state;			/* current state (1 for inside) */
  int broke;			/* latched state */
  long break_time;		/* timestamp for last break */
  int fcount;			/* internal.. */
  int nout;			/* internal.. */
  int genint;			/* generate an SIGUSR2 on break?? */
} FIXWIN;

typedef struct {
  pid_t server_pid;		/* PID of server */
  pid_t pype_pid;		/* PID of pype process */

  /* raw data (input and output) */
  char	din[NDIGIN];		/* status of digital input lines */
  char	din_changes[NDIGIN];	/* # of changes since last reset */
  char  din_intmask[NDIGIN];	/* mask for SIGUSR1 digital inputs */
  char	dout[NDIGOUT];		/* status of digital output lines */
  char	dout_strobe;		/* software strobe (force digital output) */
  char  joyint;			/* joypad buttons generate ints? */

  int	eye_x;			/* current eye position: X position */
  int	eye_y;			/* current eye position: Y position */
  int	eye_pa;			/* current pupil area, if available */
  int   eye_rawx, eye_rawy;	/* raw uncalibrated, unsmoothed eye pos */

  int	adc[NADC];		/* current values for ADC channels */
  int	dac[NDAC];		/* current values for DAC channels */
  int	dac_strobe;		/* software strobe (force DA output) */

  float eye_xgain, eye_ygain;	/* mult. gain for x/y eye position */
  int	eye_xoff, eye_yoff;	/* additive offset in pixels */
  float eye_smooth;		/* length of smoothing kernel (#samps) */
  float eye_affine[3][3];       /* optional affine transform matrix  */
  float eye_rot;		/* final rotation (deg) for x/y eye position */


  /* housekeeping flags */
  unsigned long timestamp;	/* timestamp of last update (ms resolution) */
  int	terminate;		/* set flag to force termination */
  int	das_ready;		/* sync flag -- when true, dacq proc ready */
  int	clock_reset;		/* set to force reset of int. timestamp clock */
  double usts;			/* raw time stamp in us as double */
  double ts0;			/* raw time zero set by timestamp(1) */

  /* used only once.. */
  int	dacq_pri;

  /* d/a buffers */
  unsigned int	adbuf_on;	/* flag to trigger a/d collect */
  unsigned int	adbuf_ptr;	/* current point in ring buffers */
  unsigned int	adbuf_overflow;	/* overflow flag (INDICATES ERROR!!) */

  double	adbuf_t[ADBUFLEN];	/* timestamps (us) */
  int		adbuf_x[ADBUFLEN];	/* eye x position trace */
  int		adbuf_y[ADBUFLEN];	/* eye y position trace */
  int		adbuf_pa[ADBUFLEN];	/* pupil area, if available */
  int		adbuf_new[ADBUFLEN];	/* new data? if sampling rate < 1khz */
  int		adbufs[NADC][ADBUFLEN];

  /* automatic fixation windows */
  FIXWIN fixwin[NFIXWIN];
  int		fixbreak_tau;		/* number of samples outside */
					/* before it counts as a break */

  /* joystick button states (usb joystick) */
  int		js_enabled;
  int		js[NJOYBUT];
  int		js_x;
  int		js_y;


  int		mx, my, mnew;	/* mouse params */

  /* input from external eye tracker: x, y, pupil, new? */
  int		xx, xy, xpa, xnew;

  /* interupt generating elapsed time counter/alarm
   * tracks in ms -- same as timestamp(). 0 for no alarm
   */
  unsigned long		alarm_time;

  /* 'interrupt' classes & arguments */
  int int_class;
  int int_arg;

  int elrestart; // flag to force reconnect to eyelink

} DACQINFO;

/* these are for backwards compatibility: */
// #define adbuf_photo	adbuf_c2
// #define adbuf_spikes	adbuf_c3
