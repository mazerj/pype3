
# need subversion to pull down snapshot -- since you're
# looking at this file, it's probably already done..

##sudo apt-get install subversion
##svn checkout http://pype3.googlecode.com/svn/trunk/ pype3

# install required packages
sudo sh dep-packages.sh

# libezV24 is for iscan serial port comm -- for some reason it
# was dropped from Ubuntu 12.04, but picked up in later versions
# again.. It compiles out of the box, so it's no big deal..

tar xfz libezV24-0.1.3.tar.gz && \
    cd libezV24-0.1.3 && make && sudo make install && \
    cd .. && /bin/rm -rf libezV24-0.1.3
cd ..

# install to /usr/local

sudo ./localinstall install

cat <<EOF
1. Copy ../Notes/bashrc.sample" to your .bashrc file to setup path
2. run 'pypesetup' to setup config dir
3. run 'pype' to try it out
EOF
