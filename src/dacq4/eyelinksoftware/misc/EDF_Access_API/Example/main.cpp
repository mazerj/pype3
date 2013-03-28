#include "edf.h"
#include <iostream>
#include <sstream>
//#include "types.h"
//#include "eye.h"
//#include "trial.h"
#include <math.h>

using namespace std;
int main(int argc, char * argv[])
{
    
    EDFFILE *ed = NULL;
    bool active_trial = false;
    int err = 0;
    ed = edf_open_file(argv[1], 0, 1, 1, &err);
    if (ed == NULL)
      return false;
    char buf[1024] = "";
    edf_get_preamble_text(ed, buf, 1024);
    string header = buf;

    ALLF_DATA *fd = NULL;
    int cnt_skipped = 0;
    int cnt_all = 0;
    /* Check all messages and see if one is not NULL        */
    /* This only treats message events and ignores the rest */
    while (1)
    {        
        int type = edf_get_next_data(ed);
        switch (type)
        {            
            case MESSAGEEVENT:            
            {
                cnt_all++;
                fd = edf_get_float_data(ed);
                printf("%d %d %s \n", fd->fe.type, fd->fe.sttime, &(fd->fe.message->c));
		if(!fd->fe.message){
                    cerr << ".";
                    cnt_skipped ++ ;                    
                }
                break;
            }
            case NO_PENDING_ITEMS:
            {
                edf_close_file(ed);
                cout <<endl<< 100*(cnt_skipped / cnt_all) << "% were skipped" << endl;

                return true;
            }
            default:
                continue;
        }
    }
}

