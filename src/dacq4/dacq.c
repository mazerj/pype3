/* title:   dacq_client.c
** author:  jamie mazer
** created: Thu Dec 10 21:12:55 1998 mazer 
** info:    python bindings to talk to "das_server"
** history:
**
** Wed Jan  6 19:06:09 1999 mazer 
**   figured out what was delaying termination of the sound
**   stuff -- basically the default buffer size is 4096 samples
**   and my little tone bursts were around 400 samples, so
**   all the samples were zero padded.  I modified das_beep()
**   to open the device and reduces the fragment/thunk size to
**   256 bytes; this gives better responsiveness, at a slight
**   cost of cycles (I assume, but can't readily detect).
**
**   Along the way, I wrote a better interface (snd_* functions)
**   which allows for caching of sounds so you don't have to
**   recompute them (I thought that might the hang up).  This
**   works and should really be ripped out into a separate
**   module -- as should all the sound stuff, since it's got
**   nothing to do with the das drivers..
**
**   Ok -- to avoid later dangers -- I reimplmented das_beep()
**   using the new caching snd_* functions.  If you're lazy,
**   you can continue to use das_beep w/o risk..
**
** Wed Jan  6 22:27:02 1999 mazer 
**   split off snd_* function into separate module ("snd")
**
** Wed Jan  6 23:44:42 1999 mazer 
**   rewrote to use generic DACQ data structures -- this module
**   is now device INDEPENDENT and only das_server.c knows anythin
**   about the computerboards hardware..
**
** Thu Jan  6 11:20:31 2000 mazer
**   Moved eye_gain/offset stuff into das_server for speed
**   and to implement c-speed fixation windows (eventually).
**   This means that the das_server now returns +-2048 values;
**   so all the (val - 2048) frags were removed in this file.
**
** Thu Jan 27 20:34:48 2000 mazer
**   Changed the order of gain/offset application.
**   BEFORE:
**      out = (in - offset) * gain
**        [or, in = (out/gain) + offset]
**   AFTER:
**      out = (in * gain) - offset
**        [or, in = (out - offset) / gain]
**   This is actually a better way to do it, since you it makes
**   the units for offset equal to pixels for pype..
**
** Tue May 16 21:13:50 2000 mazer 
**   grafted in support for iscan serial link
**
** Sun Dec 16 16:16:22 2001 mazer 
**   added support for parallel port i/o for Ben Hayden's project
**
** Tue Feb 19 13:08:43 2002 mazer 
**   added [xy]pow to dacq_eye_params()
**
** Mon Feb 25 16:24:48 2002 mazer 
**   - removed dependency on env vars (passed directly in now to dacq_start)
**   - added nice support for all xxxx_servers
**
** Mon Mar  4 16:52:50 2002 mazer 
**   - removed iscan_server dependence (folded into das{16,08}_server.c)
**
** Thu Apr  4 14:06:25 2002 mazer 
**   - changed dacq_set_mypri() to also bump scheduler priority up to
**	realtime (SCHED_RR)
**
** Thu Aug  1 10:54:22 2002 mazer 
**   added: dacq_fixwin_reset(int n)
**
** Fri Aug 23 16:04:40 2002 mazer 
**   removed gaintables, eye_rot and eye_pow stuff
**
** Fri Jan 24 17:29:22 2003 mazer 
**   Added dacq_set_rt() to switch between RT and non-RT scheduler
**   modes.  This is now independent of the priority.
**
** Sun Mar  9 13:25:58 2003 mazer 
**   Added dacq_bar_transitions(int reset) & dacq_bar_gen_sigusr1(int b)
**   dacq_bar_gen_signusr1(1) makes the XXX_server generate a sigusr1
**   on each bar transition.  (0) turns it off.
**
**    IF YOU TURN THIS ON, YOU MUST HAVE A HANDLER SETUP!!
**  
**
** Mon Mar 10 12:27:06 2003 mazer 
**   Added dacq_fixwin_genint(int n, int b) -- if you set the nth
**   fixwin to TRUE, then when that fixwin is broken the pype
**   process will get a SIGUSR2 interupt that can be caught and
**   handled.
**
**   Interupts should only be raised once -- when the fixwin is
**   initialized or reset interupts are disabled automatically. Basically,
**   once you're sure he's in the window, you should enable interrupts.
**
**       IF YOU TURN THIS ON, YOU MUST HAVE A HANDLER SETUP!!
**
**
** Wed Mar 19 12:12:43 2003 mazer 
**   Modified to put all "interupts" through SIGUSR1.  Now pype just
**   catches SIGUSR1 and looks at the dacqinfo->int_class and int_arg
**   for dispatching:
**     class=1 (INT_DIN) for digital input transition arg=chan-num
**     class=2 (INT_FIXWIN) for fixwin break
**
** Sun Jan 25 14:39:05 2004 mazer 
**   added: int dacq_release(void)
**   this is to be called inside the SIGUSR1 interupt handler to make
**   sure that there's no stray semaphore being held by the current
**   process..
**
** Mon Jan 23 10:01:22 2006 mazer 
**   Added argument to dacq_fixwin to set vertical elongation of
**   factor on fixation windows.
**
** Thu Feb  2 10:03:25 2006 mazer 
**   added dacq_fixbreak_tau().
**
** Wed Mar 29 15:25:00 2006 mazer 
**   initialize dacq_data->js[]
**   added: dacq_jsbut(int n)
**
** Wed Apr 12 18:13:57 2006 mazer 
**   Removed all iscan_server.c junk --> now part of das_common.c
**   This involved changing the syntax for dacq_boot(), dacq_set_pri()
**     and messing with the DACQINFO structure to remove iscan_server
**     specific members.
**
** Tue Nov 28 16:58:07 2006 mazer 
**   added support for a ms-resolution alarm that sends interupts
**   the client/parent process: dacq_set_alarm(int ms_from_now)
**
** Tue Apr  3 10:39:56 2007 mazer 
**   added support for "-notracker" mode (for acutes)
**   activate by setting trakdev to "NONE" when calling dacq_start(). happens
**     in pype.py
**
** Thu Apr  5 10:29:16 2007 mazer 
**   About NADC and A/D channels in general... {das,comedi}_server etc all
**   work by sampling two sources of data:
**     - A/D channels 0-NADC are sampled continuously at 1kHz and the
**       data are inserted into dacq_data->adbuf[channel][time] (this used
**       to by a bunch of individual arrays: adbuf_c0, adbuf_c1 etc..
**     - In addition, a network or serial based eyetracker is also sampled
**       at an appropriate sampling rate. These data are inserted into
**       dacq_data->x,y,pa.
**
**   In the case of a coil system or other analog eyetracker, the [x,y]
**   eye position data should go into channels 0 & 1 respectively on the
**   DACQ board. If the tracker mode is "ANALOG", then the 0&1 channels
**   from dacq_data->adbuf are copied over into the data_data->x,y vectors
**   automatically. This means that adbuf[0,1][] is now redundant. This is
**   not a problem -- memory is cheap. Just don't enable saving to disk of
**   the 0/1 channels in pype
**
**   A similar situation exists for the photo diode and TTL spike inputs
**   lines. The photo_diode should go into ADC channel 2 and the TTL spike
**   signal into channel 3. Pype collects these data and saves them
**   automatically in the datafile on each trial. Again, memory is cheap,
**   so we live with some redundancy -- just don't enable save of c2 and c3
**   unless you're sure you know what you're doing.
**
**   To make a long story short, if you set the tracker to be EYELINK,
**   ISCAN or NONE, then you are free to use channels 0 and 1 to save
**   arbitary analog data at 1khz... into the datafile. Just make sure
**   you set the channels to be saved in pype (see the rig parameter
**   sheet down near the bottom).
**
** Mon Oct 11 15:38:49 2010 mazer 
**   deleted internal version of timestamp() --> gotta have comedi_server
**   working!
**
** Mon Oct 11 17:27:38 2010 mazer 
**   internally timestamps are now in us instead of ms, so we need to be
**   careful about this.. dacq_ts handles the division correctly, rounding
**   to nearest ms, but adbuf_t returns us for increases precision..
**
** Fri Oct 15 11:17:58 2010 mazer 
**   new version of dacq_start -- simplified and uses new command line
**   args (instead of ENV vars with XX_ prefix) to pass arguments into
**   comedi_server.
**
** Wed Oct 20 15:39:17 2010 mazer 
**   dacq_adbuf_t() returns double instead of unsigned long
**
** Thu Oct 21 15:18:27 2010 mazer 
**   new: dacq_clockreset() -- tells comedi_server to reset the internal
**   timestamp clock.
**
** Tue Apr 26 13:03:58 2011 mazer 
**   added support for on-line affine transform matrix
**
** Mon May 14 10:06:46 2012 mazer 
**   added dacq_fixwin_move(x,y,size) to update position/size w/o
**   changing anything else (like for pursuit!)
*/

