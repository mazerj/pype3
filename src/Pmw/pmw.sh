#!/bin/sh

# Create a bundle file for Pmw -- one importable file that contains
# all the Pmw stuff (+ PmwBlt.py and PmwColor.py) and copy it to the
# target directory
#
# usage: sh ./pmw.sh pwm.tgz python-exe
#

x=`pwd`/Pmw

mkdir /tmp/$$
cd /tmp/$$
tar xfz $x/Pmw.1.3.2.patched.tgz

$2 ./Pmw.1.3.2/src/Pmw/Pmw_1_3/bin/bundlepmw.py \
    ./Pmw.1.3.2/src/Pmw/Pmw_1_3/lib >/dev/null

cp ./Pmw.py $1
cp ./Pmw.1.3.2/src/Pmw/Pmw_1_3/lib/PmwBlt.py $1
cp ./Pmw.1.3.2/src/Pmw/Pmw_1_3/lib/PmwColor.py $1
cd $x
rm -rf /tmp/$$

