/* title:   shm semaphore wrapper..
** author:  jamie mazer
** created: Tue Apr  9 15:02:46 2002 mazer 
** info:    this module implements a SINGLE shared semaphore..
** history:
**
** Tue Apr  9 15:12:13 2002 mazer 
**   interface file for psems.c, see psems.c for documentation
**
*/

extern int psem_init(int key);
extern int psem_free(int semid);
extern int psem_set(int semid, int value);
extern int psem_get(int semid);
extern int psem_info(int semid);
extern int psem_incr(int semid);
extern int psem_incr_mine(int semid);
extern int psem_decr(int semid);

/* useful macros: */

#define LOCK(semid) {if ((semid)>=0) psem_decr(semid);}
#define UNLOCK(semid) {if ((semid)>=0) psem_incr(semid);}

//#define LOCK(semid)
//#define UNLOCK(semid)
