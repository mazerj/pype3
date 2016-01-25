#!/bin/sh
#
# generate setup.sh file in specfified install dir
# to setup path and env automatically
#

if [ "$1" = "" ]; then
  echo "usage: `basename $0` install-dir"
  exit 1
fi

INSTDIR="$1"

cat <<EOF >$INSTDIR/setup.sh
export PYPEDIR=$INSTDIR
PATH=$INSTDIR/bin:$INSTDIR/p2m:\$PATH
EOF


echo "------------------------------------------------"
echo "To activate, add to .bashrc:"
echo "   . $INSTDIR/setup.sh"
echo "------------------------------------------------"
