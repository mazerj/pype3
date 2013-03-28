/* title:   shm semaphore wrapper..
** author:  jamie mazer
** created: Tue Apr  9 15:02:46 2002 mazer 
** info:    this module implements a SINGLE shared semaphore..
** history:
**    this is sort of like the gallant-lab speaking stick...
**
** Tue Apr  9 15:12:13 2002 mazer 
**   each call to sem_init() will return handle for a single
**   system wide semaphore (created, if it doesn't already
**   exist).  It's #0 in a set of 1.
**
**   the logic here is:
**     - semaphore is initialized to value of 1
**     - too take the semaphore, you DECREMENT (now it's zero),
**	 and nobody can decrement it while it's zero.
**     - when you're done, you INCREMENT, leaving the semaphore
**       at 1, which will unblock someone waiting to decrement..
**
**   We can think of the semaphore as holding a resource, when the
**   semaphore is 1, 1 unit of resource is available, you decrement
**   the semaphore to take ther resource and increment it when you
**   return the resource to the pool.  Trying to take from an empty
**   semaphore, will block (it doesn't have to if you use IPC_NOWAIT).
**
**   -> NOTE: psem_free() removed semaphore from the kernel, anybody
**      waiting for the semaphore will get an error...
**
**   -> NOTE: got to be careful about nested locks within a single
**            process -- don't call LOCK() before calling some other
**            function, if the second function calls LOCK() too, then
**            it will block and never return!!!!
**
**   -> NOTE: using the 't' function in main below, I get about
**            0.6us per pair of incr/decr operations, so this should
**	      be fast enough to use all over the place..
**
** Sun Jan 25 14:34:38 2004 mazer 
**   added: int psem_decr_mine(int semid)
**   which decremements (UNLOCKS) the semaphore ONLY if it's owned by
**   the processes calling the function..
**
** Thu Mar 23 11:45:54 2006 mazer 
**   dummy_server under ubuntu 5.10 seems to die if the semaphore's are
**   deleted and then decremented.. now a warning is printed and then it
**   should exit normally.
**
** Thu Apr 13 09:42:44 2006 mazer 
**   Modified the psem_incr/_decr() code to use a common underlying
**   function and put the underlying function in a loop. I think stray
**   interupts can cause semop() to exit before getting the semaphore,
**   which gets things out of sync. With this change, the semaphore code
**   loops UNTIL it takes or drops the semaphore, even if it gets
**   interupted.
**
**   NOTE: This really only seemed to be a problem when the standalone
**         iscan_server program was running. Now that the iscan_server
**         functionality has been folded into das_common, I think this
**         fix may be extraneous.. but I think it's still correct.
*/

#include <stdio.h>
#include <sys/types.h>
#include <unistd.h>
#include <sys/ipc.h>
#include <sys/sem.h>
#include <errno.h>

#include "psems.h"


int psem_init(int key)
{
  if (key < 0) {
    key = 0xABCD;
  }
  return(semget((key_t) key, 1, 0666 | IPC_CREAT));
}

int psem_free(int semid)
{
  return(semctl(semid, 0, IPC_RMID, 0));
}


int psem_set(int semid, int value)
{
  union semun {
    int val;                    /* value for SETVAL */
    struct semid_ds *buf;       /* buffer for IPC_STAT, IPC_SET */
    unsigned short int *array;  /* array for GETALL, SETALL */
    struct seminfo *__buf;      /* buffer for IPC_INFO */
  } u;
  u.val = value;
  return(semctl(semid, 0, SETVAL, u));
}

int psem_get(int semid)
{
  return(semctl(semid, 0, GETVAL, 0));
}

int psem_info(int semid)
{
  printf("%d waiting\n", semctl(semid, 0, GETNCNT, 0));
  printf("last pid = %d\n", semctl(semid, 0, GETPID, 0));
  printf("value = %d\n", semctl(semid, 0, GETVAL, 0));
  return(1);
}

int _psem_change(int semid, int dir)
{
  struct sembuf s;

  s.sem_num = 0;		/* first semaphore */
  s.sem_op = dir;
  s.sem_flg = 0;		/* block/wait */

  while (1) {
    if (semop(semid, &s, 1) < 0) {
      if (errno == EINVAL) {
	fprintf(stderr, "warning: psem_decr semaphore destroyed?\n");
	return(1);
      } else {
	perror("psem_change/semop (restarted)");
      }
    } else {
      return(1);
    }
  }
}

int psem_incr(int semid)
{
  return(_psem_change(semid, 1));
}

int psem_decr(int semid)
{
  return(_psem_change(semid, -1));
}

int psem_incr_mine(int semid)
{
  if (semctl(semid, 0, GETPID, 0) == getpid()) {
    return(psem_incr(semid));
  }
  return(0);
}


