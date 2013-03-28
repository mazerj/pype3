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
#include <sys/io.h>
#include <signal.h>
#include <math.h>
#include <comedilib.h>
#include <getopt.h>

#include <ezV24/ezV24.h>	/* for iscan serial I/O  */


//compile: cc -o iscandump iscandump.c -lezV24

main(int ac, char **av)
{
  v24_port_t *iscan_port = NULL;
  int c, n;

  if (ac < 2) {
    fprintf(stderr, "need to supply port\n");
    exit(1);
  }

  if ((iscan_port = v24OpenPort(av[1], V24_NO_DELAY | V24_NON_BLOCK)) == NULL) {
    perror(av[1]);
    exit(1);
  }
  v24SetParameters(iscan_port, V24_B115200, V24_8BIT, V24_NONE);

  for (n=0; n < 1000; n++) {
    do {
      c = v24Getc(iscan_port);
    } while (c < 0);
    printf("0x%2X 0%-3o %3d %c", c, c, c, c > 32 ? c : '?');
    printf("\n");
  }
  v24ClosePort(iscan_port);
}
