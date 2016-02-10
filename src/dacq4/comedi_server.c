/* title:   comedi_server.c

** author:  jamie mazer
** created: Wed Jan  8 17:21:15 2003 mazer 
** info:    shm interface to COMEDI devices
** history:
**
** Wed Jan  8 17:20:18 2003 mazer 
**   - based on das16_server.c -- this is driver for the COMEDI
**     data acq. library/device-driver kit.  It's GENERIC, designed
**     to work with the ISA & PCI versions of the DAS-1602 card.
**
** Sun Mar  9 13:34:54 2003 mazer 
**   added support for din_changes[] to dig_in()
**
** Wed Nov  3 15:02:41 2004 mazer 
**   added support for the DAS08 board (no 8255!!)
**
** Tue Apr  3 08:37:59 2007 mazer 
**   cleaned up error messages for comedit to make it easier to track
**   down problems with non-DAS/ComputerBoards cards (like NI-6025E).
**
** Tue May  5 15:58:44 2009 mazer 
**   joystick junk moved into separate JS device in das_common.c
**
** Thu Jul 22 12:06:45 2010 mazer 
**   - looks like only das08 now is really pci-das08.. so pci-das08->das08
**   - moreover, looks like driver name changed, so for the best..
**   - also fixed some "signed" to "unsigned" that were probably always wrong..
**
******************************************************************************
**
**  Wed Sep 22 11:59:30 2010 mazer  -- from das_common.c
**
** title:   das_common.c
** author:  jamie mazer
** created: Mon Mar  4 16:41:26 2002 mazer 
** info:    dasXX_server.c common functions
** history:
**
** Thu Apr  4 14:06:25 2002 mazer 
**   - changed calls to setpriority to also bump scheduler priority up to
**	realtime (SCHED_RR)
**
** Fri Aug 23 16:53:54 2002 mazer 
**   - Modified timestamp() to use the RDTSC for speed.  At
**     1 gHz, the 8byte (64bit) counter would overflow in:
**       (2^64) / (1e9) secs = 1.8e10s, or more than 500 years..
**     so, I'm assuming overflow is NOT a problem right now..
**
** Thu Dec 19 14:03:32 2002 mazer 
**   added EYELINK_TEST mode
**
** Wed Apr 16 10:41:16 2003 mazer 
**   added parsing of $XXEYELINK_OPTS to allow setting of eyelink
**   parameters in the pyperc config file...
**
** Sun Nov  6 10:06:36 2005 mazer 
**   added $EYELINK_FILE to save native EDF file during run.
**
** Tue Jan 17 11:37:56 2006 mazer 
**   - added $(CWD)/eyelink.ini file --> supplemental commands for the
**     eyelink
**   - made sure stderr messages all contain progname..
**
** Mon Jan 23 10:01:22 2006 mazer 
**   Added handling of FIXWIN.vbias for vertical elongation of the
**   fixation window.
**
** Fri Mar 10 10:08:25 2006 mazer 
**   Added stub support of a usb joystick or keypad. Right now the
**   device is detected and initialized, but nothing's done yet
**   with the signals.
**
** Thu Apr 13 09:38:38 2006 mazer 
**   merged stand-alone iscan_server code into the main event
**   loop for das_common, so all XXX_server's will be able to
**   talk to the iscan without competition from a separate
**   process.
**
** Thu May 25 11:40:58 2006 mazer 
**   changed z from int to float in mainloop() to avoid overflow
**   errors on (x*x)+(y*y) with ISCAN...
**
** Tue Nov 28 16:58:07 2006 mazer 
**   added support for a ms-resolution alarm that sends interupts
**   the client/parent process
**
** Tue Apr  3 10:39:56 2007 mazer 
**   added support for "-notracker" mode (for acutes)
**
** Fri Jun 15 15:09:05 2007 mazer 
**   added arange (analog input range) for comedi drivers
**
** Thu Dec 18 11:39:36 2008 mazer 
**   - moved eyelink and iscan specific code into separate files
**     that get included here:
**       - iscan.c
**       - eyelink.c
**   - reorganized the mainloop to sample each channel only once
**     and then usleep for a bit to reduce CPU load. original
**     behavior can be restored by #defining SPIN_SAMPLE (which
**     averages over the 1ms interval in a tight loop).
**
** Tue May  5 14:40:33 2009 mazer 
**   - removed EYELINK_TEST mode completely..
**   - changed private XXxxx env vars to XX_xxxx
**
**************************************************************************
** New 'merged' comedi_server notes follow (22-SEP-2010):
**************************************************************************
**
** Wed Sep 22 12:12:25 2010 mazer 
**   - merged das_common.[ch], iscan.c & eyelink.c directly into this
**     file
**  
** Mon Oct 11 15:19:22 2010 mazer 
**   - Changed timestamp to return timestamps in microsecs (us) instead
**     of ms. SHM buffer adbuf_t values are now in us and need to be
**     divided by 1000 to make things compatible.
**
** Fri Oct 15 09:42:32 2010 mazer 
**   - pruned all hidden getenv() args in favor of proper command line arguments
**   
** Wed Oct 20 15:37:43 2010 mazer 
**   - changed timestamp() to return a double instead of an unsigned long
**   - adbuf_t (see dacqinfo.h) also changed to double, along with
**     dacq:dacq_adbuf_t(), which now returns a double instead of an
**     unsigned long
**
** Tue Dec 14 17:24:36 2010 mazer 
**   - upped sleep time from 0.250ms to 0.750ms and added busy wait
**     to enforce 1khz sampling
**
** Wed Dec 22 09:26:06 2010 mazer 
**   - store RAW (unsmoothed) eye position in adbuf_x/y, but use
**     smoothed values for display & fixwins etc..
**
** Wed Mar 16 16:03:58 2011 mazer 
**   - got rid of EYEJOY crap (and changed NONE to 99)
**
** Thu Mar 24 12:42:52 2011 mazer 
**   - pressing buttons 1 and 2 on joystick now sends SIGUSR2 to
**     pype, which should be caught, withdraw the full screen
**     window and stop any run in progress.
**
** Mon Apr  4 12:18:23 2011 mazer 
**   - changed iscan code to accept P-CR (fewer bytes) directly
**     instead of doing subtraction on pype side..
**
** Fri Apr  8 09:17:36 2011 mazer 
**   - added eyenew (adbuf_new[t]) --> this is a boolean indicating
**     whether or not the eye tracker sample is a "new" sample, or
**     propagated from the last time point.
**
** Tue Apr 26 13:03:58 2011 mazer 
**   - added support for on-line affine transform matrix
**
** Fri Aug 26 16:53:00 2011 mazer 
**   - added lastadc_chan to reduce load by not sampling any
**     more channels than necessary.
*/

