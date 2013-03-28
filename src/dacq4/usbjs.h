/* title:   usbjs.h

** author:  jamie mazer
** created: Thu Mar  9 17:18:53 2006 mazer 
** info:    api for usbjs.c
** history:
**
*/

extern int usbjs_init(char *devname);
extern void usbjs_close(int fd);
extern int usbjs_query(int fd, int *buttonp, int *number, int *value,
		       unsigned long *time);
