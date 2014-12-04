function pf=p2mNoFalseSpikes(pf, verbose)
%function pf=p2mNoFalseSpikes(pf, verbose)
%
%  - Look for TTL spikes in a newly loaded datafile that occur right
%    after ADC starts and strip them out
%  - This is needed because pype's TTL-detection algorithm sometimes
%    gets confused and detects the onset of ADC as a spike. So the
%    first spike usually has a timestamp exactly equal to the onset
%    of ADC ('eye_start'). To be safe, this considers anyting within
%    +-5ms of the 'eye_start' signal gabarge.
%  - this should be called immediately after loading by p2mLoad(). Users
%    should never have to deal with this function directly
%
%
% <<part of pype/p2m toolbox>>
%
% Tue Jun  2 10:14:10 2009 mazer 

if nargin < 2
  verbose = 1;
end

ks=0;
kp=0;
for n=1:length(pf.rec)
  [ix, ts] = p2mFindEvents(pf,n,'eye_start');
  if length(ts)
    if length(pf.rec(n).spike_times) & abs(pf.rec(n).spike_times(1) - ts(1)) < 5
      % false spike detection
      pf.rec(n).spike_times = pf.rec(n).spike_times(2:end);
      try
        % old files don't have ttl_times...
        pf.rec(n).ttl_times = pf.rec(n).ttl_times(2:end);
      end
      ks = ks + 1;
    end
    if length(pf.rec(n).photo_times) & abs(pf.rec(n).photo_times(1) - ts(1)) < 5
      % false photo event detection
      pf.rec(n).photo_times = pf.rec(n).photo_times(2:end);
      kp = kp + 1;
    end
  end
end
if verbose
  if ks > 0
    fprintf('warning: removed %d false initial spikes\n', ks);
  end
  if kp > 0
    fprintf('warning: removed %d false initial photodiode events\n', kp);
  end
end
