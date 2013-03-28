function [t, v] = xdacq_lfp(xd, trial, channel)
%function [t, v] = xdacq_lfp(xd, trial, channel)
%
% get lfp signal for specified trial and channel/electrode
%
% INPUT
%   xd -- data structure returned by plx2mat()
%   trial -- trial number (1-based)
%   channel -- channel or electrode number (0-based)
%
% OUTPUT
%   t -- time in ms
%   v -- voltage trace
%    note: if these are empty/[], then the specified channel
%          doesn't exist in the datafile.
%
% SEE ALSO
%   plx2mat.py, xdacq_spk, xdacq_spw
%
%
% <<part of pype/p2m toolbox>>
%
%Tue Jan  8 10:14:17 2008 mazer 

t = xd.lfp_times{trial};
v = xd.lfp_volts{trial};
c = xd.lfp_chans{trial};

t = t(c == channel);
v = v(c == channel);
