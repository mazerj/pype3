#ifndef _PLEXON_H_INCLUDED
#define _PLEXON_H_INCLUDED


///////////////////////////////////////////////////////////////////////////////
// Plexon Client API Definitions
///////////////////////////////////////////////////////////////////////////////


#define PL_SingleWFType         (1)
#define PL_StereotrodeWFType    (2)
#define PL_TetrodeWFType        (3)
#define PL_ExtEventType         (4)
#define PL_ADDataType           (5)
#define PL_StrobedExtChannel    (257)
#define PL_StartExtChannel      (258)
#define PL_StopExtChannel       (259)
#define PL_Pause                (260)
#define PL_Resume               (261)

#define MAX_WF_LENGTH           (56)
#define MAX_WF_LENGTH_LONG      (120)



// Ff the server closes connection, dll sends WM_CONNECTION_CLOSED message
// to hWndMain
#define WM_CONNECTION_CLOSED    (WM_USER + 401)



//
// PL_Event is used in PL_GetTimestampStructures(...)
//
struct PL_Event{
    char    Type;  // so far, PL_SingleWFType or PL_ExtEventType
    char    NumberOfBlocksInRecord;
    char    BlockNumberInRecord;
    unsigned char    UpperTS; // fifth byte of the waveform timestamp
    unsigned long    TimeStamp; // formerly just long
    short   Channel;
    short   Unit;
    char    DataType; // tetrode stuff, ignore for now
    char    NumberOfBlocksPerWaveform; // tetrode stuff, ignore for now
    char    BlockNumberForWaveform; // tetrode stuff, ignore for now
    char    NumberOfDataWords; // number of shorts (2-byte integers) that follow this header 
}; // 16 bytes


// the same PL_Event above with Waveform added
struct PL_Wave {
    char    Type;
    char    NumberOfBlocksInRecord;
    char    BlockNumberInRecord;
    unsigned char    UpperTS;
    unsigned long    TimeStamp;
    short   Channel;
    short   Unit;
    char    DataType; 
    char    NumberOfBlocksPerWaveform; 
    char    BlockNumberForWaveform; 
    char    NumberOfDataWords; // number of shorts (2-byte integers) that follow this header 
    short   WaveForm[MAX_WF_LENGTH];
}; // size should be 128


// extended version of PL_Wave for longer waveforms
struct PL_WaveLong {
    char    Type;
    char    NumberOfBlocksInRecord;
    char    BlockNumberInRecord;
    unsigned char    UpperTS;
    unsigned long    TimeStamp;
    short   Channel;
    short   Unit;
    char    DataType; 
    char    NumberOfBlocksPerWaveform; 
    char    BlockNumberForWaveform; 
    char    NumberOfDataWords; // number of shorts (2-byte integers) that follow this header 
    short   WaveForm[MAX_WF_LENGTH_LONG];
}; // size should be 256





// PL_InitClient - initialize client
// In: 
//		type  -- client type. SC registers with type = 256, electrode client with type = 1 
//		hWndList -- handle to the listbox type window.
//					if hWndList is not null,  PlexClient.dll will send 
//					LB_ADDSTRING messages with error or debug strings to this window
// Effect:
//		Initializes PlexClient.dll for a client. Opens MMF's and registers 
//					the client with the server.
//
extern "C" int      WINAPI PL_InitClient(int type, HWND hWndList);



// PL_InitClientEx2 - initialize client
// In: 
//		type  -- client type. SC registers with type = 256, electrode client with type = 1 
//		hWndMain -- handle to the main client window.
//					if hWndMain is not null, the server sends 
//					WM_COPYDATA broadcas messages to this window,  
// Effect:
//		Initializes PlexClient.dll for a client. Opens MMF's and registers 
//					the client with the server.
//
extern "C" int      WINAPI PL_InitClientEx2(int type, HWND hWndMain);


// PL_InitClientEx3 - initialize client
// In: 
//		type  -- client type. SC registers with type = 256, electrode client with type = 1 
//		hWndList -- handle to the listbox type window.
//					if hWndList is not null,  PlexClient.dll will send 
//					LB_ADDSTRING messages with error or debug strings to this window
//		hWndMain -- handle to the main client window.
//					if hWndMain is not null, the server sends 
//					WM_COPYDATA broadcas messages to this window,  
// Effect:
//		Initializes PlexClient.dll for a client. Opens MMF's and registers 
//					the client with the server.
extern "C" int      WINAPI PL_InitClientEx3(int type, HWND hWndList, HWND hWndMain);



