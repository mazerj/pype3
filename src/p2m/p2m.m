% Tools for handling p2m file (aka matlab-based pype datafiles) 
%
%SHELL/PYTHON SCRIPTS --
% p2m                   - (shell) convert pypefiles to p2m files form cmd line
% affinecal             - (shell) front end for affinecal_batch.m
% p2m-ical              - (shell) generates .ical files (obsolete??)
% pypeinfo              - (python) dump param and events from pypefile
% showpypefile          - (python) pypenv shell with record loaded
%
%MATLAB SCRIPTS & FUNCTIONS --
% affinecal.m           - compute or apply affine calibration from fixation data
% affinecal_batch.m     - apply affine matrix to a bunch of datafiles
% banner.m              - add a banner ("supertitle") to a figure window
% bound.m               - find boundaries of an ical dataset
% cannonicalfname.m     - exandand filename into cannonical form
% chan.m                - get/set selected spike channel
% findcontour.m         - find single level contour in x,y,z dataset
% getf.m                - get filename from user
% getopts.m             - parse argument list as (name, value) pairs 
% isp2m.m               - test to see if var is a p2m data struct
% isp2mfile.m           - test to see if file is p2m datafile
% isp2mgzfile.m         - test to see if file is gzipped p2m datafile
% ispypefile.m          - test to see if file is python-based pype data file
% ispypegzfile.m        - test to see if file is gzipped pype data file
% p2mBatch.m            - pypefile->p2mfile interface (don't use)
% p2m_.m                - pypefile->p2mfile engine (don't use)
% p2mCombine.m          - merge a bunch of p2m files into a single p2m struct
% p2mExist.m            - check to see if file exists without following PATH
% p2mExit.m             - exit after writing exit code to /tmp/$PPID.exit
% p2mEyeStats.m         -
% p2mEyecal.m           -
% p2mEyecalApply.m      -
% p2mEyecalBatch.m      -
% p2mEyecalNeeded.m     -
% p2mEyecalUnapply.m    -
% p2mFileInfo.m         - get task info from PF struct
% p2mFindEvents.m       - find pype named events
% p2mFindFixes.m        - find fixations
% p2mFindSaccades.m     - ? find saccades
% p2mFindSaccadesRaw.m  - ? find saccades
% p2mFixDiode.m         - filter photodiode signal to exclude frame modulation
% p2mGauss1d.m          - generate 1-D Gaussian vector
% p2mGetEyetrace.m      - get eye processed trace data from
% p2mGetEyetraceRaw.m   - get eye un-processed trace data from
% p2mGetPPD.m           - query pixels-per-degree (PPD)
% p2mLoad.m             - load p2m file -- this is the preferred load method!
% p2mNoFalseSpikes.m    -
% p2mPlotEye.m          -
% p2mRespike.m          -
% p2mSave.m             - save p2m file
% p2mSelect.m           -
% p2mShow.m             - gui for viewing p2m file
% p2m_abline.m          -
% p2m_dir.m             -
% p2m_fitline.m         -
% p2m_fname.m           -
% p2m_getpid.m          -
% p2m_lreg.m            -
% p2mpp.m               - pretty print p2m record
% p2mset.m              - NOT DONE
% strsplit.m            - split string based on specified delimeter char
% xdacq_lfp.m           - obsolete?
% xdacq_spk.m           - obsolete?
% xdacq_spw.m           - obsolete?
%
%Fri Jan  7 15:23:11 2011 mazer 
