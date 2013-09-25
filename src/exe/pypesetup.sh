#!/bin/sh

export PYPERC=$HOME/.pyperc

if [ ! -e $PYPERC ]; then
  mkdir $PYPERC
  chown $USER $PYPERC
  echo mkdir $PYPERC
fi

if [ ! -e $PYPERC/bin ]; then
  mkdir $PYPERC/bin
  chown $USER $PYPERC/bin
  echo mkdir $PYPERC/bin
fi

if [ ! -e $PYPERC/_none ]; then
  echo "WARNING: upgrading your .pyperc directory"
  mkdir $PYPERC/_none
  chown $USER $PYPERC/_none
  echo mkdir $PYPERC/_none
  mv -f $PYPERC/*.par $PYPERC/_none
  mv -f $PYPERC/pypestate* $PYPERC/_none
  mv -f $PYPERC/last.fid $PYPERC/_none
  mv -f $PYPERC/probe $PYPERC/_none
fi

if [ ! -e $PYPERC/Tasks ]; then
  mkdir $PYPERC/Tasks
  chown $USER $PYPERC/Tasks
  echo mkdir $PYPERC/Tasks
fi

if [ ! -e $PYPERC/Modules ]; then
  mkdir $PYPERC/Modules
  chown $USER $PYPERC/Modules
  echo mkdir $PYPERC/Modules
fi

if [ ! -e $PYPERC/Config.$(hostname) ]; then
  cat <<EOF >$PYPERC/Config.$(hostname)
# sample Config file
EYEMOUSE:1
FRAME: 1
MOUSE: 1
ONE_WINDOW: 1
USERDISPLAY_HIDE: 0
USERDISPLAY_SCALE: 0.50
SDLDPY: :0.0
FULLSCREEN: 0
EYETRACKER: ANALOG
FLIP_BAR: 1
USB_JS_DEV: /dev/input/js0
DPYW: 800
DPYH: 800
DPYBITS: 24
GAMMA: 2.17
VIEWDIST: 80
MON_ID: test display
MONW: 36.8
MONH: 27.9
SYNCSIZE: 0
SYNCX: 0
SYNCY: 0
AUDIODRIVER: alsa
EOF
fi

