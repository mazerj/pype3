#include <time.h>
#include <sys/time.h>
#include <sys/errno.h>
#include <sys/resource.h>
#include <sys/types.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>

#include <sys/ipc.h>
#include <sys/shm.h>
#include <sys/mman.h>

#define __USE_GNU 1
#include <sched.h>		/* need __USE_GNU=1 to get CPU_* macros */

#include "dacqinfo.h"
#include "systemio.h"

double timestamp(void)		/* return elapsed time in us */
{
  static struct timespec ti[2];	/* initial and current times */
  clock_gettime(CLOCK_MONOTONIC, &ti[1]);
  return((1.0e6 * (double)(ti[1].tv_sec - ti[0].tv_sec)) +
	 (1.0e-3 * (double)(ti[1].tv_nsec - ti[0].tv_nsec)));
}

int locktocore(int corenum) /* -1 for no lock; else corenum (0,1..) */
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

void *shm_init(int *shmid)
{
  void *datablock = NULL;
  
  if ((*shmid = shmget((key_t)SHMKEY,
		       sizeof(DACQINFO), 0666 | IPC_CREAT)) < 0) {
    perror("shm_init");
    return(NULL);
  }
  if ((datablock = shmat(*shmid, NULL, 0)) == NULL) {
    perror("shm_init");
    return(NULL);
  }
  if (mlockall(MCL_CURRENT)) {
    perror("shm_init");
  }
  return(datablock);
}

void shm_close(void *ptr)
{
  if (shmdt(ptr)) {
    perror("shm_close");
  }
  if (munlockall()) {
    perror("shm_close");
  }
}
