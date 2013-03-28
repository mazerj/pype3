
#ifdef DEBUG
# define REPORT(p) fprintf(stderr, "%s: %s", progname, p)
#else
# define REPORT(p)
#endif