#include <sys/types.h>
#include <time.h>
#include <sys/time.h>
#include <unistd.h>
#include <sys/resource.h>
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <string.h>
#include <signal.h>
#include <sys/ipc.h>
#include <sys/shm.h>
#include <sys/wait.h>
#include <sys/errno.h>
#include <math.h>
#include <sys/io.h>
#include <sched.h>
#include <errno.h>

#include "dacqinfo.h"
#include "psems.h"
#include "dacq.h"


static DACQINFO *dacq_data = NULL;
static pid_t server_pid = -1;
static int semid = -1;

static void dacq_sigchld_handler(int signum)
{
  int e, tflag;

  /* in theory wait(NULL) should tell us which child terminated, but
   * that seems to cause problems.. so we'll stick with the old logic..
   */

  LOCK(semid);
  tflag = dacq_data->terminate;
  UNLOCK(semid);

  if ((e = kill(server_pid, 0)) < 0) {
    if (errno == ESRCH && tflag) {
      fprintf(stderr, "dacq: server normal exit (pid=%d)\n", server_pid);
    } else if (errno == EPERM && tflag) {
      fprintf(stderr, "dacq: server alive, but rooted (pid=%d)\n", server_pid);
    }
  } else if (e == 0) {
    /* some non-dacq process exited, just ignore it.. */
  } else if (! tflag) {
    /* dacq process did exit, but it was unexpected */
    fprintf(stderr, "dacq: fatal server death (pid=%d)\n", server_pid);
    exit(1);
  } else {
    /* dacq process did exit, but it was supposed to!! */
    fprintf(stderr, "dacq: likely normal server exit (pid=%d)\n", server_pid);
  }
  /* reset signal handler */
  signal(SIGCHLD, dacq_sigchld_handler);
}

