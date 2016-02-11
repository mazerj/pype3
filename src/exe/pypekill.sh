#!/bin/sh

if [ "$1" != "" ]; then
    # with any args rerun as root using sudo (needed to clear SHM stuff)
    sudo -p"sudo [pypekill]:" $0
    exit 0
fi

# kill stray pype processes
ps -ax --width=1000 2>/dev/null | egrep "pyperun" | \
    grep -v grep | awk '{print $1}' | xargs -r kill -9
ps -ax --width=1000 2>/dev/null | egrep "[0-9] comedi_server" | \
    grep -v grep | awk '{print $1}' | xargs -r kill -9

# free up shared memory segments
ipcs -m | grep '^0x[0-9a-f]*da01' | awk '{print $1}' | \
    xargs -r ipcrm -M

# free up semaphores
ipcs -s | grep '^0x[0-9a-f]*f0f0' | awk '{print $1}' | \
    xargs -r ipcrm -S

exit 0
