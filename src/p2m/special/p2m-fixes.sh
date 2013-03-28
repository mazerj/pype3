#!/bin/csh -f

if ("$1" == "") then
  echo "Usage: `basename $0` p2mfile icalfile"
  echo "  Calibrates eye traces in p2mfile using icalfile and then"
  echo "  extracts fixation data into a new structure and saves"
  echo "  the fixation data back into the .p2m file (new .fixes"
  echo "  member of the pf structure."
  exit 1
endif

echo "====================================================="
echo "    FILE: $1"
echo "    ICAL: $2"
echo "====================================================="

set ec=/tmp/$$.exit
/bin/rm -f $ec
echo "p2mFindFixes('$1', '$2', 1, 1);" | matlab -nodisplay
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