// PL_CloseClient - closes client connection to the server
// Effect: 
//		Cleans up PlexClient.dll (deletes CClient object) and
//		Sends ClientDisconnected command to the server. 
//		The server decrements the counter for the number of connected clients 
extern "C" void     WINAPI PL_CloseClient();



// PL_IsLongWaveMode - is serevr using long wave mode? 
// Returns:
//		1, if the server uses long waves, 0 otherwise
// Effect: 
//		none
extern "C" int      WINAPI PL_IsLongWaveMode();




// PL_GetTimeStampArrays - get recent timestamps
// In: 
//		*pnmax  - maximum number of timestamps to transfer
// Out:
//      *pnmax - actual number of timestamps transfered
//		type - array of types (PL_SingleWFType, PL_ExtEventType or PL_ADDataType)
//		ch - array of channel numbers
//		cl - array of unit numbers
//		ts - array of timestamps
// Effect: 
//		Copies the timestamps that the server transferred to MMF since
//			any of the PL_GetTimeStamp* or PL_GetWave* was called last time
extern "C" void     WINAPI PL_GetTimeStampArrays(int* pnmax, short* type, short* ch,
                                              short* cl, int* ts);



// PL_GetTimeStampStructures - get recent timestamp structures
// In: 
//		*pnmax  - maximum number of timestamp structures to transfer
// Out:
//      *pnmax - actual number of timestamp structures transferred
//		events - array of PL_Event structures filled with new data
// Effect: 
//		Copies the timestamp structures that the server transferred to MMF since
//			any of the PL_GetTimeStamp* or PL_GetWave* was called last time
extern "C" void     WINAPI PL_GetTimeStampStructures(int* pnmax, 
                                                        PL_Event* events);




// PL_GetTimeStampStructuresEx - get recent timestamp structures
// In: 
//		*pnmax  - maximum number of timestamp structures to transfer
// Out:
//      *pnmax - actual number of timestamp structures transferred
//		events - array of PL_Event structures filled with new data
//      *pollhigh - high DWORD of the perf. counter at the time of HB poll
//      *pollhigh - low DWORD of the perf. counter at the time of HB poll
// Effect: 
//		Copies the timestamp structures that the server transferred to MMF since
//			any of the PL_GetTimeStamp* or PL_GetWave* was called last time
extern "C" void     WINAPI PL_GetTimeStampStructuresEx(int* pnmax, 
                                                    PL_Event* events,
                                                    int* pollhigh,
                                                    int* polllow);




// PL_GetWaveFormStructures - get recent waveform structures
// In: 
//		*pnmax  - maximum number of waveform structures to transfer
// Out:
//      *pnmax - actual number of waveform structures transferred
//		waves - array of PL_Wave structures filled with new data
// Effect: 
//		Copies the waveform structures that the server transferred to MMF since
//			any of the PL_GetTimeStamp* or PL_GetWave* was called last time
extern "C" void     WINAPI PL_GetWaveFormStructures(int* pnmax, 
                                                        PL_Wave* waves);



// PL_GetWaveFormStructuresEx - get recent waveform structures
// In: 
//		*pnmax  - maximum number of waveform structures to transfer
// Out:
//      *pnmax - actual number of waveform structures transferred
//		waves - array of PL_Wave structures filled with new data
//      *serverdropped - number of waveforms that were dropped in MXI transfer
//      *mmfdropped - number of waveforms that were dropped in MMF->client transfer
// Effect: 
//		Copies the waveform structures that the server transferred to MMF since
//			any of the PL_GetTimeStamp* or PL_GetWave* was called last time
extern "C" void     WINAPI PL_GetWaveFormStructuresEx(int* pnmax, 
                                        PL_Wave* waves, 
                                        int* serverdropped,
                                        int* mmfdropped);




// PL_GetLongWaveFormStructures - get recent long waveform structures
// In: 
//		*pnmax  - maximum number of waveform structures to transfer
// Out:
//      *pnmax - actual number of waveform structures transferred
//		waves - array of PL_WaveLong structures filled with new data
//      *serverdropped - number of waveforms that were dropped in MXI transfer
//      *mmfdropped - number of waveforms that were dropped in MMF->client transfer
// Effect: 
//		Copies the waveform structures that the server transferred to MMF since
//			any of the PL_GetTimeStamp* or PL_GetWave* was called last time
extern "C" void     WINAPI PL_GetLongWaveFormStructures(int* pnmax, 
                                        PL_WaveLong* waves, 
                                        int* serverdropped,
                                        int* mmfdropped);