#include <sys/types.h>
#include <time.h>
#include <sys/time.h>
#include <sys/errno.h>
#include <sys/resource.h>
#include <sys/types.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <string.h>
#include <sys/ipc.h>
#include <sys/shm.h>
#include <sys/mman.h>
#ifndef __APPLE__
# include <sys/io.h>
#endif
#include <signal.h>
#include <math.h>
#include <comedilib.h>
#include <getopt.h>

#define __USE_GNU 1
#include <sched.h>		/* need __USE_GNU=1 to get CPU_* macros */

#include <ezV24/ezV24.h>	/* for iscan serial I/O  */
#include <eyelink.h>		/* eyelink API  */
#include <eyetypes.h>		/* more eyelink API stuff */
#include <core_expt.h>	/* my_... works with both 32bit & 64bit libs */

#include "dacqinfo.h"
#include "sigs.h"
#include "psems.h"
#include "usbjs.h"
#include "debug.h"

#define ANALOG		0	/* eye tracker mode flags */
#define ISCAN		1
#define EYELINK		2
#define NONE		99

#define INSIDE		1	/* fixwin status flags */
#define OUTSIDE		0

#define ISCAN_NODATA    99999

/* convert float to int with proper rounding: */
#define F2I(f)	((int)((f) >= 0 ? ((f)+0.5) : ((f)-0.5)))

static char	*progname = NULL;
static DACQINFO *dacq_data = NULL;
static int	mem_locked = 0;
static int	gotdacq = 0;
static int	semid;
static double	arange;
static int	das08 = 0;	/* board is das08? (was pci-das08)*/
static char	*comedi_devname = "/dev/comedi0";
static comedi_t *comedi_dev;	/* main handle to comedi lib */
static int	analog_in = -1;	/* subdevice for analog input */
static int	use8255;	/* 0 for ISA, 1 for PCI */
static int	dig_io = -1;	/* combined digital I/O subdevice */
static int	dig_i = -1;	/* digital IN only subdevice (ISA) */
static int	dig_o = -1;	/* digital OUT only subdevice (ISA)*/
static int	analog_range;
static int	itracker = NONE;
static int	semid = -1;
static int	swap_xy = 0;
static int	iscan_x, iscan_y, iscan_p, iscan_new;
static double	arange = 10.0;

static int	usbjs_dev = -1;	/* usb joystick handle */
static int	eyelink_camera = -1;  /* eyelink handle */
static v24_port_t *iscan_port = NULL;	/* iscan handle */

static int	debugint = 0;

static pid_t	pypepid = 0;


// command line args; these used to be private to main, but
// changed to global to allow restarts on the fly
static char *elopts = NULL;
static char *elcam = NULL;
static char *port = NULL;
static char *tracker = "none";
static char *usbjs = NULL;


#define ERROR(s) perror2(s, __FILE__, __LINE__)

void perror2(char *s, char *file, int line)
{
  char *p = (char *)malloc(strlen(progname)+strlen(s)+25);

  sprintf(p, "%s (file=%s, line=%d):%s", progname, file, line, s);
  perror(p);
  free(p);
}

void iscan_halt()
{
  if (iscan_port) {
    v24ClosePort(iscan_port);
    fprintf(stderr, "%s: closed iscan_port\n", progname);
  }
}

#ifdef PYPE_INTERNAL_CR
// 2 bytes/param * 4 param/packet ==> 4 bytes/packet (P, CR, P, CR)
# define ISCAN_PACKETLEN 6
#else
// 2 bytes/param * 2 param/packet ==> 4 bytes/packet (P-CR, P-CR)
# define ISCAN_PACKETLEN 4
#endif

int iscan_read()
{
  static unsigned char buf[6];
  static short *ibuf = NULL;
  int n, k, c;

  if (ibuf == NULL) {
    for (n = 0; n < sizeof(buf); n++) { buf[n] = 0; }
    ibuf = (short *)buf;
    iscan_x = ISCAN_NODATA;
    iscan_y = ISCAN_NODATA;
    iscan_p = 0;
    iscan_new = 0;
  }

  if ((c = v24Getc(iscan_port)) < 0) {
    // no data available
    return(0);
  }
  // shift buffer down and insert new data at end
  for (k = 0; k < 5; k++) {
    buf[k] = buf[k+1];
  }
  buf[5] = 0x00ff & c;

  // buffer ready to read? --> not this assumes X, Y only and P-CR
  if (buf[0] == 'D' && buf[1] == 'D') {
    iscan_x = ibuf[1] + 128; /* 128 gets things centered ~0 */
    iscan_y = (2*ibuf[2]) + 128;
    iscan_new = 1;
    if (iscan_x == 128 || iscan_y == 128) {
      // lost signal (0,0), probably blink..
      iscan_x = ISCAN_NODATA;
      iscan_y = ISCAN_NODATA;
      iscan_p = 0;
    } else {
      iscan_p = 1000;
    }
  }
  return(1);
}

