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

  signal(SIGHUP,	sigint_handler);
  signal(SIGINT,	sigint_handler);
  signal(SIGQUIT,	sigint_handler);
  signal(SIGILL,	sigint_handler);
  signal(SIGTRAP,	sigint_handler);
  signal(SIGABRT,	sigint_handler);
  signal(SIGIOT,	sigint_handler);
  signal(SIGBUS,	sigint_handler);
  signal(SIGFPE,	sigint_handler);
  signal(SIGKILL,	sigint_handler);
  signal(SIGUSR1,	sigint_handler);
  signal(SIGSEGV,	sigint_handler);
  signal(SIGUSR2,	sigint_handler);
  signal(SIGPIPE,	sigint_handler);
  signal(SIGALRM,	sigint_handler);
  signal(SIGTERM,	sigint_handler);
  signal(SIGSTKFLT,	sigint_handler);
  signal(SIGCLD,	sigint_handler);
  signal(SIGCHLD,	sigint_handler);
  signal(SIGCONT,	sigint_handler);
  signal(SIGSTOP,	sigint_handler);
  signal(SIGTSTP,	sigint_handler);
  signal(SIGTTIN,	sigint_handler);
  signal(SIGTTOU,	sigint_handler);
  signal(SIGURG,	sigint_handler);
  signal(SIGXCPU,	sigint_handler);
  signal(SIGXFSZ,	sigint_handler);
  signal(SIGVTALRM,	sigint_handler);
  signal(SIGPROF,	sigint_handler);
  signal(SIGWINCH,	sigint_ignore);
  signal(SIGPOLL,	sigint_handler);
  signal(SIGIO,		sigint_handler);
  signal(SIGPWR,	sigint_handler);
  signal(SIGUNUSED,	sigint_handler);
}
