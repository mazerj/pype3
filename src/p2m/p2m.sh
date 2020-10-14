#!/bin/sh
#
# command line interface to p2mBatch.m for converting
# pypefiles to p2mfiles
#
# 9/25/2012: converted from csh to sh

if [ -z "$1" ]; then
    echo "Usage: `basename $0` [-f] pypefile1 pypefile2 ... pypefileN"
    echo "  Converts pypefiles to matlab 'p2m' files using pype"
    echo "  and matlab tools.  Leaves p2m files in same directory"
    echo "  as the original pype files."
    echo "  -f option will force update (even if dates indicate not needed)"
    exit 1
fi

force=0
for src in $* ; do
    if [ "$src" = "-f" ]; then
	force=1
	continue
    fi
       
    # messy sed calls below mimic csh's :r and :e variable modifiers
    root="`echo $src | sed -e 's|.[^.]*$||'`"
    if test "`expr $root : '.*\.\([^.]*\)$'`" = "gz" ; then
	dst="`echo $root | sed -e 's|.[^.]*$||'`".p2m
    else
	dst="$src.p2m"
    fi

    if [ ! -f $src ]; then
	echo "`basename $0`: $src does not exist."
	exit 1
    fi

    update=0
    if [ $force = 1 ]; then
	update=1
    elif [ -f $dst ]; then
	if [ $src -nt $dst ]; then  
	    update=1
	else
	    update=0
	fi
    else
	update=1
    fi

    if [ "$update" = "1" ]; then
	echo "[$src -> $dst]"
	unset DISPLAY
	#echo "p2mBatch('$src', 1, 1); exit(0);" | matlab-nh -nodisplay -nojvm
	matlab-batch "p2mBatch('$src', 1, 1);"
	if [ $? -ne 0 ]; then
	    exit 1
	fi
    else
	echo "[$src -> $dst] no update needed"
    fi
done
