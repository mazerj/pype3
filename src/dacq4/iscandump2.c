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


//compile: cc -o iscandump2 iscandump2.c -lezV24

main(int ac, char **av)
{
  v24_port_t *iscan_port = NULL;
  int c, n, k, x, y;
  unsigned char buf[6];
  short *ibuf;

  if (ac < 2) {
    fprintf(stderr, "need to supply port\n");
    exit(1);
  }

  if ((iscan_port = v24OpenPort(av[1], V24_NO_DELAY | V24_NON_BLOCK)) == NULL) {
    perror(av[1]);
    exit(1);
  }
  v24SetParameters(iscan_port, V24_B115200, V24_8BIT, V24_NONE);

  ibuf = (short *)buf;
  for (n=0; n < 1000; n++) {
    do {
      c = v24Getc(iscan_port);
    } while (c < 0);
    for (k = 0; k < 5; k++) {
      buf[k] = buf[k+1];
    }
    buf[5] = 0x00ff & c;
    if (buf[0] == 'D' && buf[1] == 'D') {
      x = ibuf[1] + 128; /* 128 gets things centered ~0 */
      y = (2*ibuf[2]) + 128;
      printf("%d %d\n", x, y);
    }
  }
  v24ClosePort(iscan_port);
}