static void shm_init(void)
{
  int i, ii;

  for (i = 0; i < NDIGIN; i++) {
    dacq_data->din[i] = 0;
    dacq_data->din_changes[i] = 0;
    dacq_data->din_intmask[i] = 0;
  }
  
  for (i = 0; i < NDIGOUT; i++) {
    dacq_data->dout[i] = 0;
  }
  
  dacq_data->dout_strobe = 0;
  
  for (i = 0; i < NADC; i++) {
    dacq_data->adc[i] = 0;
  }

  dacq_data->eye_xgain = 1.0;
  dacq_data->eye_ygain = 1.0;
  dacq_data->eye_xoff = 0;
  dacq_data->eye_yoff = 0;

  // start with empty affine transform: [1 0 0; 0 1 0; 0 0 1]
  for (i = 0; i < 3; i++) {
    for (ii = 0; ii < 3; ii++) {
      dacq_data->eye_affine[i][ii] = (i == ii) ? 1.0 : 0.0;
    }
  }
  
  for (i = 0; i < NFIXWIN; i++) {
    dacq_data->fixwin[i].active = 0;
    dacq_data->fixwin[i].genint = 0;
  }
  
  for (i = 0; i < NJOYBUT; i++) {
    dacq_data->js[i] = 0;
  }
  dacq_data->js_x = 0;
  dacq_data->js_y = 0;
  dacq_data->js_enabled = 0;
  
  dacq_data->adbuf_on = 0;
  dacq_data->adbuf_ptr = 0;
  dacq_data->adbuf_overflow = 0;
  for (i = 0; i < ADBUFLEN; i++) {
    dacq_data->adbuf_t[i] = 0.0;
    dacq_data->adbuf_x[i] = 0;
    dacq_data->adbuf_y[i] = 0;
    for (ii=0; ii < NADC; ii++) {
      dacq_data->adbufs[ii][i] = 0;
    }
  }
  
  for (i = 0; i < NDAC; i++) {
    dacq_data->dac[i] = 0;
  }
  
  dacq_data->dac_strobe = 0;
  
  dacq_data->timestamp = 0;
  dacq_data->terminate = 0;
  dacq_data->das_ready = 0;
  
  dacq_data->eye_smooth = 0;
  dacq_data->eye_x = 0;
  dacq_data->eye_y = 0;
  
  dacq_data->dacq_pri = 0;
  
  dacq_data->fixbreak_tau = 5;
  
  /* alarm timer (same units as timestamp); 0 for no alarm */
  dacq_data->alarm_time = 0;

  dacq_data->clock_reset = 0;

  dacq_data->pype_pid = getpid();
}


