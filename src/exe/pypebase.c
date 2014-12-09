#include <stdio.h>		/* for stderr() */
#include <unistd.h>		/* for geteuid() */
#include <stdlib.h>		/* for exit() */

int main(int ac, char **av)
{
  char **newav;
  int newac, n;

#ifdef PYPE
  newac = ac + 2;
  newav = (char **) calloc(sizeof(char *), (newac + 2));

  newav[0] = PYTHONEXE;
  newav[1] = RUN;
  for (n = 1; n < (ac+1); n++) {
    newav[1+n] = av[n];
  }
#ifndef __APPLE__
  if (geteuid() != 0) {
    fprintf(stderr, "pypeboot: not suid root and not running as root.\n");
    exit(1);
  }
#endif
  execvp(newav[0], newav);
#else // PYPENV
  newac = ac + 3;
  newav = (char **) calloc(sizeof(char *), (newac + 2));

  newav[0] = PYTHONEXE;
  newav[1] = RUN;
  newav[2] = "-s";
  for (n = 1; n < (ac+1); n++) {
    newav[2+n] = av[n];
  }
  execvp(newav[0], newav);
#endif
}