int OLD_iscan_read()
{
  static unsigned char buf[25];
  static int c, bp = -1;
  static short *ibuf;
  static int lastc = -1;
  static int first_time = 1;
  static int first_fail = 1;

  /* initialize the read buffer */
  if (bp < 0) {
    for (bp = 0; bp < sizeof(buf); bp++) {
      buf[bp] = 0;
    }
    bp = -1;
    ibuf = (short *)buf;
    iscan_x = ISCAN_NODATA;
    iscan_y = ISCAN_NODATA;
    iscan_p = 0;
    iscan_new = 0;
  }

  if ((c = v24Getc(iscan_port)) < 0) {
    if (first_fail) {
      fprintf(stderr, "%s: warning can't read iscan (check baudrate!)\n",
	      progname);
      first_fail = 0;
    }
    return(0);
  }

  // each packet begins with a 'DD', wait to get two D's in a row
  if (c == 'D') {
    if (lastc == 'D') {
      lastc = -1;
      bp = 0;
    } else {
      lastc = c;
    }
    if (first_time) {
      first_time = 1;
      fprintf(stderr, "%s: iscan synced up!\n", progname);
      first_time = 0;
    }
    return(1);
  }
  // char is part of the data payload
  if (bp >= 0) {
    buf[bp] = 0x00ff & c;
    if (bp == (ISCAN_PACKETLEN - 1)) {
      // payload is complete -- packet ends

      // Thu Apr 28 11:16:30 2011 mazer 
      // originally PUPIL and CR data were collected independently
      // and 0's indicated pupil lock lost, this isn't the case
      // for PUP-CR mode.. there's kind of a potential problem here,
      // in that you can't really tell when the track's lost. But
      // we'd rather have 120hz data for psychophysics..
      //
      // Actually, there's a slight problem -- even int PUP-CR mode,
      // the tracker returns a 0,0 when signal lock is lost. Technically
      // this means that looking at 0,0's not possible..

#ifdef PYPE_INTERNAL_CR
      if (ibuf[0] || ibuf[1]) {
        // 2+8 bytes from iscan:  <PUP_H1,CR_H1,PUP_V1,CR_V1>
	iscan_x = ibuf[0] - ibuf[2] + 4096;
	iscan_y = ibuf[1] - ibuf[3] + 4096;
	iscan_p = 1000;
	iscan_new = 1;
	return(1);
      } else {
	iscan_x = ISCAN_NODATA;	// out of range or no pupil lock
	iscan_y = ISCAN_NODATA;
	iscan_p = 0;
	iscan_new = 1;
	return(1);
      }
#else
      if (ibuf[0] && ibuf[1]) {
	// 2+4 bytes from iscan: <PUP_H1-CR,PUP_V1-CR>  (better 120hz perf)
	iscan_x = ibuf[0] + 128; /* 128 gets things centered ~0 */
	iscan_y = (2*ibuf[1]) + 128;
	iscan_p = 1000;
	iscan_new = 1;
	return(1);
      } else {
	// both params are 0 means tracking/lock lost..
	iscan_x = ISCAN_NODATA;
	iscan_y = ISCAN_NODATA;
	iscan_p = 0;
	iscan_new = 1;
	return(1);
      }
#endif
    } else {
      if (++bp > (ISCAN_PACKETLEN - 1)) {
	fprintf(stderr, "iscan packet overrun, reseting.\n");
      }
    }
  }
  return(1);
}

void eyelink_init(char *ip_address, char *el_opts, char *el_cam)
{
  char *p, *q, buf[100];
  extern char *__progname;
  char *saved;
  FILE *fp;
  

  fprintf(stderr, "%s: eyelink_init trying %s\n", progname, ip_address);

  saved = malloc(strlen(__progname) + 1);
  strcpy(saved, __progname);

  //begin_realtime_mode();
  set_eyelink_address(ip_address);
  
  if (open_eyelink_connection(0)) {
    fprintf(stderr, "\n%s eyelink_init can't open connection to tracker\n",
	    progname);
    return;
  }
  set_offline_mode();

  /* 16-apr-2003: step through the XX_EYELINK_OPTS env var (commands
   * separated by :'s) and set each command to the eyelink, while
   * echoing to the console..  This variable is setup by pype before
   * dacq_start() gets called..
   */
  if (el_opts != NULL) {
    for (q = p = el_opts; *p; p++) {
      if (*p == ':') {
	*p = 0;
	eyecmd_printf(q);
	fprintf(stderr, "%s: eyelink_opt=<%s>\n", progname, q);
	*p = ':';
	q = p + 1;
      }
    }
  }

  /* this should be "0" or "1", default to 1 */
  if (el_cam == NULL || sscanf(el_cam, "%d", &eyelink_camera) != 1) {
    eyelink_camera = 1;
  }
  sprintf(buf, "eyelink_camera = %d", eyelink_camera);
  fprintf(stderr, "%s: %s\n", progname, buf);
  eyecmd_printf(buf);

  /* Tue Jan 17 11:37:48 2006 mazer 
   * if file "eyelink.ini" exists in the current directory, send
   * it as a series of commands to the eyelink over the network.
   */

  if ((fp = fopen("eyelink.ini", "r")) != NULL) {
    while (fgets(buf, sizeof(buf), fp) != NULL) {
      if ((p = index(buf, '\n')) != NULL) {
	*p = 0;
      }
      fprintf(stderr, "%s: %s\n", progname, buf);
      eyecmd_printf(buf);
    }
  }

  // start recording eyelink data
  // tell eyelink to send samples, but not 'events' through link
  if (start_recording(0,0,1,0)) {
    fprintf(stderr, "%s eyelink_init can't start recording\n", progname);
    return;
  }

  if (eyelink_wait_for_block_start(10,1,0)==0) {
    fprintf(stderr, "%s eyelink_init can't get block start\n", progname);
    return;
  }

  fprintf(stderr, "%s eyelink_init connected ok\n", progname);
  itracker = EYELINK;
}

void eyelink_halt()
{
  if (itracker == EYELINK) {
    stop_recording();
    set_offline_mode();
    close_eyelink_connection();
    fprintf(stderr, "%s: closed eyelink connection\n", progname);
    itracker = NONE;
  }
}

int eyelink_read(float *x, float *y,  float *p,
		 unsigned int *t, int *new)
{
  static FSAMPLE sbuf;
  int e;

  if (! eyelink_is_connected()) {
    // send parent process an interupt..
    eyelink_halt();
    fprintf(stderr, "%s: warning, lost eyelink connection\n", progname);
    dacq_data->int_class = INT_FATAL;
    dacq_data->int_arg = 1;
    kill(pypepid, SIGUSR1);
  }

  if ((e = eyelink_newest_float_sample(&sbuf)) < 0) {
    return(0);
  } else {
    /* there are new data about eye positions */
    *t = (unsigned int) sbuf.time;
    *x = sbuf.px[eyelink_camera];		/* xpos, RIGHT/LEFT */
    *y = sbuf.py[eyelink_camera];		/* ypos, RIGHT/LEFT */
    *p = sbuf.pa[eyelink_camera];		/* pupil area, RIGHT/LEFT */
    *new = (e == 1);
    return(1);
  }
}