int dacq_start(char *server, char *tracker, char *port, char *elopt,
	       char *elcam, char *swapxy, char *usbjs, int force)
{
  int shmid, i;

  if ((shmid = shmget((key_t)SHMKEY, sizeof(DACQINFO), 0666 | IPC_CREAT)) < 0) {
    if (errno == EINVAL) {
      fprintf(stderr, "dacq_start: SHM buffer's changed size.\n");
      fprintf(stderr, "dacq_start: run pypekill and start again\n");
      return(-1);
    } else {
      perror("shmget");
      fprintf(stderr, "dacq_start: kernel compiled with SHM/IPC?\n");
      return(-1);
    }
  }

  if ((dacq_data = shmat(shmid, NULL, 0)) == NULL) {
    perror("shmat");
    fprintf(stderr, "dacq_start: kernel compiled with SHM/IPC?\n");
    return(-1);
  }

  if (dacq_data->pype_pid > 0 && kill(dacq_data->pype_pid, 0) == 0) {
    fprintf(stderr, "dacq_start: pype (pid=%d) is running!\n",
	    dacq_data->pype_pid);
    return(-1);
  }

  /* check to see if old comedi_server is running! */
  if (dacq_data->server_pid > 0 && kill(dacq_data->server_pid, 0) == 0) {
    fprintf(stderr, "dacq_start: comedi_server (pid=%d) running\n",
	    dacq_data->server_pid);
    if (force) {
      if (kill(dacq_data->server_pid, 9) < 0) {
	fprintf(stderr, "dacq_start: run `pypekill` and try again.\n");
	return(-1);
      }
    } else {
      return(0);
    }
  }

  if ((semid = psem_init(SEMKEY)) < 0) {
    perror("psem_init");
    fprintf(stderr, "dacq_start: can't init semaphore\n");
    return(-1);
  } else {
    /* start semaphore off at value of 1 */
    if (psem_set(semid, 1) < 0) {
      perror("psem_init");
      return(-1);
    }
  }

  shm_init();			/* initialize shm block */
  signal(SIGCHLD, dacq_sigchld_handler);
  if ((server_pid = fork()) == 0) {
    /* child becomes dac subsystem server */
    execlp(server, server, tracker, port, elopt, elcam, swapxy, usbjs, NULL);
    perror(server);
    exit(1);
  } else {
    /* parent waits for server to become ready */
    do {
      LOCK(semid);
      i = dacq_data->das_ready;
      UNLOCK(semid);
      usleep(1000);
    } while (i == 0);
  }
  return(1);
}

void dacq_stop(void)
{
  int status;

  if (server_pid >= 0) {
    fprintf(stderr, "dacq_stop: waiting for server (pid=%d) shutdown.\n",
	    server_pid);
    LOCK(semid);
    dacq_data->terminate = 1;
    UNLOCK(semid);
    waitpid(server_pid, &status, 0);
    fprintf(stderr, "dacq_stop: server has terminated.\n");
  }
}

int dacq_release(void)
{
  /* release semaphore if we own it -- this is for inside
  ** interupt handlers only!!
  */
  if ((semid)>=0) {
    return(psem_incr_mine(semid));
  }
  return(1);
}

static int dacq_dig_in(int n)
{
  int i;

  LOCK(semid);
#ifdef BUT_TEST
  fprintf(stderr, "%d: ", n);
  for (i=0; i < 4; i++) {
    fprintf(stderr, "%d ", dacq_data->din[i]);
  }
  fprintf(stderr, "\n");
#endif
  i = dacq_data->din[n];
  UNLOCK(semid);

  return(i);
}

void dacq_dig_out(int n, int val)
{
  int i;
  /* wait for strobe to be clear */
  do {
    LOCK(semid);
    i = dacq_data->dout_strobe;
    UNLOCK(semid);
    usleep(100);
  } while (i);

  LOCK(semid);  
  dacq_data->dout[n] = val ? 1 : 0;

  /* signal server digital output pending */
  dacq_data->dout_strobe = 1;
  UNLOCK(semid);  
}