// PL_GetWaveFormStructuresEx2 - get recent waveform structures
// In: 
//		*pnmax  - maximum number of waveform structures to transfer
// Out:
//      *pnmax - actual number of waveform structures transferred
//		waves - array of PL_Wave structures filled with new data
//      *serverdropped - number of waveforms that were dropped in MXI transfer
//      *mmfdropped - number of waveforms that were dropped in MMF->client transfer
//      *pollhigh - high DWORD of the perf. counter at the time of HB poll
//      *pollhigh - low DWORD of the perf. counter at the time of HB poll
// Effect: 
//		Copies the waveform structures that the server transferred to MMF since
//			any of the PL_GetTimeStamp* or PL_GetWave* was called last time
extern "C" void     WINAPI PL_GetWaveFormStructuresEx2(int* pnmax, PL_Wave* waves,
                                                  int* serverdropped, 
                                                  int* mmfdropped,
                                                  int* pollhigh,
                                                  int* polllow);



// PL_GetLongWaveFormStructuresEx2 - get recent long waveform structures
// In: 
//		*pnmax  - maximum number of waveform structures to transfer
// Out:
//      *pnmax - actual number of waveform structures transferred
//		waves - array of PL_WaveLong structures filled with new data
//      *serverdropped - number of waveforms that were dropped in MXI transfer
//      *mmfdropped - number of waveforms that were dropped in MMF->client transfer
//      *pollhigh - high DWORD of the perf. counter at the time of HB poll
//      *pollhigh - low DWORD of the perf. counter at the time of HB poll
// Effect: 
//		Copies the waveform structures that the server transferred to MMF since
//			any of the PL_GetTimeStamp* or PL_GetWave* was called last time
extern "C" void     WINAPI PL_GetLongWaveFormStructuresEx2(int* pnmax, PL_WaveLong* waves,
                                                  int* serverdropped, 
                                                  int* mmfdropped,
                                                  int* pollhigh,
                                                  int* polllow);





// "get" commands
extern "C" void     WINAPI PL_GetOUTInfo(int* out1, int* out2);
extern "C" void     WINAPI PL_GetSlowInfo(int* freq, int* channels, int* gains);
extern "C" void     WINAPI PL_GetSlowInfo64(int* freq, int* channels, int* gains);
extern "C" int      WINAPI PL_GetActiveChannel();
extern "C" int      WINAPI PL_IsElClientRunning();
extern "C" int      WINAPI PL_IsSortClientRunning();
extern "C" int      WINAPI PL_IsNIDAQEnabled();
extern "C" int      WINAPI PL_IsDSPProgramLoaded();
extern "C" int      WINAPI PL_GetTimeStampTick();
extern "C" void     WINAPI PL_GetGlobalPars(int* numch, int* npw, int* npre, int* gainmult);
extern "C" void     WINAPI PL_GetGlobalParsEx(int* numch, int* npw, int* npre, int* gainmult, int* maxwflength);
extern "C" void     WINAPI PL_GetChannelInfo(int* nsig, int* ndsp, int* nout);
extern "C" void     WINAPI PL_GetSIG(int* sig);
extern "C" void     WINAPI PL_GetFilter(int* filter);
extern "C" void     WINAPI PL_GetGain(int* gain);
extern "C" void     WINAPI PL_GetMethod(int* method);
extern "C" void     WINAPI PL_GetThreshold(int* thr);
extern "C" void     WINAPI PL_GetNumUnits(int* thr);
extern "C" void     WINAPI PL_GetTemplate(int ch, int unit, int* t);
extern "C" void     WINAPI PL_GetNPointsSort(int* t);
extern "C" int      WINAPI PL_SWHStatus();      // 1 if SWH board is present, otherwise 0
extern "C" int      WINAPI PL_GetPollingInterval();
extern "C" void     WINAPI PL_EnableExtLevelStartStop(int enable);
extern "C" int      WINAPI PL_IsNidaqServer();


// not implemented in the verison 09.98
extern "C" void     WINAPI PL_GetName(int ch1x, char* name);
extern "C" void     WINAPI PL_GetValidPCA(int* num);
extern "C" void     WINAPI PL_GetTemplateFit(int ch, int* fit);
extern "C" void     WINAPI PL_GetBoxes(int ch, int* b);
extern "C" void     WINAPI PL_GetPC(int ch, int unit, float* pc);
extern "C" void     WINAPI PL_GetMinMax(int ch,  float* mm);
extern "C" void     WINAPI PL_GetGlobalWFRate(int* t);
extern "C" void     WINAPI PL_GetWFRate(int* t);
extern "C" void     WINAPI PL_GetEventName(int ch1x, char* name);
extern "C" void     WINAPI PL_SetSlowChanName(int ch0x, char* name);
extern "C" void     WINAPI PL_GetSlowChanName(int ch0x, char* name);













