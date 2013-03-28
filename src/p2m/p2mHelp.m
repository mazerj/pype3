function p2mHelp()
%
% <<part of pype/p2m toolbox>>
%

fprintf('VISIBLE FUNCTIONS\n');
fprintf('-----------------\n');
fprintf('banner.m -- add header to plot window\n');
fprintf('p2m.m -- generate single p2m file\n');
fprintf('p2mLoad.m -- load p2m or ical file\n');
fprintf('p2mSave.m -- same p2m or ical file\n');
fprintf('p2mBatch.m -- generate p2m files in a batch\n');
fprintf('p2mGetPPD.m -- \n');
fprintf('p2mGetEyetrace.m -- \n');
fprintf('p2mGetEyetraceRaw.m -- \n');
fprintf('p2mEyecal2.m -- compute ical structure from eyecal data`run\n');
fprintf('p2mEyecalApply.m -- apply ical structure to single trial\n');
fprintf('p2mEyeStats.m -- estimate best guess for saccade vel threshold\n');
fprintf('p2mFindEvents.m -- \n');
fprintf('p2mFindFixes.m -- \n');
fprintf('p2mFindSaccades.m -- \n');
fprintf('p2mPlotEye.m -- \n');
fprintf('p2mShow.m -- interactive trial browser\n');
fprintf('p2mSpotmap.m -- revcor spotmap analysis\n');
fprintf('p2mSpotmapBatch.m -- \n');
fprintf('p2mSpotmapPlot.m -- \n');
  
fprintf('\n');
fprintf('INTERNAL FUNCTIONS\n');
fprintf('------------------\n');
fprintf('p2m_dir.m -- internal ls function\n');
fprintf('p2mExit.m -- generate exit code\n');
fprintf('p2mFileInfo.m -- get task info from src-filename\n');
fprintf('p2mEyecalUnapply.m -- \n');
fprintf('p2m_fitline.m -- \n');
fprintf('p2m_fname.m -- \n');
fprintf('p2m_abline.m -- plot regression line given slope & intercept\n');
fprintf('p2m_getpid.m -- \n');
fprintf('p2m_lreg.m -- \n');
fprintf('bound.m -- find the boundaries on an ical\n');
fprintf('cannonicalfname.m -- expand ~ etc to generate full pathname\n');
fprintf('findcontour.m -- get (x,y) points for one contour\n');
fprintf('getopts.m -- option parser; converts args to structure\n');

fprintf('\n');
fprintf('OBSOLETE FUNCTIONS\n');
fprintf('------------------\n');
fprintf('p2mEyecal.m -- old version of p2mEyecal2()\n');
  
