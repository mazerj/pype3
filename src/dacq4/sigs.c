#include <stdio.h>
#include <signal.h>
#include <stdlib.h>

#include "sigs.h"

static char *pname = "generic_dacq";

static void sigint_handler(int signum)
{
  fprintf(stderr, "%s: caught SIG#%02d, exiting.\n", pname, signum);
  exit(1);
}

static void sigint_ignore(int signum)
{
  fprintf(stderr, "%s: caught spurious SIG#%02d, continuing\n", pname, signum);
  signal(signum, sigint_ignore);
}

void catch_signals(char *p)
{
  if (pname) {
    pname = p;
  }

#ifdef SIGHUP
  signal(SIGHUP,	sigint_handler);
#endif
#ifdef SIGINT
  signal(SIGINT,	sigint_handler);
#endif
#ifdef SIGQUIT
  signal(SIGQUIT,	sigint_handler);
#endif
#ifdef SIGILL
  signal(SIGILL,	sigint_handler);
#endif
#ifdef SIGTRAP
  signal(SIGTRAP,	sigint_handler);
#endif
#ifdef SIGABRT
  signal(SIGABRT,	sigint_handler);
#endif
#ifdef SIGIOT
  signal(SIGIOT,	sigint_handler);
#endif
#ifdef SIGBUS
  signal(SIGBUS,	sigint_handler);
#endif
#ifdef SIGFPE
  signal(SIGFPE,	sigint_handler);
#endif
#ifdef SIGKILL
  signal(SIGKILL,	sigint_handler);
#endif
#ifdef SIGUSR1
  signal(SIGUSR1,	sigint_handler);
#endif
#ifdef SIGSEGV
  signal(SIGSEGV,	sigint_handler);
#endif
#ifdef SIGUSR2
  signal(SIGUSR2,	sigint_handler);
#endif
#ifdef SIGPIPE
  signal(SIGPIPE,	sigint_handler);
#endif
#ifdef SIGALRM
  signal(SIGALRM,	sigint_handler);
#endif
#ifdef SIGTERM
  signal(SIGTERM,	sigint_handler);
#endif
#ifdef SIGSTKFLT
  signal(SIGSTKFLT,	sigint_handler);
#endif
#ifdef SIGCLD
  signal(SIGCLD,	sigint_handler);
#endif
#ifdef SIGCHLD
  signal(SIGCHLD,	sigint_handler);
#endif
#ifdef SIGCONT
  signal(SIGCONT,	sigint_handler);
#endif
#ifdef SIGSTOP
  signal(SIGSTOP,	sigint_handler);
#endif
#ifdef SIGTSTP
  signal(SIGTSTP,	sigint_handler);
#endif
#ifdef SIGTTIN
  signal(SIGTTIN,	sigint_handler);
#endif
#ifdef SIGTTOU
  signal(SIGTTOU,	sigint_handler);
#endif
#ifdef SIGURG
  signal(SIGURG,	sigint_handler);
#endif
#ifdef SIGXCPU
  signal(SIGXCPU,	sigint_handler);
#endif
#ifdef SIGXFSZ
  signal(SIGXFSZ,	sigint_handler);
#endif
#ifdef SIGVTALRM
  signal(SIGVTALRM,	sigint_handler);
#endif
#ifdef SIGPROF
  signal(SIGPROF,	sigint_handler);
#endif
#ifdef SIGWINCH
  signal(SIGWINCH,	sigint_ignore);
#endif
#ifdef SIGPOLL
  signal(SIGPOLL,	sigint_handler);
#endif
#ifdef SIGIO
  signal(SIGIO,		sigint_handler);
#endif
#ifdef SIGPWR
  signal(SIGPWR,	sigint_handler);
#endif
#ifdef SIGUNUSED
  signal(SIGUNUSED,	sigint_handler);
#endif
}
