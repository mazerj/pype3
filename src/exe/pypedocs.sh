#!/bin/sh

dir=`dirname $0`
pypedir=`dirname $dir`

if [ "$1" = "-index" ]; then
  xdg-open file:$pypedir/docs/identifier-index.html
else
  xdg-open file:$pypedir/docs/index.html
fi
