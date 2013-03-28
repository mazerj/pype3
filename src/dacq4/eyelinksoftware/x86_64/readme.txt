eyelink library for Linux

Contents
1. eyelink libraries
	eyelink_core, eyelink_core_graphics - both shared and static 
	libraries are found on lib directory. 
2. eyelink includes
	several eyelink include files are found on includes directory
	
3. eyelink sdl_util library
	convenient support functions for sdl.
	provides function like gaze cursor on double buffer surface 
	and software surfaces.
	
3. eyelink sample experiments
	Sample experiments for for eyelink libraries.
	To run with hard ware assisted flips and real-time mode:
	1. switch user to root or do a sudo
	2. set the environment variable SDL_VIDEODRIVER=dga.
	
4. SDL and GD support libraries
	find it in addon directory(you only need this if you do not have 
	sdl  and gd installed)
	
5. SDL and GD include files
	find it in addon directory (you only need this if you do not 
	have sdl and gd installed)

6. EyeLink DataViewer
	EyeLink Data viewer for Linux.  For this to run properly you need 
	to have java 1.4 or better and you need to install hasp driver
	(find hasp driver in addon directory). Hasp install instructions 
	are given on haspinstalation.txt and on INSTALL file on 
	haspdriver.tar.gz
	
7. EyeLink EDFConverter
	A GUI interface for the command line tool edf2asc. You need to 
	have  java 1.4 or better installed. 
	
8. EDF_AccessAPI
	A library to access edf content. The edf2asc program uses this 
	library. The edf2asc is given as an example.
	
9. edf2asc
	A command line tool to convert your edf files to ascii files.

Installation instruction
1. copy over the contents of lib, addon/lib to /usr/local/lib or /usr/lib
2. copy over the contents of bin, addon/bin to /usr/local/bin or /usr/bin
3. copy over the contents of include, addon/include to /usr/local/include or /usr/include
4. To install hasp extract haspdriver.tar.gz and follow the instructions 
   given on haspinstalation.txt or INSTALL file in haspdriver.tar.gz. There are rpm
   given for hasp install as well.
5. To install DataViewer just place the DataViewer directory to anywhere. To run the dataviewer 
   just type in dataviewer from the Dataviewer directory. The dataviewer install requires JRE 1.5 or later.


NOTE: 
      The edfconverter and dataviewer programs need to be run from the bin 
      directory(no symbolic links to the starter script).


Ubuntu easy install
--------------------
open up Synaptic Package Manager and install
libsdl1.2
libsdl-image
libsdl-mixer
libsdl-ttf


Once the above is installed, install eyelink api.
1. copy over the contents of lib, addon/lib to /usr/local/lib or /usr/lib
2. copy over the contents of bin, addon/bin to /usr/local/bin or /usr/bin


