#!/bin/sh


f=~/.pyperc/spikepattern

if [ "$1" = "-query" ]; then
  if [ -e $f ]; then
    cat $f
  else
    echo TTL
  fi
elif [ "$1" = "TTL" ]; then
  /bin/rm -f $f
  echo "Using TTL data."
elif [ "$1" = "ttl" ]; then
  /bin/rm -f $f
  echo "Using TTL data."
elif [ $# = 1 ]; then
  echo $1 >$f
  echo "Using plexon data from sig$1."
else
  cat <<EOF
usage: $(basename $0) [-query | channel-reg-ex]
  Where channel-reg-exp is some variant on: [0-9][0-9][0-9][a-z]. Here
  are some examples:
    "$(basename $0) TTL"  would select all spikes on electrode 7
    "$(basename $0) 007." would select all spikes on electrode 7
    "$(basename $0) 00.." would select ALL spikes on ALL electrodes
    "$(basename $0) 004b" would select unit b on electrode 4

  NOTE: Electrode numbers start at 001, units at 'a'
        And '.' is the 'match-any-char' for rex-exp's, NOT '?'
EOF
  exit 1
fi
exit 0