// for cards with 8255 digital i/o (autodetectged), we have banks
// A,B and C and we want bank A (0-7) for input and B (8-15) for output.
#define BANK_A          0
#define BANK_B          8
#define PCI_NOWRITEMASK 0
#define PCI_READMASK    (1+2+4+8+16+32+64+128)
#define PCI_WRITEMASK   (1+2+4+8+16+32+64+128)<<BANK_B

// for the ISA cards, we have 4 bits of digital input and 4 of output
#define ISA_NOWRITEMASK	0
#define ISA_WRITEMASK	(1+2+4+8)

int comedi_init()
{
  const char *devname;
  comedi_range *r;
  int n;

  if (!(comedi_dev = comedi_open(comedi_devname))) {
    fprintf(stderr, "%s: can't find comedi board.\n", progname);
    return(0);
  }
  devname = comedi_get_driver_name(comedi_dev);
  
  fprintf(stderr, "%s: found DAQ device board=<%s> driver=<%s>\n",
	  progname, comedi_get_board_name(comedi_dev), devname);

  if (strncmp(devname, "das16", 5) == 0) {
    fprintf(stderr, "%s: 8255 disabled.\n", progname);
    use8255 = 0;
  } else if (strncmp(devname, "das08", 5) == 0 ||
	     strncmp(devname, "pci-das08", 9) == 0) {
    use8255 = 0;
    das08 = 1;
    fprintf(stderr, "%s: 8255 disabled.\n", progname);
    fprintf(stderr, "%s: detected das08 -- using comedi_data_read_delayed\n",
	    progname);
  } else {
    fprintf(stderr, "%s: 8255 enabled.\n", progname);
    use8255 = 1;
  }

  // find which comedi subdevices correspond the the facilities we need
  analog_in  = comedi_find_subdevice_by_type(comedi_dev,COMEDI_SUBD_AI,0);
  if (analog_in == -1) {
    comedi_perror("analog_in");
  } else {
    fprintf(stderr, "%s: analog input OK\n", progname);
  }

  n = comedi_get_n_channels(comedi_dev, analog_in);
  fprintf(stderr, "%s: %d analog inputs available.\n", progname, n);
  n = comedi_get_n_ranges(comedi_dev, analog_in, 0);
  fprintf(stderr, "%s: %d analog ranges available.\n", progname, n);
  if (n > 1) {
    // try to find the +/- 10V range.  the 4th parm means 'volts'.
    // BW: I THINK THIS ASSUMES ALL CHANNELS ARE THE SAME
    //analog_range = comedi_find_range(comedi_dev,analog_in,0,0,-10,10);
    analog_range = comedi_find_range(comedi_dev,analog_in,0,0,-arange,arange);
    if (analog_range == -1) {
      comedi_perror("analog_range");
    }
  } else {
    // DAS08 doesn't have programmable ranges -- use 0
    analog_range = 0;
  }
  r = comedi_get_range(comedi_dev, analog_in, 0, analog_range);
  fprintf(stderr, "%s: analog range (%.1f%s)-(%.1f%s)\n", progname,
	  r->min, (r->unit==UNIT_volt) ? "V" : "??",
	  r->max, (r->unit==UNIT_volt) ? "V" : "??");

  if (use8255) {
    dig_io = comedi_find_subdevice_by_type(comedi_dev,COMEDI_SUBD_DIO,0);
    if (dig_io == -1) {
      comedi_perror("dig_io");
    } else {
      fprintf(stderr, "%s: digital IO OK\n", progname);
      dig_i = -1;
      dig_o = -1;
    }
  } else {
    dig_i  = comedi_find_subdevice_by_type(comedi_dev,COMEDI_SUBD_DI,0);
    if (dig_i == -1) {
      comedi_perror("dig_i");
    } else {
      fprintf(stderr, "%s: digital input OK\n", progname);
    }
    dig_o = comedi_find_subdevice_by_type(comedi_dev,COMEDI_SUBD_DO,0);
    if (dig_o == -1) {
      comedi_perror("dig_o");
    } else {
      fprintf(stderr, "%s: digital output OK\n", progname);
    }
  }

  if (use8255) {
    // configure digital I/O bank A as input, and bank B as output
    if (comedi_dio_config(comedi_dev,dig_io,BANK_A,COMEDI_INPUT) &&
	comedi_dio_config(comedi_dev,dig_io,BANK_B,COMEDI_OUTPUT)) {
      return(1);
    } else {
      return(0);
    }
  }
  return(1);
}

int ad_in(int chan)
{
  lsampl_t sample;
  int success;

  if (gotdacq) {
    return(0);
  } else {
    // need to set aref correctly: either AREF_GROUND or AREF_COMMON
    if (das08) {
      // das08 is screwy -- needs time for multiplexer to settle:
      success = comedi_data_read_delayed(comedi_dev,analog_in,
					 chan,analog_range,AREF_GROUND,
					 &sample, 0);
      if (success < 0) {
	comedi_perror("comedi_data_read_delayed");
      }
    } else {
      success = comedi_data_read(comedi_dev,analog_in,
				 chan,analog_range,AREF_GROUND,
				 &sample);
      if (success < 0) {
	comedi_perror("comedi_data_read");
      }
    }
    // note: lsampl is an unsigned int; we are casting to int. it won't
    // matter for 12 bit cards
    return((int)sample);
  }
}

void dig_in()
{
  int i, last;
  unsigned int bits;

  if (gotdacq) {
    // just lock these down -- polarities are
    // from the old taks -- hardcoded to work in NAF...
    LOCK(semid);
    dacq_data->din[0] = 0;	/* monkey bar NOT down */
    dacq_data->din[2] = 1;	/* user button 2 NOT down */
    dacq_data->din[3] = 1;	/* user button 1 NOT down */
    UNLOCK(semid);
  } else {
    if (use8255) {
      comedi_dio_bitfield(comedi_dev,dig_io,PCI_NOWRITEMASK,&bits);
      bits = bits & PCI_READMASK;
    } else {
      comedi_dio_bitfield(comedi_dev,dig_i,ISA_NOWRITEMASK,&bits);
    }
    /* unpack inp word into the first 8 slots of the dacq struct's din array */
    for (i = 0; i < 4; i++) {
      LOCK(semid);
      last = dacq_data->din[i];
      dacq_data->din[i] = ((bits & 1<<i) != 0);
      if (dacq_data->din[i] != last) {
	dacq_data->din_changes[i] += 1;
	if (dacq_data->din_intmask[i]) {
	  dacq_data->int_class = INT_DIN;
	  dacq_data->int_arg = i;
	  kill(pypepid, SIGUSR1);
	}
      }
      UNLOCK(semid);
    }
  }
}

