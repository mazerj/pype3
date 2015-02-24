#!/bin/sh

cat <<EOF EOF >>/etc/apt/sources.list

# Eyelink repository (64bit)
deb http://download.sr-support.com/x64 /

EOF

apt-get update
apt-get -yq install eyelinkcore-1.9 eyelinkcoregraphics-1.9

