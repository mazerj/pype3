function pf = p2mSelect(pf, channel, unit)
%function pf = p2mSelect(pf, channel, unit)
%
% Extract PlexNet spikes from channel/unit and stick them in spike_times
% so existing software can use the data unchanged.
%
% INPUT
%   pf = p2m data strcture
%   channel = electrode # (1-N)  --> specify -1 for TTL datastream
%   unit = sorted unit number (1-N)
% -OR-
%   channel = string with plexon-style specification, e.g. '005a',
%             or 'TTL' for revert back to TTL data
%
% OUTPUT
%   pf = modified pf data structure with the new spike times in place
%
% NOTE
%   this is only for old plexon datasets -- for anything else you
%   should probably be using the unispike toolbox
%
% <<part of pype/p2m toolbox>>
%
%Sun Dec  4 21:10:28 2005 mazer 
%
%Fri Oct 27 12:36:41 2006 mazer 
% added support for plexon-style channel specification...

if ~isfield(pf.rec(1), 'plx_times')
  error('p2mSelect for on-line integrated plexon files');
end

if nargin == 1
  l = [];
  for n = 1:length(pf.rec)
    for k = 1:length(pf.rec(n).plx_times)
      l = [l; pf.rec(n).plx_channels(k) pf.rec(n).plx_units(k)];
    end
  end
  l = unique(l, 'rows');
  for k = 1:size(l, 1)
    fprintf('chn %03d, unit %d <sig%03d%c>\n', ...
	    l(k,1), l(k,2), l(k,1), 96+l(k,2));
  end
  return
end

if nargin == 2
  if strcmpi(channel, 'TTL')
    channel = 0;
    unit = 0;
  else
    % single argument in plexon format: "005a", etc
    x = channel;
    channel = str2num(x(1:(end-1)));
    unit = x(end)-('a')+1;
  end
end

for n = 1:length(pf.rec)
  if channel >= 0
    ts = [];
    for k = 1:length(pf.rec(n).plx_times)
      if pf.rec(n).plx_channels(k) == channel && ...
	    pf.rec(n).plx_units(k) == unit
	ts = [ts pf.rec(n).plx_times(k)];
      end
    end
    pf.rec(n).spike_times = ts;
  else
    pf.rec(n).spike_times = pf.rec(n).ttl_times;
  end
end
  
