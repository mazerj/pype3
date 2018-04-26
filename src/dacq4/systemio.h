extern double timestamp(void);
extern int locktocore(int corenum);
extern void resched(int rt);
extern void *shm_init(int *shmid);
extern void shm_close(void *ptr);

