## Pype3

Visual psychophysics and neurophysiology control system in
Python. Uses OpenGL+pygame for framebuffer control, numpy for
dynamic image synthesis and comedi to interface with data
acquisition hardware. Provides experimental stimulus generation,
real-time behavioral monitoring/control and data collection
in a single open source package.

Designed for Linux -- all mandatory dependencies are open source.

Migrated from googlecode to github 11/24/2014.

# 1st time installation instructions

1. Get a computer -- any commodity PC will do the trick -- we recommend a 64bit machine with an reasonably fast Nvidia graphics card supported by the NVidia proprietary linux drivers (most of the stimulus generation is currently done on the CPU, so a top-of-the-line video card won't be used to it's full capabilities).

2. Install Debian/Ubuntu linux. We use Ubuntu 10.04 in the lab for data collection machines, but that's not longer supported by Ubuntu, so I suggest new users start with 12.04 LTS, which is currently stable and supported (pype will work out of the box with 12.04 LTS). Debian's a much lighter weight installation, so if you're new to linux and just playing with pype for the first time, Debian's much quicker to get up and running.

3. Once Linux is up and running, log in and open a terminal window. You'll need to have root access to set up and install, so setup sudo or use su to become the root user.

4. The first thing you need to do is to install git and pull down a current snapshot of pype:

        % sudo apt-get -yq install git
	
5. Then pull down the latest version of pype from github:

        % git clone https://github.com/mazerj/pype3.git pype3
	
6. Install all the packages needed by pype:

        % cd pype3
        % sudo sh ./Notes/install-packages.sh
	
7. Add eyelink repository and install dev kit:

		% sudo sh ./Notes/eyelink-repo.sh
		...say 'y' to everything..

8. Install libezV24 (needed for access to serial port):

		% sudo sh ./Notes/ez-install.sh

9. Build and install local copy of pype:

		% ./localinstall

10. Append pype3/Notes/bashrc.sample to your ~/.bashrc file to getyourlogin environment setup with pype on the search path (if you'reusing csh/tcsh, it's finally time to switch to bash).

		% cat ./Notes/bashrc.sample >> ~/.bashrc

11. Open a new terminal window to pick up the new .bashrc (or source ~/.bashrc etc)

12. Create and initialize your ~/.pyperc directory (first time only):

        % pypesetup
	
13. Then you can actually get started. To fire up the GUI interface, just run the pype command:

        % pype

# Sample Tasks

To try things out, go ahead and start pype in the pype3/example-tasks directory that came with the distribution. This directory contains some sample tasks to play with and test things out. To load a tasks, just pick the task from the 'cwd' ('current working directory') tab in the main menu at the top of the GUI.

The first one to try is the basic `fixation` task -- if you're not actually running in a rig with and eye tracker etc, you should go to the `subject` worksheet and set the `win_size` parameter to 0, which will basically allow you to play without requiring a working eye tracker.

# Other useful shell commands

- *pypeconfig* - edit your config file (host specific!)
- *pypedocs* - open a browser to the on-line docs

# On-line documentation

Automatically generated documentation is available from the [Mazer lab web site](http://jackknife.med.yale.edu/docs). These docs can be generated automatically from the python code using epydoc (provided as build target).

# Subversion

For existing users, the file [svn-to-git.txt](https://github.com/mazerj/pype3/blob/master/svn-to-git.txt) contains a table for mappings from Subversion revision numbers (stored in pype files etc) to git hashes. You can use this to retrieve old versions of pype that match the data collection period.

# Notes for mac/osx

1. Everything works except the actual data collection (comedi_server).

2. Best bet is to use python2.7 from fink. First install fink
following instructions on the distribution site. Then the needed
packages:

    % sudo fink install scipy-py27
    % sudo fink install pygame-py27
    % sudo fink install swig

3. Then you should be able to follow the regular install instructions.

4. Everything seems to work, but hasn't been extensively tested yet.

# Gamma calibration

As of Dec 2014, pype has a built-in gamma calibration module derrived
from the standalone [optix2](https://github.com/mazerj/optix2). This
uses X-Rite [MonacoOPTIX DTP94](http://www.xrite.com/product_overview.aspx?ID=730&Action=support) USB device to measure Yxy values of the)
frame buffer and then fit gamma functions (and the full color gamut,
if you want it).

Note: The DTP94 is no longer available, but there is a recommended
replacement (i1Display Pro). If anyone tests this for protocol
compatibility, please let me know.

