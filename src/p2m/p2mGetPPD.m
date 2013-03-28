function ppd = p2mGetPPD(pf, recno)
%function ppd = p2mGetPPD(pf, recno)
%
%  In general, params.mon_ppd contains the ppd for each trial. For
%  some very old mac files, this value is not present in the data
%  file, but always has the value of 18.0 pixels/deg.
%
%
% <<part of pype/p2m toolbox>>
%
%Sun Mar  2 13:52:57 2003 mazer 

if ~exist('recno', 'var')
  recno = 1;
end

pf=p2mLoad(pf);

try
  ppd = pf.rec(recno).params.mon_ppd;
catch
  % VERY OLD FILES: no ppd info --> should be 18 pix/deg..
  ppd = 18;
end