void dig_out()
{
  unsigned int bits = 0;
  int i;

  if (gotdacq) {
    return;
  } else {
    for (i = 0; i < 8 && i < NDIGOUT; i++) {
      LOCK(semid);
      bits = bits | (dacq_data->dout[i] << i);
      UNLOCK(semid);
    }
    if (use8255) {
      bits = bits<<BANK_B;
      comedi_dio_bitfield(comedi_dev,dig_io,PCI_WRITEMASK,&bits);
    } else {
      comedi_dio_bitfield(comedi_dev,dig_o,ISA_WRITEMASK,&bits);
    }
  }
}

static void sigusr2_handler(int signum)
{
  debugint = 1;
}

int mainloop_init()
{
  int shmid;

  if (comedi_init()) {
    gotdacq = 0;
    fprintf(stderr, "%s: comedi initialized.\n", progname);
  } else {
    fprintf(stderr, "%s: no dacq mode.\n", progname);
    gotdacq = 1;
  }

  if (dig_io >= 0) {
    fprintf(stderr, "%s: dig_io=subdev #%d\n", progname, dig_io);
  }
  if (dig_i >= 0) {
    fprintf(stderr, "%s: dig_i=subdev #%d\n", progname, dig_i);
  }
  if (dig_o >= 0) {
    fprintf(stderr, "%s: dig_o=subdev #%d\n", progname, dig_o);
  }
  if (analog_in >= 0) {
    fprintf(stderr, "%s: analog_in=subdev #%d\n", progname, analog_in);
  }

  if ((shmid = shmget((key_t)SHMKEY,
		      sizeof(DACQINFO), 0666 | IPC_CREAT)) < 0) {
    ERROR("shmget");
    fprintf(stderr, "%s:init -- kernel compiled with SHM/IPC?\n", progname);
    exit(1);
  }

  if ((dacq_data = shmat(shmid, NULL, 0)) == NULL) {
    ERROR("shmat");
    fprintf(stderr, "%s:init -- kernel compiled with SHM/IPC?\n", progname);
    exit(1);
  }

  if (mlockall(MCL_CURRENT) == 0) {
    mem_locked = 1;
  } else {
    ERROR("mlockall");
    fprintf(stderr, "%s:init -- failed to lock memory\n", progname);
  }
  LOCK(semid);
  dacq_data->elrestart = 0;
  dacq_data->server_pid = getpid();
  if (dacq_data->dacq_pri != 0) {
    if (nice(dacq_data->dacq_pri) == 0) {
      fprintf(stderr, "%s:init -- bumped priority %d\n",
	      progname, dacq_data->dacq_pri);
    } else {
      ERROR("nice");
      fprintf(stderr, "%s:init -- failed to change priority\n", progname);
    }
  }
  UNLOCK(semid);

  signal(SIGUSR2, sigusr2_handler); /* catch SIGUSR2's from pype (debugging) */

  return(1);
}


/* from das_common.c */

void iscan_init(char *dev)
{
  if ((iscan_port = v24OpenPort(dev, V24_NO_DELAY | V24_NON_BLOCK)) == NULL) {
    fprintf(stderr, "%s: iscan_init can't open \"%s\"\n.", progname, dev);
    exit(1);
  }
  v24SetParameters(iscan_port, V24_B115200, V24_8BIT, V24_NONE);

  itracker = ISCAN;
  fprintf(stderr, "%s: opened iscan_port (%s)\n", progname, dev);
}

double timestamp(int init) /* return elapsed time in us */
{
  static struct timespec ti[2];	/* initial and current times */
  static double ts;

  if (init) {
    clock_gettime(CLOCK_MONOTONIC, &ti[0]);
    LOCK(semid);
    dacq_data->ts0 = ti[0].tv_sec + ti[0].tv_nsec * 1e-9;
    UNLOCK(semid);
  }
  clock_gettime(CLOCK_MONOTONIC, &ti[1]);
  ts = (1.0e6 * (double)(ti[1].tv_sec - ti[0].tv_sec)) +
    (1.0e-3 * (double)(ti[1].tv_nsec - ti[0].tv_nsec));
  return(ts);
}

static int locktocore(int corenum) /* -1 for no lock; else corenum (0,1..) */
{
  /* 0 for first core etc.. -1 for no lock */
  cpu_set_t mask;
  int result = 1;

  if (corenum >= 0) {
    CPU_ZERO(&mask);
    CPU_SET(corenum, &mask);
    result = sched_setaffinity(0, sizeof(mask), &mask);
    if (result < 0) {
      return(-1);
    } else {
      return(corenum);
    }
  }
  return(-1);
}

void resched(int rt)
{
#ifdef ALLOW_RESCHED
  struct sched_param p;

  /* change scheduler priority from OTHER to RealTime/RR or vice versa */

  if (sched_getparam(0, &p) >= 0) {
    if (rt) {
      p.sched_priority = SCHED_RR;
      sched_setscheduler(0, SCHED_RR, &p);
    } else {
      p.sched_priority = SCHED_OTHER;
      sched_setscheduler(0, SCHED_OTHER, &p);
    }
  }
#endif
}

#define A(r,c) (dacq_data->eye_affine[(r)-1][(c)-1])

