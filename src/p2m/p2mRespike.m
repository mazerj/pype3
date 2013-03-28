function pf = p2mRespike(pf, thresh, polarity)
%function pf = p2mRespike(pf, thresh, polarity)
%
% Scan through an existing p2m file and use the raw_spike waveforms
% to find spikes in the raw_spike waveform. Compute new timestamps
% and replace them in the data structure. This is to repair files
% in which the spike_threshold or spike_polarity were set
% incorrectly.
%
% If you call this with just the pf arg, it will bring up an
% interactive plot of the raw spike waveforms and let you select
% a threshold and polarity with the mouse. It will then step
% through the trials showing you the results. Red dots are
% the new spike times, black dots are the old.
%
% INPUT
%   pf = p2m data strcture
%   thresh = user-defined new spike threshold
%   polarity = look for positive or negative going pulses
%
% OUTPUT
%   pf = modified pf data structure with the new spike times in place
%
%
% <<part of pype/p2m toolbox>>
%
%Thu Apr  1 11:03:33 2004 mazer 

if isfield(pf.rec(1), 'spike_times_orig')
  fprintf('Warning: this file has been previously Respiked\n');
end
  
if nargin < 3
  for n = 1:length(pf.rec)
    plot(pf.rec(n).eyet,pf.rec(n).raw_spike);
    xlabel('time (ms)')
    ylabel('voltage');
    hold on;
  end
  hold off;
  title('click to pick {\bf BASELINE}')
  [x, baseline] = ginput(1);
  title('click to pick {\bf THRESHOLD}')
  [x, thresh] = ginput(1);
  
  if thresh > baseline
    pf.polarity = 1;
  else
    pf.polarity = -1;
  end
  pf.thresh = round(thresh);
  view = 1;
else
  view = 0;
  pf.thresh = thresh;
  pf.polarity = polarity;
end
pf

for n = 1:length(pf.rec)
  % save old spike times first pass through.. this lets
  % you rethreshold several times without creaming the
  % original spike times detected by pype.
  if ~isfield(pf.rec(n), 'spike_times_orig')
    pf.rec(n).spike_times_orig = pf.rec(n).spike_times;
  end
  
  s = pf.rec(n).raw_spike;
  ds = [NaN diff(pf.rec(n).raw_spike)];
  ts = pf.rec(n).eyet(find((s > thresh) & ...
			   (sign(ds) == pf.polarity)));
  pf.rec(n).spike_times = ts;
  
  if view
    plot(pf.rec(n).eyet, s);
    hold on;
    plot(ts, thresh, 'ro');
    if ~isempty(pf.rec(n).spike_times_orig)
      plot(pf.rec(n).spike_times_orig, 0.90*thresh, 'ko');
    end
    hold off;
    xlabel('time (ms)')
    ylabel('voltage');
    axis tight;
    
    title('click to advance; any key to quit');
    
    [x, y, b] = ginput(1);
    if b > 3
      break
    end
  end
end
  
