#!/bin/sh

# Create a bundle file for Pmw -- one importable file that contains
# all the Pmw stuff (+ PmwBlt.py and PmwColor.py) and copy it to the
# target directory
#
# usage: sh ./pmw.sh installdir python-exe
#

x=`pwd`
cp $x/Pmw2/Pmw.py $1
cp $x/Pmw2/PmwBlt.py $1
cp $x/Pmw2/PmwColor.py $1
exit

if 0; then
    archive=$x/Pmw2/Pmw_2_0_0-rc1.tar.gz

    mkdir /tmp/$$
    cd /tmp/$$
    tar xfz $archive

    $2 $x/Pmw2/bundlepmw.py ./Pmw2/Pmw/Pmw_*/lib/ >/dev/null
fi
if 0; then
    cd $x
    rm -rf /tmp/$$
fi
