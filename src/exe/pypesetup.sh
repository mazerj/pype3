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
