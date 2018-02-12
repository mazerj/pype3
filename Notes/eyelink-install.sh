#!/bin/sh

if [ `whoami` != root ]; then
    echo "run as root!"
    exit 1
fi

# run as root..

cat <<EOF >/etc/apt/sources.list.d/eyelink.list
# Eyelink repository
deb http://download.sr-support.com/software SRResearch main
EOF

cd /tmp
wget http://download.sr-support.com/software/dists/SRResearch/SRResearch_key
apt-key add SRResearch_key
rm SRResearch_key

apt-get update
apt-get install eyelinkcore eyelinkcoregraphics
apt-get install -f