int dacq_eye_params(double xgain, double ygain, int xoff, int yoff, double rot)
{
  LOCK(semid);
  dacq_data->eye_xgain = xgain;
  dacq_data->eye_ygain = ygain;
  dacq_data->eye_xoff = xoff;
  dacq_data->eye_yoff = yoff;
  dacq_data->eye_rot = rot;
  UNLOCK(semid);
  return(1);
}

int dacq_eye_setaffine_coef(int r, int c, double val)
{
  LOCK(semid);
  dacq_data->eye_affine[r][c] = val;
  UNLOCK(semid);
  return(1);
}

double dacq_eye_getaffine_coef(int r, int c)
{
  double f;

  LOCK(semid);
  f = dacq_data->eye_affine[r][c];
  UNLOCK(semid);
  return(f);
}

int dacq_eye_read(int which)
{
  int i;

  LOCK(semid);
  switch (which)
    {
    case 1:
      i = dacq_data->eye_x;
      break;
    case 2:
      i = dacq_data->eye_y;
      break;
    case -1:
      i = dacq_data->eye_rawx;
      break;
    case -2:
      i = dacq_data->eye_rawy;
      break;
    default:
      i = 0;
      break;
  }
  UNLOCK(semid);
  return(i);
}

unsigned long dacq_ts(void)	/* this is timestamp to nearest MS */
{
  unsigned long i;
  LOCK(semid);
  i = dacq_data->timestamp;
  UNLOCK(semid);
  return(i);
}

double dacq_usts(void)		/* us timestamp as double */
{
  double f;
  LOCK(semid);
  f = dacq_data->usts;
  UNLOCK(semid);
  return(f);
}

double dacq_ts0(void)		/* retrieve raw timestamp 0-basis */
{
  double f;
  LOCK(semid);
  f = dacq_data->ts0;
  UNLOCK(semid);
  return(f);
}

int dacq_bar(void)
{
  /* note: digital 1 (high) is pressed */
  if (dacq_dig_in(0)) {
    return(1);
  } else {
    return(0);
  }
}

int dacq_bar_genint(int b)
{
  int i;

  //LOCK(semid);
  i = dacq_data->din_intmask[0];
  dacq_data->din_intmask[0] = b;
  //LOCK(semid);
  return(i);
}

int dacq_joy_genint(int b)
{
  int i;

  //LOCK(semid);
  i = dacq_data->joyint;
  dacq_data->joyint = b;
  //LOCK(semid);
  return(i);
}

int dacq_bar_transitions(int reset)
{
  int i;
  LOCK(semid);
  i = dacq_data->din_changes[0];
  if (reset) {
    dacq_data->din_changes[0] = 0;
  }
  UNLOCK(semid);
  return(i);
}

void dacq_juice(int on)
{
  if (on) {
    dacq_dig_out(0, 1);
  } else {
    dacq_dig_out(0, 0);
  }
}

int dacq_juice_drip(int ms)
{
  // Wed Nov 28 13:47:59 2012 mazer 
  // revised version of this function that restarts after
  // interupts -- this should work even if interupts are
  // enabled.. the caveat is that a long running interupt
  // hander could cause real problems..
  unsigned long endat;

  dacq_juice(1);
  LOCK(semid);
  endat = dacq_data->timestamp + ms;
  while (dacq_data->timestamp <= endat) {
    UNLOCK(semid);
    usleep(1000);
    LOCK(semid);
  }
  UNLOCK(semid);
  dacq_juice(0);
  return(1);
}

void dacq_fixbreak_tau(int n)
{
  /*
   * set time period (in ms/sampling ticks) the eye must be outside
   * the fixation window before it counts as a break
   */
  LOCK(semid);
  dacq_data->fixbreak_tau = n;
  UNLOCK(semid);
}
  