void mainloop(void)
{
  int i, ii, k, lastpri, setpri, last, eyenew, button;
  int firstadc_chan, lastadc_chan;
  float rx, ry, lsx, lsy, x, y, z, pa, tx, ty, tp;
  unsigned int eyelink_t;
  int jsbut, jsnum, jsval;
  unsigned long jstime;
  float sumx, sumy;
  int si, sumn;
  float sbx[MAXSMOOTH], sby[MAXSMOOTH];
  double usts, last_usts;
  unsigned long msts, last_parent_check = 0;
  int ncores;
  pid_t pypeid;

  x = y = pa = -1.0;
  eyenew = sumx = sumy = 0;
  lsx = lsy = y = x = 0.0;
  for (si = 0; si < MAXSMOOTH; si++) {
    sbx[si] = sby[si] = 0.0;
  }
  si = 0;

  LOCK(semid);
  k = dacq_data->dacq_pri;
  UNLOCK(semid);

  errno = 0;
  if (setpriority(PRIO_PROCESS, 0, k) == 0 && errno == 0) {
    fprintf(stderr, "%s: bumped priority %d\n", progname, k);
    lastpri = k;
    if (lastpri < 0) {
      resched(1);
    }
    setpri = 1;
  } else {
    fprintf(stderr, "%s: failed to change priority\n", progname);
    setpri = 0;
    lastpri = 0;
  }

  ncores = sysconf(_SC_NPROCESSORS_ONLN);
  if (ncores > 1 && locktocore(ncores - 1) >= 0) { 
    fprintf(stderr, "%s: %d cores; locked to %d\n",
	    progname, ncores, ncores - 1);
  }
  timestamp(1);			/* initialize timestamp counter to 0 */
  last_usts = -1.0;

  // Mon May  2 14:40:11 2011 mazer 
  // If eyetrack info is analog, then sample channels 0 & 1, otherwise,
  // these channels are not used and are filled with the raw data from
  // the external tracking devices (via network, serial port etc)
  
  firstadc_chan = itracker == ANALOG ? 0 : 2;
  lastadc_chan = 3;

  fprintf(stderr, "%s: %.1f kHz sampling\n", progname, SAMP_RATE / 1000.0);

  /* signal client we're ready */
  LOCK(semid);
  dacq_data->das_ready = 1;
  pypeid = dacq_data->pype_pid;
  UNLOCK(semid);
  fprintf(stderr, "%s: ready\n", progname);

  do {

    if (debugint) {
      // this chunk of code can be used for one-shots triggered by SIGUSR2
      int r, c;
      for (r = 1; r < 4; r++) {
	for (c = 1; c < 4; c++) {
	  printf("%10f [%d%d] ", A(r,c), r, c);
	}
	printf("\n");
      }
      printf("xg=%10f\n", dacq_data->eye_xgain);
      printf("yg=%10f\n", dacq_data->eye_ygain);
      printf("xo=%10d\n", dacq_data->eye_xoff);
      printf("yo=%10d\n", dacq_data->eye_yoff);
      debugint = 0;
    }
    LOCK(semid);
    if (dacq_data->clock_reset) {
      // this is basically a one-shot; client sets clock_reset to
      // force clock reset on next iteration through mainloop
      timestamp(1);
      UNLOCK(semid);
      dacq_data->clock_reset = 0;
      LOCK(semid);
      last_usts = -1.0;
    }
    //fprintf(stderr, "test: ready=%d\n", dacq_data->das_ready);
    UNLOCK(semid);

    while (1) {
      usts = timestamp(0);
      if (last_usts < 0 || (usts - last_usts) > (1.0e6 / SAMP_RATE)) {
	last_usts = usts;
	break;
      }
    }
    msts = (unsigned long) (0.5 + usts / 1000.0);

    // exit automatically if parent dies -- check 1/sec
    if (last_parent_check && (msts-last_parent_check) > 1000 && 
	kill(pypeid, 0) < 0) {
      fprintf(stderr, "%s: parent gone, exiting!\n", progname);
      break;
    } else {
      last_parent_check = msts;
    }
    
    for (i=firstadc_chan; i<=lastadc_chan; i++) {
      // sample all (in-use) converters fast as possible
      dacq_data->adc[i] = ad_in(i);
    }
    if (itracker == ISCAN) {	// maybe read iscan from serial port..
      while (iscan_read()) {
	/* read until nothing available -- drain buffers each time */
	;
      }
    }
    if (usbjs_dev > 0) {	// joystick, only if enabled
      if (usbjs_query(usbjs_dev, &jsbut, &jsnum, &jsval, &jstime)) {
	if (jsbut && jsnum < NJOYBUT) {
	  LOCK(semid);
	  dacq_data->js[jsnum] = jsval; // button # jsnum: up or down?
	  UNLOCK(semid);
	} else if (jsbut == 0 && jsnum == 0) {
	  dacq_data->js_x = jsval; // x motion; jsval=current position */
	} else if (jsbut == 0 && jsnum == 1) {
	  dacq_data->js_y = jsval; // y motion; jsval=current position */
	}
      }
    }

    // try to reconnect to eyelink
    if (dacq_data->elrestart) {
      dacq_data->elrestart = 0;
      // only allow resets if initial connection was eyelink and
      // no longer currently connected (analog fallback mode)
      if (port != NULL && itracker == NONE) {
	fprintf(stderr, "%s: trying to reconnect to eyelink\n", progname);
	eyelink_init(port, elopts, elcam);
      }
    }

    switch (itracker)
      {
      case ISCAN:
	x = iscan_x;
	y = iscan_y;
	pa = iscan_p;
	eyenew = iscan_new;
	iscan_new = 0;
	dacq_data->adc[0] = x;
	dacq_data->adc[1] = y;
	break;
      case EYELINK:
	if (eyelink_read(&tx, &ty, &tp, &eyelink_t, &eyenew) != 0) {
	  x = tx;
	  y = ty;
	  pa = tp;
	} else {
	  eyenew = 0;
	}
	dacq_data->adc[0] = x;
	dacq_data->adc[1] = y;
	break;
      case ANALOG:
	x = dacq_data->adc[0];
	y = dacq_data->adc[1];
	pa = -1;
	eyenew = 1;
	break;
      default:
	/* This is for any sort of tracker that will inject it's data
	 * stream into data_data->xx,xy,xpa,xnew directly via SHM.
	 * In general, this means something running in a thread in the
	 * parent process.. mouse, usb tracker etc..
	 */
	dacq_data->adc[0] = x = dacq_data->xx;
	dacq_data->adc[1] = y = dacq_data->xy;
	pa = dacq_data->xpa;
	eyenew = dacq_data->xnew;
	dacq_data->xnew = 0;
	break;
      }

    if (swap_xy) {
      int tmp;

      tmp = x;
      x = y;
      y = tmp;

      // this was missing, which broke eyecal when swap_xy was set..

      tmp = dacq_data->adc[0];
      dacq_data->adc[0] = dacq_data->adc[1];
      tmp = dacq_data->adc[1] = tmp;
    }

    if (itracker != ISCAN || x != ISCAN_NODATA || y != ISCAN_NODATA) {
      /* IMPORTANT -- eye calibration is performed in a specific
       * order: affine -> gain -> offset -> rotation.  Idealy, you
       * should NEVER use rotation, since affine's can to everything,
       * including rotation. But sometimes it's handy to be able to
       * quickly do both.
       */

      // 1st: apply unwrapped matrix multiply for applying affine transform
      rx = (x * A(1,1)) + (y * A(2,1)) + (1.0 * A(3,1));
      ry = (x * A(1,2)) + (y * A(2,2)) + (1.0 * A(3,2));

      LOCK(semid);

      // 2nd: apply gain/offset
      x = (dacq_data->eye_xgain * rx) + dacq_data->eye_xoff;
      y = (dacq_data->eye_ygain * ry) + dacq_data->eye_yoff;

      // 3rd: apply supplemental rotation for ACM..
      if (dacq_data->eye_rot != 0) {
	float r,th;
	r = hypot(x, y);
	th = atan2(y, x) - (M_PI * dacq_data->eye_rot / 180.);
	x = r * cos(th);
	y = r * sin(th);
      }
    } else {
      // pass through iscan out of bounds signal unchanged..
      LOCK(semid);
    }

    // stash these before they get changed..
    dacq_data->eye_rawx = F2I(x);
    dacq_data->eye_rawy = F2I(y);

    rx = x;
    ry = y;
    if ((sumn = dacq_data->eye_smooth) > MAXSMOOTH) {
      sumn = MAXSMOOTH;
    }

    if (sumn > 1) {
      // apply sumn-point running average
      if (eyenew && 
	  (itracker != ISCAN || x != ISCAN_NODATA || y != ISCAN_NODATA)) {
	// if eye data is new and not out of bounds, then include it in
	// the smoothing buffer and generate the next smoothed point.
	UNLOCK(semid);
	sumx += -sbx[si] + x;	/* pop */
	sumy += -sby[si] + y;
	sbx[si] = x;		/* push */
	sby[si] = y;
	si = (si + 1) % sumn;	/* advance pointer */
	lsx = x = sumx / sumn;		/* compute smoothed mean */
	lsy = y = sumy / sumn;
	LOCK(semid);
      } else {
	// Otherwise, just use the last smooth value available.
      	x = lsx; y = lsy;
      }
    }
    // current position is smoothed position, but we're going to
    // store unsmoothed raw position in the eyebuf arrays
    dacq_data->eye_x = F2I(x);
    dacq_data->eye_y = F2I(y);
    dacq_data->eye_pa = pa;
    UNLOCK(semid);
    
    /* read digital input lines */
    if (usbjs_dev >= 0) {
#ifdef EMERG_QUIT
      if (dacq_data->js[0] && dacq_data->js[1]) {
	kill(pypepid, SIGUSR2);
      }
#endif
      /*
       * Make joystick button 1 acts as bar (DIN#0); other buttons should
       * be read using dacq_jsbut() API function.
       */
      LOCK(semid);
      last = dacq_data->din[0];
      dacq_data->din[0] = dacq_data->js[0];
      if (dacq_data->din[0] != last) {
	dacq_data->din_changes[0] += 1;
	if (dacq_data->din_intmask[0]) {
	  dacq_data->int_class = INT_DIN;
	  dacq_data->int_arg = 0;
	  kill(pypepid, SIGUSR1);
	}
      }
      UNLOCK(semid);

      /* other buttons generate ints only if joyint is set: */
      for (button = 1; dacq_data->joyint && button < NJOYBUT; button++) {
	if (dacq_data->js[button]) {
	  dacq_data->joyint = 0;		/* force manual reset! */
	  dacq_data->int_class = INT_JOYBUT;
	  dacq_data->int_arg = button;
	  kill(pypepid, SIGUSR1);
	}
      }
    } else {
      /* otherwise, fall back to comedi DIO lines etc */
      dig_in();
    }

    /* set digital output lines, only if the strobe's been set */
    LOCK(semid);
    k = dacq_data->dout_strobe;
    UNLOCK(semid);
    if (k) {
      dig_out();
      /* reset the strobe (as if it were a latch */
      LOCK(semid);
      dacq_data->dout_strobe = 0;
      UNLOCK(semid);
    }

    LOCK(semid);
    dacq_data->timestamp = msts; /* in 'ms' (for backwards compat) */
    dacq_data->usts = usts;	 /* us */

    /* check alarm status */
    if (dacq_data->alarm_time && 
	(dacq_data->timestamp >= dacq_data->alarm_time)) {
      // alarm set and expired -- clear and send interupt to pype
      dacq_data->alarm_time = 0;
      dacq_data->int_class = INT_ALARM;
      dacq_data->int_arg = 0;
      kill(pypepid, SIGUSR1);
    }
    k = dacq_data->adbuf_on;
    UNLOCK(semid);

    if (k) {
      LOCK(semid);
      k = dacq_data->adbuf_ptr;
      dacq_data->adbuf_t[k] = usts;
      dacq_data->adbuf_x[k] = rx; /* raw (unsmoothed) x pos */
      dacq_data->adbuf_y[k] = ry; /* raw (unsmoothed) y pos */
      dacq_data->adbuf_pa[k] = dacq_data->eye_pa;
      dacq_data->adbuf_new[k] = eyenew;

      // start at 0 (instead of first_adcchan) because raw x,y is
      // always stored in channels 0,1
      for (ii=0; ii <= lastadc_chan; ii++) {
	dacq_data->adbufs[ii][k] = dacq_data->adc[ii];
      }
      if (++dacq_data->adbuf_ptr > ADBUFLEN) {
	dacq_data->adbuf_overflow++;
	dacq_data->adbuf_ptr = 0;
      }
      UNLOCK(semid);
    }

    /* check fixwins for in/out events */
    for (i = 0; i < NFIXWIN; i++) {
      LOCK(semid);
      k = dacq_data->fixwin[i].active;
      UNLOCK(semid);
      if (k) {
	float dx, dy;
	LOCK(semid);
	dx = dacq_data->eye_x - dacq_data->fixwin[i].cx;
	dy = (dacq_data->eye_y - dacq_data->fixwin[i].cy) /
	  dacq_data->fixwin[i].vbias;
	UNLOCK(semid);
	
	z = (dx * dx) + (dy * dy);
	
	LOCK(semid);
	if (z < dacq_data->fixwin[i].rad2) {
	  // eye in fixwin -- stop counting transient breaks
	  dacq_data->fixwin[i].state = INSIDE;
	  dacq_data->fixwin[i].fcount = 0;
	} else {
	  // eye outside fixwin -- could be shot noise.
	  if (dacq_data->fixwin[i].state == INSIDE) {
	    // eye was inside last time, so recent fixbreak -- reset
	    // timer and start timing period outside
	    dacq_data->fixwin[i].fcount = 1;
	    dacq_data->fixwin[i].nout = 0;
	  }
	  dacq_data->fixwin[i].state = OUTSIDE;
	  if (dacq_data->fixwin[i].fcount) {
	    dacq_data->fixwin[i].nout += 1;
	    if (dacq_data->fixwin[i].nout > dacq_data->fixbreak_tau) {
	      // # samps outside exceeds fixbreak_tau --> real fixbreak!
	      if (dacq_data->fixwin[i].broke == 0) {
		// save break time
		dacq_data->fixwin[i].break_time =  dacq_data->timestamp;
	      }
	      dacq_data->fixwin[i].broke = 1;
	      if (dacq_data->fixwin[i].genint) {
		// alert parent process
		dacq_data->int_class = INT_FIXWIN;
		dacq_data->int_arg = 0;
		dacq_data->fixwin[i].genint = 0;
		kill(pypepid, SIGUSR1);
		//fprintf(stderr,"das: sent int, disabled\n");
	      }
	    }
	  }
	}
	UNLOCK(semid);
      }
    }

    /* possibly bump up or down priority on the fly */
    LOCK(semid);
    k = dacq_data->dacq_pri;
    UNLOCK(semid);
    if (setpri && lastpri != k) {
      lastpri = k;
      errno = 0;
      if (setpriority(PRIO_PROCESS, 0, k) == -1 && errno) {
	/* disable future priority changes */
	setpri = 0;
      }
      if (lastpri < 0) {
	resched(1);
      }
    }
    LOCK(semid);
    k = dacq_data->terminate;
    UNLOCK(semid);
  } while (! k);

  fprintf(stderr, "%s: terminate signal received\n", progname);
  iscan_halt();
  eyelink_halt();
  if (usbjs_dev >= 0) {
    usbjs_close(usbjs_dev);
  }

  /* no longer ready */
  LOCK(semid);
  dacq_data->das_ready = 0;
  UNLOCK(semid);
}

