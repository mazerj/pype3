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

2. Install Ubuntu. We use 10.04 in the lab for data collection machines, but that's not longer supported by Ubuntu, so I suggest new users start with 12.04 LTS, which is currently stable and supported (pype will work out of the box with 12.04 LTS).

3. Once Ubuntu is up and running, log in and open a terminal window. The first thing you need to do is to install subversion and pull down a current snapshot of pype:

    % sudo apt-get -yq install git-core
	
4. Then pull down the repository from github:

    % git clone https://github.com/mazerj/pype3.git pype3
	
5. Install all the dependency packages needed by pype. This will take ~10 mins. The fresh-install.sh script will download and install all the packages needed to build/run pype and then do the actual build/install into /usr/local/pype3:

    % cd pype3/Notes; sudo sh fresh-install.sh
	
6. Append pype3/Notes/bashrc.sample to your ~/.bashrc file to get your login environment setup with pype on the search path (if you're using csh/tcsh, it's finally time to switch to bash).
7. Open a new terminal window to pick up the new .bashrc (or source ~/.bashrc etc)
8. Create and initialize your ~/.pyperc directory (first time only):

    % pypesetup
	
9. Then you can actually get started. To fire up the GUI interface, just run the pype command:

    % pype

# Sample Tasks

To begin with, start pype in the pype3/Notes directory downloaded from googlecode. This directory contains some sample tasks to play with and test things out. To load a tasks, just pick the task from the 'cwd' ('current working directory') tab in the main menu at the top of the GUI.


# Other useful commands

- *pypeconfig* - edit your config file (host specific!)
- *pypedocs* - open a browser to the on-line docs

# Subversion

The file [svn-to-git.txt](https://github.com/mazerj/pype3/blob/master/svn-to-git.txt) contains a table for mappings from Subversion revision numbers (stored in pype files etc) to git hashes. You can use this to retrieve old versions of pype that match the data collection period.
