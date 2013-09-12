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

apt-get install -yq \
	comedi-source \
	libcomedi-dev \
	libcomedi0 \
	libezV24-0 \
	libezV24-dev \
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
	python-tk 