///////////////////////////////////////////////////////////////////////////////
// Plexon .plx File Structure Definitions
///////////////////////////////////////////////////////////////////////////////


// file header (is followed by the channel descriptors)
struct  PL_FileHeader {
    unsigned int    MagicNumber; // = 0x58454c50;
    int     Version;
    char    Comment[128];
	int		ADFrequency; // Timestamp frequency in hertz
	int		NumDSPChannels; // Number of DSP channel headers in the file
	int		NumEventChannels; // Number of Event channel headers in the file
	int		NumSlowChannels; // Number of A/D channel headers in the file
	int		NumPointsWave; // Number of data points in waveform
	int		NumPointsPreThr; // Number of data points before crossing the threshold
	int		Year; // when the file was created
	int		Month; // when the file was created
	int		Day; // when the file was created
	int		Hour; // when the file was created
	int		Minute; // when the file was created
	int		Second; // when the file was created
    int     FastRead; // 0 - none, 1 - all short events, 2 - all waveforms
    int     WaveformFreq; // waveform sampling rate; ADFrequency above is timestamp freq 
    double  LastTimestamp; // duration of the experimental session, in ticks
    
    // New items are only valid if Version >= 103
    char    Trodalness;     // 1 for single, 2 for stereotrode, 4 for tetrode
    char    DataTrodalness;  // trodalness of the data representation

    char    BitsPerSpikeSample;     // ADC resolution for spike waveforms in bits (usually 12)
    char    BitsPerSlowSample;      // ADC resolution for slow-channel data in bits (usually 12)

    unsigned short SpikeMaxMagnitudeMV; // the zero-to-peak voltage in mV for spike waveform adc values (usually 3000)
    unsigned short SlowMaxMagnitudeMV;  // the zero-to-peak voltage in mV for slow-channel waveform adc values (usually 5000)
    

    char    Padding[48]; // so that this part of the header is 256 bytes
    
    
    // counters
    int     TSCounts[130][5]; // number of timestamps[channel][unit]
    int     WFCounts[130][5]; // number of waveforms[channel][unit]
    int     EVCounts[512];    // number of timestamps[event_number]
};


struct PL_ChanHeader {
    char    Name[32];
    char    SIGName[32];
    int     Channel;// DSP channel, 1-based
    int     WFRate; // w/f per sec divided by 10
    int     SIG;    // 1 - based
    int     Ref;    // ref sig, 1- based
    int     Gain;   // 1-32, actual gain divided by 1000
    int     Filter; // 0 or 1
    int     Threshold;  // +- 2048, a/d values
    int     Method; // 1 - boxes, 2 - templates
    int     NUnits; // number of sorted units
    short   Template[5][64]; // a/d values
    int     Fit[5];         // template fit 
    int     SortWidth;      // how many points to sort (template only)
    short   Boxes[5][2][4];
    int     SortBeg;
    int     Padding[43];
};

struct PL_EventHeader {
    char    Name[32];
    int     Channel;// input channel, 1-based
    int     IsFrameEvent; // frame start/stop signal
    int     Padding[64];
};

struct PL_SlowChannelHeader {
    char    Name[32];
    int     Channel;// input channel, 0-based
    int     ADFreq; 
    int     Gain;
    int     Enabled;
    int     PreAmpGain;
    int     Padding[61];
};

// the record header used in the datafile (*.plx)
// it is followed by NumberOfWaveforms*NumberOfWordsInWaveform
// short integers that represent the waveform(s)

struct PL_DataBlockHeader{
    short   Type;
    unsigned short   UpperByteOf5ByteTimestamp;
    unsigned long    TimeStamp;
    short   Channel;
    short   Unit;
    short   NumberOfWaveforms;
    short   NumberOfWordsInWaveform; 
}; // 16 bytes










///////////////////////////////////////////////////////////////////////////////
// Plexon continuous data file (.DDT) File Structure Definitions
///////////////////////////////////////////////////////////////////////////////

struct DigFileHeader {
    int     Version; // BitsPerSample field added in version 101, see below
    int     DataOffset;
    double  Freq;
    int     NChannels;
    int     Year;
    int     Month;
    int     Day;
    int     Hour;
    int     Minute;
    int     Second;
    int     Gain;  // as of version 102, this is the *preamp* gain, not NI gain
    char    Comment[128];
    unsigned char BitsPerSample; // added for ddt version 101
    // LFS 4/10/03 - added for version 102 - actual channel gains, not index
    unsigned char ChannelGain[64]; 
    unsigned char Padding[191];
};





#endif
