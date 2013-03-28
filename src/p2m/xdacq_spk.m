function [t]= xdacq_spk(xd, trial, channel, unit)
%function [t] = xdacq_spk(xd, trial, channel, unit)
%
% get spike times specified trial and channel/electrode and unit
%
% INPUT
%   xd -- data structure returned by plx2mat()
%   trial -- trial number (1-based)
%   channel -- channel or electrode number (1-based)
%   unit -- unit (0 for unsorted, 1 for 'a' etc..)
%
% OUTPUT
%   t -- times in ms
%    note: if these are empty/[], then the specified channel
%          either doesn't exist in the datafile or generated
%          no spikes..
% SEE ALSO
%   plx2mat.py, xdacq_lfp, xdacq_spw
%
%
% <<part of pype/p2m toolbox>>
%
%Tue Jan  8 10:14:17 2008 mazer 

t = xd.spk_times{trial};
c = xd.spk_chans{trial};
u = xd.spk_units{trial};

t = t((c == channel) & (u == unit));
