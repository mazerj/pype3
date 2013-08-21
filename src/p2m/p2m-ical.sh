#!/bin/csh -f

if ("$1" == "") then
  echo "Usage: `basename $0` p2mfile p2mfile ... p2mfile"
  echo "  Converts p2m files for eyecal runs into .ical"
  echo "  files.  Leaves ical files in same directory"
  echo "  as the original p2m files."
  exit 1
endif

foreach i ($*)
  echo "====================================================="
  echo "                           FILE: $i"
  echo "====================================================="
  if !(-e $i) then
    echo "`basename $0`: $i does not exist."
    exit 1
  endif
  echo "p2mEyecalBatch('$i', 1, 1); exit(0);" | matlab -nodisplay
  s = $status
  if ("$s") then
    echo "aborting.."
    exit $s
  endif
end
