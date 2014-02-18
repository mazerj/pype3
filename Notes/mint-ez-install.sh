#!/bin/sh
#
# Looks like Ubuntu/Mint no longer provides the libezV24 library, so
# this will quickly compile and install the library using a tweaked
# version of the sources (makefile fixed!)
#
# Note: this is require on very recent installs to run the mlab-wide
# shared version of pype.
#

D=`pwd`
mkdir /tmp/$$ && cd /tmp/$$
tar xfz $D/mint-libezV24-0.1.3.tar.gz
cd libez*
pwd
make
echo "READY TO INSTALL?  REQUIRES SUDO ACCESS:"
sudo make install
cd $D
/bin/rm -rf /tmp/$$
