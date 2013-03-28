#include <stdio.h>
#include <core_expt.h>



#define DURATION 20000 //20 seconds

int main(int argc, char ** argv)
{
	UINT32 st =0;
    if(open_eyelink_connection(0) !=0) // connect to the tracker
	{
		printf("Failed to connect to tracker \n");
		return 0;
	}
	
	eyecmd_printf("link_sample_data  = LEFT,RIGHT,GAZE"); // tell tracker to send data over the link
	eyecmd_printf("binocular_enabled =YES"); // enable binocular
	if(start_recording(1,1,1,1) != 0) 
	{
		printf("failed to start recording \n");
		return -1;
	}

	st = current_time();
	while(st+20000>current_time())
	{

		FSAMPLE sample;
		if(eyelink_newest_float_sample(&sample)>0) // get the newest sample
			printf("%f %f %f %f\n", sample.gx[0], sample.gy[0], sample.gx[1], sample.gy[1]); // print gaze data
		
	}
	
	stop_recording(); // stop recording
	close_eyelink_system(); // disconnect from tracker
	return 1;
   
}