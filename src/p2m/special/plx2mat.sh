#!/bin/sh
#
# Extract .lfp and .spw files from .plx files
#
# usage: plx2mat [-f] ..plxfiles...
#  if -f is specified, then existing files will be overwritten
#  

force=0
if [ "$1" = "-f" ]; then
  force=1
  shift
fi

for f in $*; do
  if [ -e $f.lfp -a $f -nt $f.lfp ]; then
    echo "freshening $f"
    ex=1
  elif [ -e $f.lfp -a $force -eq 0 ]; then
    echo "skipped $f (use -f to force)"
    ex=0
  else
    echo "extracting $f"
    ex=1
  fi

  if [ $ex -eq 1 ]; then
    echo "plx2mat('$f'); quit;" | matlab -nojvm
  fi
done
