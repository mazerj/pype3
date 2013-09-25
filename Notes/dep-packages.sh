#!/bin/sh
#
# install packages needed for pype -- run as root..
#
# see `dep-packages.txt` for descriptions of each
# dependency.
#

# enable partner repositories:
grep partner /etc/apt/sources.list | grep '^# deb' | sed 's/# //g' >/tmp/$$
cat /tmp/$$ >>/etc/apt/sources.list && /bin/rm /tmp/$$

# update index files
apt-get update -yq

# make sure all installed packages are up to date
apt-get upgrade -yq

# avoid user confirmation for installation of msttcorefonts package:
sudo sh -c "echo ttf-mscorefonts-installer msttcorefonts/accepted-mscorefonts-eula select true | debconf-set-selections"

# this takes a while (5-10 mins) because python-epydoc pulls down
# tex for formatting docs..
apt-get install -yq \
	libcomedi-dev \
	libcomedi0 \
	libsdl-image1.2-dev \
	libsdl-ttf2.0-dev \
	libsmpeg-dev \
        libusb-dev \
	msttcorefonts \
	python-epydoc \
	python-xlrd \
	python-comedilib \
	python-dev \
	python-imaging \
	python-imaging-tk \
	python-mysqldb \
	python-numpy \
	python-matplotlib \
	python-opengl \
	python-pmw \
	python-pygame \
	python-scipy \
	python-tk \
	swig

