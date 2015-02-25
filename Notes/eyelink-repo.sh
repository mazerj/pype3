#!/bin/sh

cat <<EOF >>/etc/apt/sources.list

# Eyelink repository (64bit)
deb http://download.sr-support.com/x64 /

EOF

apt-get update
apt-get install eyelinkcore-1.9 eyelinkcoregraphics-1.9