int main(int ac, char **av)
{
  int i, c, option_index = 0;
  double f;
  char *p;

  static struct option long_options[] =
    {
      {"tracker", required_argument, 0, 't'}, /* tracker mode */
      {"port",    optional_argument, 0, 'p'}, /* dev file or ip num */
      {"elopts",  optional_argument, 0, 'e'}, /* eyelink options */
      {"elcam",   optional_argument, 0, 'c'}, /* eyelink camera (0/1) */
      {"usbjs",   optional_argument, 0, 'j'}, /* dev file for usbjs */
      {"swapxy",  optional_argument, 0, 's'}, /* swap xy channels? */
      {"arange",  optional_argument, 0, 'a'}, /* set dacq analog range */
      {0, 0, 0, 0}
    };

  /* save pype's pid in global var for later fast access */
  pypepid = getppid();


  p = rindex(av[0], '/');
  progname = p ? (p + 1) : av[0];
  fprintf(stderr, "%s: dacq4/comedi_server -- unified single dacq system\n",
	  progname);
  fprintf(stderr, "%s: pid=%d\n", progname, getpid());

  while ((c = getopt_long(ac, av, "t:p:e:c:j:s:a:",
			  long_options, &option_index)) != -1) {
    switch (c)
      {
      case 't':
	tracker = strcpy((char*)malloc(strlen(optarg)+1), optarg);
	break;
      case 'p':
	port = strcpy((char*)malloc(strlen(optarg)+1), optarg);
	break;
      case 'e':
	elopts = strcpy((char*)malloc(strlen(optarg)+1), optarg);
	break;
      case 'c':
	elcam = strcpy((char*)malloc(strlen(optarg)+1), optarg);
	break;
      case 'j':
	usbjs = strcpy((char*)malloc(strlen(optarg)+1), optarg);
	break;
      case 's':
	if (sscanf(optarg, "%d", &i) == 1) {
	  swap_xy = i;
	  if (swap_xy) {
	    fprintf(stderr, "%s: swapping X and Y\n", progname);
	  }
	}
	break;
      case 'a':
	if (sscanf(optarg, "%lf", &f) == 1) {
	  arange = f;
	}
	break;
      default:
	abort();
      }
  }

  if ((semid = psem_init(SEMKEY)) < 0) {
    ERROR("psem_init");
    fprintf(stderr, "%s: can't init semaphore\n", progname);
    exit(1);
  }

  mainloop_init();

  if (strcasecmp(tracker, "iscan") == 0) {
    iscan_init(port);
  } else if (strcasecmp(tracker, "eyelink") == 0) {
    eyelink_init(port, elopts, elcam);
  } else if (strcasecmp(tracker, "analog") == 0) {
    itracker = ANALOG;
  } else {
    itracker = NONE;
  }

  fprintf(stderr, "%s: tracker=%s (%d)\n", progname, tracker, itracker);

  if (usbjs != NULL && strlen(usbjs) > 0) {
    usbjs_dev = usbjs_init(usbjs);
    if (usbjs_dev < 0) {
      fprintf(stderr, "%s: can't open joystick %s\n", progname, usbjs);
    } else {
      fprintf(stderr, "%s: joystick at %s configured\n", progname, usbjs);
      LOCK(semid);
      dacq_data->js_enabled = 1;
      UNLOCK(semid);
    }
  }

  mainloop();
  comedi_close(comedi_dev);
  if (dacq_data != NULL) {
    shmdt(dacq_data);
    fprintf(stderr, "%s: SHM released\n", progname);
  }
  if (mem_locked) {
    if (munlockall() != 0) {
      ERROR("munlockall");
    } else {
      mem_locked = 0;
      fprintf(stderr, "%s: unlocked memory\n", progname);
    }
  }
  fprintf(stderr, "%s: bye bye\n", progname);
  exit(0);
}

/* end das_common.c */
