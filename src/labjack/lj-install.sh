#!/bin/sh

sudo apt-get install build-essential
sudo apt-get install libusb-1.0-0-dev
sudo apt-get install git-core
git clone git://github.com/labjack/exodriver.git
cd exodriver/liblabjackusb/
make
sudo make install
cd ..
sed 's/adm/mlab/g' <10-labjack.rules >$$
sudo mv $$ /etc/udev/rules.d/10-labjack.rules
sudo udevadm control --reload-rules
cd ..
git clone git://github.com/labjack/LabJackPython.git
cd LabJackPython/
sudo python setup.py install
cd ..
sudo rm -rf LabJackPython exodriver

echo "plug in U3 and then run test.py"
