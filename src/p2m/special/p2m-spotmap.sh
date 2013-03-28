#!/bin/csh -f

if ("$1" == "") then
  echo "Usage: `basename $0` p2mfile"
  echo "  Computes pixel-domain spotmap and spits out .ps and .rf files"
  exit 1
endif

echo "====================================================="
echo "    FILE: $1"
echo "====================================================="

set ec=/tmp/$$.exit
/bin/rm -f $ec
echo "p2mSpotmapBatch('$1');" | matlab -nodisplay
if (-e $ec) then
  set s = `cat $ec`
  /bin/rm -f $ec
else
  set s = 0
endif
if ("$s") then
  echo "aborting.."
  exit $s
endif
