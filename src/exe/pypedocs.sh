#!/bin/sh

dir=`dirname $0`
pypedir=`dirname $dir`

if [ "$1" = "-index" ]; then
  gnome-open file:$pypedir/docs/identifier-index.html
else
  gnome-open file:$pypedir/docs/index.html
fi
