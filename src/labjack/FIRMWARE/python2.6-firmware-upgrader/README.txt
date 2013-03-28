--------------- LabJack Python Cross-platform Firmware Upgrader ---------------

Pre-reqs:
- The driver for the platform you are on. ( Windows = UD, Mac = liblabjackusb.dylib, Linux = liblabjackusb.so )
- The very latest version of LabJackPython from github (http://github.com/labjack/LabJackPython)
- Python 2.5
- Other Python Modules: simplejson and httplib2

Instructions:

PLEASE: Disconnect all devices except the one you wish to upgrade.


----- Upgrading to latest, stable version:

To upgrade your device to the latest, stable version of the firmware simply type the following:

python selfUpgrader.py <device type>

Where "device type" is 3 for U3s, 6 for U6s, or 9 for UE9s. This will download the firmware from our site an install it onto the first found device of that type.


----- Recovering from a failed upgrade:

If your device is stuck with the LED blinking quickly, try running the installer again with the -r flag. Like this:

python selfUpgrader.py -r <device type>


----- Upgrading to a specific version of the firmware:

If you have a specific version of the firmware you would like to install, run selfUpgrader.py with the -v flag. This will download that version of the firmware from the site.

python selfUpgrader.py -v <version number> <device type>

For example, if I wanted to upgrade my U6 to firmware version 0.98 ( in beta ), I would run the program like this:

python selfUpgrader.py -v 0.98 6

Because the UE9 has Communication and Control firmware, you have to specify their versions separately. Use -m for Comm. and -c for Control.

python selfUpgrader.py -m <Comm version number> -c <Control version number> <device type>

----- Upgrading based on a given file:

If you have a bin/hex firmware file, you can install it using the -f flag

python selfUpgrader.py -f <filename> <device type>
 
For UE9s, you can specify the -f flag twice, one for Comm and one for Control.

----- Upgradeing a UE9 over Ethernet

If you wish to upgrade your UE9's firmware over the network, use the --ip-address flag:

python selfUpgrader.py --ip-address 192.168.1.209 9

----- Getting help if something goes wrong:

Most of the time, the firmware upgrade shouldn't have any problems. All LabJacks are designed to be quite fault tolerant, so you can write new firmware without fear that you'll "brick" your device. So, if the firmware upgrade does fail, take a breath, and try to relax. If something does go wrong, make a note of the error you received. If the LED on the device is blinking rapidly, that means it is stuck waiting for new firmware. Try running the upgrader program in recovery mode, that should fix the problem. If your problem can't be solved by running recovery mode, let us know at support@labjack.com and give us all errors and output you received from the program.










