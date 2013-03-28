/* title:   usbjs.c

** author:  jamie mazer
** created: Thu Mar  9 17:18:53 2006 mazer 
** info:    direct interface for a usb joystick device.
** history:
**
** NOTE:
**   usbjs_query is 0-based; 1st button is #0..
*/

#include <stdio.h>
#include <fcntl.h>
#include <errno.h>
#include <unistd.h>
#include <linux/joystick.h>

#include "usbjs.h"

int usbjs_init(char *devname)
{
  return(open(devname ? devname : "/dev/input/js0", O_RDONLY|O_NDELAY));
}

void usbjs_close(int fd)
{
  if (fd >= 0) {
    close(fd);
  }
}

int usbjs_query(int fd, int *buttonp, int *number, int *value,
		unsigned long *time)
{
  struct js_event e;

  if (read(fd, &e, sizeof(struct js_event)) < 0) {
    if (errno != EAGAIN) {
      fprintf(stderr, "usbjs_query: read error!\n");
    }
    return(0);
  } else {
    /* consider init and non-init events as the samething... */
    e.type &= ~JS_EVENT_INIT;
    if (buttonp) {
      if (e.type & JS_EVENT_BUTTON) {
	/* button event */
	*buttonp = 1;
      } else {
	/* axis event */
	*buttonp = 0;
      }
    }
    if (number) {
      /* button or axis number */
      *number = e.number;
    }
    if (value) {
      *value = e.value;
    }
    if (time) {
      *time = e.time;
    }
    return(1);
  }
}
