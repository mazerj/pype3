/* title:   dacq.h
** author:  jamie mazer
** created: Wed Jan  6 23:14:57 1999 mazer 
** info:    generic dacq interface structure
** history:
**
** Wed Jan  6 23:15:08 1999 mazer 
**   This is a generalized version of the original das_server.h
**   file.  The idea is to encapsulate a more general purpose
**   driver abstraction, not so directly tied to the das1600's
**   capabilities.  New devices will be able to use the same
**   interface.
**
** Sun Dec 16 16:27:10 2001 mazer 
**   added pp_XXXX functions to access a parallel port device..
**
** Tue Feb 19 13:08:43 2002 mazer 
**   added [xy]pow to dacq_eye_params()
**
** Sun Mar  9 13:25:58 2003 mazer 
**   added dacq_bar_transitions(int reset)
**
** Mon Mar 10 12:19:07 2003 mazer 
**   added dacq_bar_genint(int b) -- if you set this, then
**   each bar transition will generate a SIGUSR1 interuprt that
**   must be caught and handled..
**
** Wed Oct 20 15:40:26 2010 mazer 
**   dacq_adbuf_t() returns double instead of unsigned long
**
** Mon May 14 10:06:46 2012 mazer 
**   added dacq_fixwin_move(x,y,size) to update position/size w/o
**   changing anything else (like for pursuit!)
*/

extern int dacq_start(char *server, char *tracker, char *port, char *elopt,
		      char *elcam, char *swapxy, char *usbjs, int force);
extern void dacq_stop(void);
extern int dacq_release(void);

extern int dacq_eye_params(double xgain, double ygain, int xoff, int yoff,
			   double rot);
extern int dacq_eye_setaffine_coef(int r, int c, double val);
extern double dacq_eye_getaffine_coef(int r, int c);
extern int dacq_eye_read(int which);

extern unsigned long dacq_ts(void);
extern double dacq_usts(void);
extern double dacq_ts0(void);

extern int dacq_bar(void);
extern int dacq_bar_transitions(int reset);
extern int dacq_bar_genint(int b);

extern int dacq_joy_genint(int b);

extern void dacq_dig_out(int n, int val);
extern void dacq_juice(int on);
extern int dacq_juice_drip(int ms);

extern void dacq_fixbreak_tau(int n);
extern int dacq_fixwin(int n, int cx, int cy, int radius, double vbias);
extern int dacq_fixwin_move(int n, int cx, int cy, int radius);
extern int dacq_fixwin_genint(int n, int b);
extern int dacq_fixwin_reset(int n);
extern int dacq_fixwin_state(int n);
extern int dacq_fixwin_broke(int n);
extern long dacq_fixwin_break_time(int n);

extern int dacq_adbuf_toggle(int on);
extern void dacq_adbuf_clear(void);

extern int dacq_adbuf_size(void);
extern double dacq_adbuf_t(int ix);
extern void print_adbuf_t(int ix);
extern int dacq_adbuf_x(int ix);
extern int dacq_adbuf_y(int ix);
extern int dacq_adbuf_pa(int ix);
extern int dacq_adbuf_new(int ix);
extern int dacq_adbuf(int n, int ix);
extern int dacq_adbuf_c0(int ix);
extern int dacq_adbuf_c1(int ix);
extern int dacq_adbuf_c2(int ix);
extern int dacq_adbuf_c3(int ix);
extern int dacq_adbuf_c4(int ix);

extern int dacq_eye_smooth(int kn);
extern void dacq_set_pri(int dacq_pri);

extern int dacq_set_rt(int rt);
extern int dacq_seteuid(int uid);
extern int dacq_set_mypri(int pri);

extern int dacq_int_class(void);
extern int dacq_int_arg(void);

extern int dacq_jsbut(int n);
extern int dacq_js_x(void);
extern int dacq_js_y(void);

/* new alarm function -- set to zero to clear alarm */
extern void dacq_set_alarm(int ms_from_now);

extern void dacq_elrestart(void);

extern void dacq_set_xtracker(int x, int y, int pa);


