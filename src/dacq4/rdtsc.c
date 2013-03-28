double find_clockfreq()	/* get clock frequency in Hz */
{
  FILE *fp;
  char buf[100];
  double mhz;

  if ((fp = fopen("/proc/cpuinfo", "r")) == NULL) {
    fprintf(stderr, "%s: can't open /proc/cpuinfo\n", progname);
    exit(1);
  }
  mhz = -1.0;
  while (fgets(buf, sizeof(buf), fp) != NULL) {
    if (sscanf(buf, "cpu MHz         : %lf", &mhz) == 1) {
      break;
    }
  }
  return(mhz * 1.0e6);
}

unsigned long timestamp(int init)
{
  static struct timespec ti[2];	/* initial and current times */
  static long en;		/* elapsed time in nanosecs */


  if (init) {
    clock_gettime(CLOCK_MONOTONIC, &ti[0]);
    return(0);
  } else {
    en = 1e9 * (ti[1].tv_sec - ti[0].tv_sec) + (ti[1].tv_nsec - ti[0].tv_nsec);
    return (en / 1e6);		/* return elapsed time in ms */
  }
}


#if defined(__i386__)

// this macro doesn't quite work (under 64bit??)

#define RDTSC(x) __asm__ __volatile__ ( ".byte 0x0f,0x31"		\
					:"=a" (((unsigned long*)&x)[0]), \
					 "=d" (((unsigned long*)&x)[1]))

unsigned long timestamp(int init)
{
  static unsigned long long timezero;
  unsigned long long now;

  RDTSC(now);			/* get cycle counter from hardware TSC */
  if (init) {
    timezero = now;
    return(0);
  } else {
    /* use precalibrated ticks_per_ms to convert to real time.. */
    return((unsigned long)((now - timezero) / ticks_per_ms));
  }
}

#elif defined(__x86_64__)

/* need to use different method to access real time clock
** under 64bit kernel!
*/

unsigned long timestamp(int init)
{
  static unsigned long long timezero;
  unsigned long long now;
  unsigned a, d;

  asm("cpuid");
  asm volatile("rdtsc" : "=a" (a), "=d" (d));
  now = ((unsigned long long)a) | (((unsigned long long)d) << 32);

  if (init) {
    timezero = now;
    return(0);
  } else {
    /* use precalibrated ticks_per_ms to convert to real time.. */
    return((unsigned long)((now - timezero) / ticks_per_ms));
  }
}
#else
# error "real time clock not defined this arch"
#endif

