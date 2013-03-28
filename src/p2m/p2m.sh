#!/bin/sh
#
# command line interface to p2mBatch.m for converting
# pypefiles to p2mfiles
#
# 9/25/2012: converted from csh to sh

if [ -z "$1" ]; then
  echo "Usage: `basename $0` pypefile1 pypefile2 ... pypefileN"
  echo "  Converts pypefiles to matlab 'p2m' files using pype"
  echo "  and matlab tools.  Leaves p2m files in same directory"
  echo "  as the original pype files."
  exit 1
fi


for i in $* ; do
  # messy sed calls below mimic csh's :r and :e variable modifiers
  root="`echo $i | sed -e 's|.[^.]*$||'`"
  if test "`expr $root : '.*\.\([^.]*\)$'`" = "gz" ; then
    dst="`echo $root | sed -e 's|.[^.]*$||'`".p2m
  else
    dst="$i.p2m"
  fi

  echo "[$i -> $dst]"

  if [ ! -f $i ]; then
    echo "`basename $0`: $i does not exist."
    exit 1
  fi

  /bin/rm -f /tmp/$$.exit
  unset DISPLAY
  echo "p2mBatch('$i', 1, 1); quit;" | matlab-nh -nodisplay -nojvm
  if [ -f /tmp/$$.exit ]; then
    s=`cat /tmp/$$.exit`
    /bin/rm -f /tmp/$$.exit
  else
    s=0
  fi
  if [ $s -ne 0 ]; then
    exit $s
  fi
done
