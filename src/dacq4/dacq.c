/* title:   dacq.c
** author:  jamie mazer
** created: Thu Dec 10 21:12:55 1998 mazer 
** info:    python bindings to talk to "das_server"
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
#include <sched.h>
#include <errno.h>
#ifndef __APPLE__
# include <sys/io.h>
#endif

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
  dacq_data->servers_avail = 0;
  
  dacq_data->eye_smooth = 0;
  dacq_data->eye_x = 0;
  dacq_data->eye_y = 0;
  
  dacq_data->dacq_pri = 0;
  
  dacq_data->fixbreak_tau_ms = 5;
  
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

  // NOTE: pype (ie, dacq.c) initializes all the shared memory
  // and semaphores before starting the comedi_server process.
  // As part of this initialization, the locking semaphore is
  // initialized to 1. In order to take the lock, you have to
  // then decrement the semaphore. This means that comedi_server
  // will block at the first LOCK() if pype is not running.
  //
  // That's correct/fine -- unless you're trying to debug...

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
      i = dacq_data->servers_avail;
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
  f = dacq_data->ts0;		/* ts0 is time  comedi server */
  UNLOCK(semid);		/* was initialized */
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

// dacq_bar_genint(0/1): disable/enable bar-generated interupts
int dacq_bar_genint(int b)
{
  int i;

  //LOCK(semid);
  i = dacq_data->din_intmask[0];
  dacq_data->din_intmask[0] = b;
  //LOCK(semid);
  return(i);
}

// dacq_joy_genint(0/1): disable/enable joystick-generated interupts
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

void dacq_fixbreak_tau_ms(int nms)
{
  /*
   * set time period (in ms) the eye must be outside the fixation
   * window before it counts as a break
   */
  LOCK(semid);
  dacq_data->fixbreak_tau_ms = nms;
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
    if (b >= 0) {
      dacq_data->fixwin[n].genint = b;
    }
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
    // Tue Sep 24 17:40:53 2013 mazer 
    //   not sure why checking the fixation window was
    //   turning off the interupt generator, but it's
    //   almost certainly WRONG.
    //dacq_data->fixwin[n].genint = 0;
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

int dacq_set_rt(int rt)
{
#ifndef __APPLE__
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
#else
  // for osx, sched_getparam doesn't seem to exist.. so just ignore calls..
  return(1);
#endif
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
    if (seteuid(old)) {
      perror("should never happen!");
    }
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

void dacq_elrestart(void)
{
  LOCK(semid);
  dacq_data->elrestart = 1;
  UNLOCK(semid);
}

void dacq_set_xtracker(int x, int y, int pa)
{
  /* set externally read tracker (eg, eyetribe or similar) */
  LOCK(semid);
  dacq_data->xx = x;
  dacq_data->xy = y;
  dacq_data->xpa = pa;
  dacq_data->xnew = 1;
  UNLOCK(semid);
}
