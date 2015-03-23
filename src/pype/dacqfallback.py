# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""Fallback dacq module for non-comedi systems (ie, osx)

"""

from simpletimer import get_monotonic_ms

def dacq_start(server, tracker, port, elopt, elcam, swapxy, usbjs, force):
    return 1

def dacq_stop():
    return

def dacq_release():
    return 1

def dacq_eye_params(xgain, ygain, xoff, yoff, rot):
    return 1

def dacq_eye_setaffine_coef(r, c, val):
    return 1

def dacq_eye_getaffine_coef(r, c):
    return 1.0

def dacq_eye_read(which):
    return 1

def dacq_ts():
    return get_monotonic_ms()

def dacq_usts():
    return 1.0

def dacq_ts0():
    return 1.0

def dacq_bar():
    return 1

def dacq_bar_transitions(reset):
    return 0

def dacq_bar_genint(b):
    return 0

def dacq_joy_genint(b):
    return 0

def dacq_dig_out(n, val):
    return

def dacq_juice(on):
    return

def dacq_juice_drip(ms):
    return 1

def dacq_fixbreak_tau(n):
    return

def dacq_fixwin(n, cx, cy, radius, vbias):
    return 1

def dacq_fixwin_move(n, cx, cy, radius):
    return 1

def dacq_fixwin_genint(n, b):
    return 1

def dacq_fixwin_reset(n):
    return 1

def dacq_fixwin_state(n):
    return 1

def dacq_fixwin_broke(n):
    return 1

def dacq_fixwin_break_time(n):
    #return long
    return 1

def dacq_adbuf_toggle(on):
    return 1

def dacq_adbuf_clear():
    return

def dacq_adbuf_size():
    return 1

def dacq_adbuf_t(ix):
    return 1

def print_adbuf_t(ix):
    return

def dacq_adbuf_x(ix):
    return 1

def dacq_adbuf_y(ix):
    return 1


def dacq_adbuf_pa(ix):
    return 1


def dacq_adbuf_new(ix):
    return 1


def dacq_adbuf(n, ix):
    return 1


def dacq_adbuf_c0(ix):
    return 1


def dacq_adbuf_c1(ix):
    return 1


def dacq_adbuf_c2(ix):
    return 1


def dacq_adbuf_c3(ix):
    return 1


def dacq_adbuf_c4(ix):
    return 1

def dacq_eye_smooth(kn):
    return 1

def dacq_set_pri(dacq_pri):
    return

def dacq_set_rt(rt):
    return 1

def dacq_seteuid(uid):
    return 1

def dacq_set_mypri(pri):
    return 1

def dacq_int_class():
    return 1

def dacq_int_arg():
    return 1

def dacq_jsbut(n):
    return 1

def dacq_js_x():
    return 1

def dacq_js_y():
    return 1

def dacq_set_alarm(ms_from_now):
    return

def dacq_setmouse(mx, my):
    return

def dacq_elrestart():
    return

def  dacq_set_xtracker(x, y, pa):
    return
