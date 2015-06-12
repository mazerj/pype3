#!/bin/sh
#
# Find pype datafiles with missing or out of date p2m files and
# update them. Default is to do this is current directory, but
# you can specify a directory as well.

if [ "$1" = "" ]; then
  where="."
else
  where="$1"
fi

args=""
for line in $(find $where -name '*.[0-9][0-9][0-9]'); do 
  if [ ! -e "$line".p2m -o $line -nt "$line".p2m ]; then
    args="$args $line"
  fi
done

if [ "$args" = "" ]; then
  echo "Everything is up to date."
else
  p2m $args
fi
exit 0

find . -type f -name '*.[0-9][0-9][0-9]' -print0 | \
  while IFS= read -r -d $'\0' line; do
  echo "$line"
done