int dacq_fixwin(int n, int cx, int cy, int radius, double vbias)
{
  if (n < 0) {
    return(NFIXWIN);
  } else if (n > NFIXWIN) {
    return(0);
  } else {
    LOCK(semid);
    if (radius > 0) {
      dacq_data->fixwin[n].active = 0;

      dacq_data->fixwin[n].xchn = 0;
      dacq_data->fixwin[n].ychn = 1;
      dacq_data->fixwin[n].vbias = vbias;
      dacq_data->fixwin[n].state = 0;
      dacq_data->fixwin[n].broke = 0;
      dacq_data->fixwin[n].genint = 0;
      dacq_data->fixwin[n].break_time = 0;
      dacq_data->fixwin[n].fcount = 0;
      dacq_data->fixwin[n].nout = 0;

      dacq_fixwin_move(n, cx, cy, radius);

      dacq_data->fixwin[n].active = 1;
    } else {
      dacq_data->fixwin[n].active = 0;
    }
    UNLOCK(semid);
    return(1);
  }
}

int dacq_fixwin_move(int n, int cx, int cy, int radius)
{
  if (n < 0 || n > NFIXWIN) {
    return(0);
  } else {
    dacq_data->fixwin[n].cx = cx;
    dacq_data->fixwin[n].cy = cy;
    if (radius > 0) {
      dacq_data->fixwin[n].rad2 = (radius * radius);
    }
    return(1);
  }
}

int dacq_fixwin_genint(int n, int b)
{
  int i = -1;
  if (n >= 0) {  
    LOCK(semid);
    i = dacq_data->fixwin[n].genint;
    dacq_data->fixwin[n].genint = b;
    UNLOCK(semid);
  }
  return(i);
}

int dacq_fixwin_reset(int n)
{
  if (n >= 0) {
    LOCK(semid);
    dacq_data->fixwin[n].active = 0;

    dacq_data->fixwin[n].state = 0;
    dacq_data->fixwin[n].broke = 0;
    dacq_data->fixwin[n].genint = 0;
    dacq_data->fixwin[n].break_time = 0;
    dacq_data->fixwin[n].fcount = 0;
    dacq_data->fixwin[n].nout = 0;

    dacq_data->fixwin[n].active = 1;
    UNLOCK(semid);
  }
  return(1);
}

int dacq_fixwin_state(int n)
{
  int s;

  /* if eye gets inside window, then reset broke flag */
  LOCK(semid);
  s = dacq_data->fixwin[n].state;
  if (s) {
    dacq_data->fixwin[n].broke = 0;
    dacq_data->fixwin[n].genint = 0;
  }
  UNLOCK(semid);
  return(s);
}
  
int dacq_fixwin_broke(int n)
{
  int i;
  LOCK(semid);
  i = dacq_data->fixwin[n].broke;
  UNLOCK(semid);
  return(i);
}

long dacq_fixwin_break_time(int n)
{
  long i;

  LOCK(semid);
  i = dacq_data->fixwin[n].break_time;
  UNLOCK(semid);
  return(i);
}

int dacq_adbuf_toggle(int on)
{
  int i;

  LOCK(semid);
  dacq_data->adbuf_on = 0;
  UNLOCK(semid);
  if (on) {
    dacq_adbuf_clear();
    LOCK(semid);
    dacq_data->adbuf_on = 1;
    UNLOCK(semid);
    return(1);
  } else {
    LOCK(semid);
    i = dacq_data->adbuf_overflow;
    UNLOCK(semid);
    return(i);
  }
}

void dacq_adbuf_clear()
{
  int i, ii;

  LOCK(semid);
  dacq_data->adbuf_on = 0;		/* turn off sampling */
  dacq_data->adbuf_ptr = 0;		/* reset pointer beginning */
  dacq_data->adbuf_overflow = 0;	/* reset overflow flag */
  for (i = 0; i < ADBUFLEN; i++) {	/* clear buffers. */
    dacq_data->adbuf_t[i] = 0.0;
    dacq_data->adbuf_x[i] = 0;
    dacq_data->adbuf_y[i] = 0;
    for (ii=0; ii < NADC; ii++) {
      dacq_data->adbufs[ii][i] = 0;
    }
  }
  UNLOCK(semid);
}

int dacq_adbuf_size()
{
  int i;

  LOCK(semid);
  i = dacq_data->adbuf_ptr;
  UNLOCK(semid);
  return(i);
}

double dacq_adbuf_t(int ix) /* 10/12/2010: adbuf_t now in US! */
{
  double f;

  LOCK(semid);
  f = dacq_data->adbuf_t[ix];
  UNLOCK(semid);
  return(f);
}

