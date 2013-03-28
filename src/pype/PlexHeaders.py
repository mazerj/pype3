#!/usr/bin/env python
# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""Plexon Datafile/Network Headers

Structure definitions generated from inspection of Plexon.h and .m
files distributed on Plexon web site - no code in this module.

Author -- James A. Mazer (james.mazer@yale.edu)

"""

"""Revision History

- Thu Mar 26 15:10:32 2009 mazer

  - removed c-structs from documentation - see the Plexon.h file
    in this dir for complete structure definitions.

"""


class Plex(object):
	"""
	Constants needed for parsing plexon files and expanding the
	binary data structures in raw .plx files.

	"""

	PL_SingleWFType = 1
	PL_StereotrodeWFType = 2
	PL_TetrodeWFType = 3
	PL_ExtEventType = 4
	PL_ADDataType = 5
	PL_StrobedExtChannel = 257
	PL_StartExtChannel	= 258
	PL_StopExtChannel = 259
	PL_Pause = 260
	PL_Resume = 261

	# Waveform length
	MAX_WF_LENGTH = 56
	MAX_WF_LENGTH_LONG = 120

	# Port used by PlexNet on the machine to which the MAP is connected.
	# It can be set in the PlexNet options dialog.
	PLEXNET_PORT = 6000

	# PlexNet commands
	PLEXNET_CMD_SET_TRANSFER_MODE = 10000
	PLEXNET_CMD_START_DATA_PUMP = 10200
	PLEXNET_CMD_STOP_DATA_PUMP = 10300
	PLEXNET_CMD_DISCONNECT = 10999

	# PlexNet Packet size
	PACKETSIZE = 512

	#
	# Structure definitions -- these are string representations
	# of the c-structs defined in Plexon.h that can be used by the
	# struct module to pack and unpack binary data streams
	#
	# Fragile - don't mess with these unless you're sure you
	# know what you're doing!
	#

	fPL_Event = 'cccBLhhcccc'
	fPL_Wave = 'cccBLhhccc56h'
	fPL_WaveLong = 'cccBLhhcccc120h'
	fPL_FileHeader = 'Ii128siiiiiiiiiiiiiidccccHH48s650h650h512h'
	fPL_ChanHeader = '32s32siiiiiiiii320h5ii40hi43i'
	fPL_EventHeader = '32sii64i'
	fPL_SlowChannelHeader = '32siiiii61i'
	fPL_DataBlockHeader = 'hHLhhhh'
	fDigFileHeader = "iidiiiiiiii128sB64B191B"
