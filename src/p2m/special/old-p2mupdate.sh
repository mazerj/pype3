#!/bin/csh -f

if ("$1" == "") then
  echo "Usage: `basename $0` ..pypefiles.."
  echo "  Updates existing p2m files with new data. This is not intended"
  echo "  gziped files. It will break!"
  exit 1
endif

if ($?DISPLAY) then
  unsetenv DISPLAY
endif

foreach i ($*)
  set ec=/tmp/$$.exit
  /bin/rm -f $ec

  echo "p2mBatch('$1', 1, 1);" | matlab -nodisplay -nojvm

  if (-e $ec) then
    set s = `cat $ec`
    /bin/rm -f $ec
  else
     set s = 0
  endif

  if ("$s") then
    exit $s
  endif
end