void print_adbuf_t(int ix)
{
  double f;

  LOCK(semid);
  f = dacq_data->adbuf_t[ix];
  UNLOCK(semid);
  fprintf(stdout, "<%f>", f);
  fflush(stdout);
}

int dacq_adbuf_x(int ix)
{
  int i;

  LOCK(semid);
  i = dacq_data->adbuf_x[ix];
  UNLOCK(semid);
  return(i);
}

int dacq_adbuf_y(int ix)
{
  int i;

  LOCK(semid);
  i = dacq_data->adbuf_y[ix];
  UNLOCK(semid);
  return(i);
}

int dacq_adbuf_pa(int ix)
{
  int i;

  LOCK(semid);
  i = dacq_data->adbuf_pa[ix];
  UNLOCK(semid);
  return(i);
}

int dacq_adbuf_new(int ix)
{
  int i;

  LOCK(semid);
  i = dacq_data->adbuf_new[ix];
  UNLOCK(semid);
  return(i);
}

int dacq_adbuf(int n, int ix)
{
  int i;

  LOCK(semid);
  i = dacq_data->adbufs[n][ix];
  UNLOCK(semid);
  return(i);
}

/*
 * these functions are just for backward compatibility
 */
int dacq_adbuf_c0(int ix) { return(dacq_adbuf(0, ix)); }
int dacq_adbuf_c1(int ix) { return(dacq_adbuf(1, ix)); }
int dacq_adbuf_c2(int ix) { return(dacq_adbuf(2, ix)); }
int dacq_adbuf_c3(int ix) { return(dacq_adbuf(3, ix)); }
int dacq_adbuf_c4(int ix) { return(dacq_adbuf(4, ix)); }

int dacq_eye_smooth(int kn)
{
  int i;

  LOCK(semid);
  dacq_data->eye_smooth = kn;
  i = dacq_data->eye_smooth;
  UNLOCK(semid);
  return(i);
}

void dacq_set_pri(int dacq_pri)
{
  LOCK(semid);
  dacq_data->dacq_pri = dacq_pri;
  UNLOCK(semid);
}


int dacq_seteuid(int uid)
{
  return(seteuid((uid_t) uid));
}

int dacq_set_rt(int rt)
{
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
    return(1);
  }
  return(0);
}

int dacq_set_mypri(int pri)
{
  uid_t old = geteuid();
  int result;

  if (seteuid((uid_t)0) == 0) {
    errno = 0;
    if (setpriority(PRIO_PROCESS, 0, pri) == 0 && errno == 0) {
      result = 1;
    } else {
      result = 0;
    }
    seteuid(old);
  } else {
    result = 0;
  }
  return(result);
}

int dacq_int_class(void)
{
  int i;
  LOCK(semid);
  i = dacq_data->int_class;
  UNLOCK(semid);
  return(i);
}

int dacq_int_arg(void)
{
  int i;
  LOCK(semid);
  i = dacq_data->int_arg;
  UNLOCK(semid);
  return(i);
}

int dacq_jsbut(int n)
{
  int i;

  /* read the nth joystick button; or if n < 0, query to see if
   * joystick is available
   */
  LOCK(semid);
  if (n < 0) {
    i = dacq_data->js_enabled;
  } else {
    i = (n < NJOYBUT) ? dacq_data->js[n] : -1;
  }
  UNLOCK(semid);
  return(i);
}

int dacq_js_x()
{
  int i;

  /* read the joystick's x-axis value */
  LOCK(semid);
  i = dacq_data->js_x;
  UNLOCK(semid);
  return(i);
}


int dacq_js_y()
{
  int i;

  /* read the joystick's y-axis value */
  LOCK(semid);
  i = dacq_data->js_y;
  UNLOCK(semid);
  return(i);
}

void dacq_set_alarm(int ms_from_now)
{
  LOCK(semid);
  if (ms_from_now) {
    dacq_data->alarm_time = dacq_data->timestamp + ms_from_now;
  } else {
    dacq_data->alarm_time = 0;
  }
  UNLOCK(semid);
}

void dacq_setmouse(int mx, int my)
{
  LOCK(semid);
  dacq_data->mx = mx;
  dacq_data->my = my;
  dacq_data->mnew = 1;
  UNLOCK(semid);
}


void dacq_elrestart(void)
{
  LOCK(semid);
  dacq_data->elrestart = 1;
  UNLOCK(semid);
}
