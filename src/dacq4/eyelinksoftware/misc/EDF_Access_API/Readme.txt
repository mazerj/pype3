October 15th, 2002

EDF Access API - BETA

This folder contains the EDF Access API C DLL for Windows (lib/win32).

The Examples directory contains the source code for the edf2asc program 
which has been re-written to use the access API. The edf2asc.exe is found in the example\debug directory

The docs directory contains an overview of the API functions.


Be sure to place the edfapi.dll and edfapi.lib in a directory that is in your library path, like windows\system32

The current version of edfapi supports the following platforms.
1. Windows (95/98/Me/2000/XP and NT 4.0)
2. Linux - linked against libc 6
3. MacOS X

The linux and MacOS X versions of edf2asc is placed in EDF_Access_API/Example.
mac osx executable -> edf2asc_osx.exe  edf2asc_static_osx.exe
linux executable -> edf2asc_linux.exe  edf2asc_static_linux.exe

The edf2asc_static_osx.exe and edf2asc_static_linux.exe are staically linked and edf2asc_osx.exe edf2asc_linux.exe
are dynamically linked. Thus, the dynamically linked executables requires the environment LD_LIBRARY_PATH(linux) or DYLD_LIBRARY_PATH(osx) to be set to
EDF_Access_API/lib/linux for linux and EDF_Access_API/lib/macosx for osx. If you have used the installer in osx to install the libraries, the installer install these to standard locations, so you do not need to set these variables.



Please direct any comments or bug reports to edfapi@eyelinkinfo.com



SR Research Team

