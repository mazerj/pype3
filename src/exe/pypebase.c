/*
** This is a thin wrapper for starting up python, possibly
** with EUID=0. This is because you can't have pure python
** programs run SUID root.
**
** if PYPE is set, then it generates a wrapper that basically
** exec's:
**   % python pyperun [comand-line-args]
** while preserving root access, if possible. If PYPE is not
** set, then starts up a interpreter by passing `pyperun` the
** -s (`script`) arg:
**   % python pyperun -s [command-line-args]
**
** pyperun is a pure-python script in ../pype/pyperun
*/

#include <stdio.h>		/* for stderr() */
#include <unistd.h>		/* for geteuid() */
#include <stdlib.h>		/* for exit() */

int main(int ac, char **av)
{
  char **newav;
  int newac, n;

#ifdef PYPE
  newac = ac + 2;
  newav = (char **) calloc(sizeof(char *), (newac + 10));

  newav[0] = PYTHONEXE;
  newav[1] = RUN;
  for (n = 1; n < (ac+1); n++) {
    newav[1+n] = av[n];
  }
  if (geteuid() != 0) {
    fprintf(stderr, "pypeboot: warning not suid root.\n");
  }
  execvp(newav[0], newav);
#else // PYPENV
  newac = ac + 3;
  newav = (char **) calloc(sizeof(char *), (newac + 10));

  newav[0] = PYTHONEXE;
  newav[1] = RUN;
  newav[2] = "-s";
  for (n = 1; n < (ac+1); n++) {
    newav[2+n] = av[n];
  }
  execvp(newav[0], newav);
#endif
}
