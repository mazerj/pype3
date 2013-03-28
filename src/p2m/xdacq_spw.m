function [t, v, trial] = xdacq_spw(xd, trial, channel, unit)
%function [t, v, trial] = xdacq_spw(xd, trial, channel, unit)
%
% get spike wavforms specified trial, channel/electrode and unit
%
% INPUT
%   xd -- data structure returned by plx2mat()
%   trial -- trial number (1-based)
%   channel -- channel or electrode number (1-based)
%   unit -- unit number (0 for unsorted, 1=a, 2=b ..)
%
% OUTPUT
%   t -- time matrix [nspikes x spikelen] -- p2m-based timestamps in ms
%   v -- voltage matrix [nspikes x spikelen] -- p2m-based timestamps in ms
%   trial -- vector [nspikes] indicating trial # for each spike
%
%   if called with no output args, make a plot...
%
% SEE ALSO
%   plx2mat.py, xdacq_spk, xdacq_lfp
%
%
% <<part of pype/p2m toolbox>>
%
%Tue Jan  8 16:57:03 2008 mazer 

if nargin == 1
  colors = 'yrgbym';
  n = sum(xd.nunits > 0);
  nr = ceil(sqrt(n));
  nc = ceil(n/nr);

  n = 1;
  for c = 1:length(xd.nunits)
    if xd.nunits(c) > 0
      subplot(nr, nc, n);
      n = n + 1;
      h = [];
      names = {};
      for u = 0:xd.nunits(c)
	[t, v, trial] = xdacq_spw(xd, [], c, u);
	if isempty(t)
	  continue;
	end
	t = t(1,:) - t(1,1);
	l = plot(t, v', [colors(u+1) '-']);
	h = [h; l(1)];
	hold on;
	set(plot(t, mean(v), ['k' '-']), 'linewidth', 4);
	if u == 0
	  names{length(names)+1} = 'u';
	else
	  names{length(names)+1} = char(96+u);
	end
      end
      hold off;
      xlabel('time (ms)');
      ylabel('voltage (mv)');
      title(sprintf('sig%03d', c));
      legend(h, names);
    end
  end
  t = [];
  v = [];
  trial = [];
  return
end

if ~isempty(trial)
  ix = find((xd.spw.trial == trial) & ...
	    (xd.spw.channel == channel) & ...
	    (xd.spw.unit == unit));
else
  ix = find((xd.spw.channel == channel) & ...
	    (xd.spw.unit == unit));
end

if isempty(ix)
  t = [];
  v = [];
  trial = [];
  return;
end

v0 = xd.spw.volt(ix);

v = v0;
sniplen = find(isnan(v0)); sniplen = sniplen(1);
v = reshape(v, [sniplen size(v,1)/sniplen]);
v = v(1:(end-1),:)';

t = xd.spw.time(ix);
sniplen = find(isnan(v0)); sniplen = sniplen(1);
t = reshape(t, [sniplen size(t,1)/sniplen]);
t = t(1:(end-1),:)';


trial = xd.spw.trial(ix);
trial = trial(isnan(v0));

if nargout == 0
  t = t(1,:) - t(1,1);
  plot(t, v', 'k-', t, mean(v), 'r-');
  xlabel('ms');
  ylabel('voltage (arb)');
  title(sprintf('chan %d unit %d', channel, unit));
end


