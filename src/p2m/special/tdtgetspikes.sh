#!/bin/sh
#
# front end for tdtgetspikes.py -- tries to be smart..
#

if [ $# = 0 ]; then
  cat <<EOF
usage: `basename $0` [-f] p2mfiles...
  Pull .spk files from the tdt ttank server. Script tries to be smart
  about it and only pull down data when necessary. If '-f' is supplied,
  then force pull.

  NOTE: FAILURES are due to either passing a non-pypefile in or because
        the tank server program or machine is not available..
EOF
  exit 1
fi

force=0
if [ "$1" = "-f" ]; then
  force=1
  shift;
fi

for f in $*; do
  d=`dirname $f`		# directory name
  b=`basename $f`		# p2m file name
  t=$d/.$b.spk			# destination spike file

  if [ $force = 1 ]; then
    /bin/rm -f $t
  fi

  if [ ! -e $t ]; then
    # no spike file at all, generate one, if it's really a pypefile..
    if tdtgetspikes_ $f > /tmp/$$ 2>/dev/null; then
      mv /tmp/$$ $t
      echo PULLED $f
    else
      echo FAILED $f
    fi
  elif [ $f -nt $t ]; then
    # spike file exists, but it's older than the pypefile, so regenerate
    if tdtgetspikes_ $f > /tmp/$$ 2>/dev/null; then
      mv /tmp/$$ $t
      echo RE-PULLED $f
    fi
  else
      echo CURRENT $f
  fi
done
exit 0