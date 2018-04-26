/* title:   shm semaphore wrapper..
** author:  jamie mazer
** created: Tue Apr  9 15:02:46 2002 mazer 
** info:    this module implements a SINGLE shared semaphore..
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


