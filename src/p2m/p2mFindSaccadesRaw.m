function table = p2mFindSaccadesRaw(t0, x0, y0, nsigma)
%function p2mFindSaccadesRaw(t0, x0, y0)
%  Heuristic filter to find saccades in eyetraces.
%
%  INPUT
%    t, x, y: time & x, y position
%
%  OUTPUT (variable!!)
%    (a) if 'recno' is specfied, then returns a table of
%        fixation data for the specfied trial
%    (b) otherwise, returns a list of tables, for the entire
%        datafile, one entry for trial.
%    (c) with no output args at all, plots the results..
%
%    tables have the following members/rows:
%	recno:		record number
%	sacOnsets	saccade ONSET time (ms)
%	sacOffsets	saccade OFFSET time (ms)
%	fixOnsets	fixation ONSET time (ms)
%	fixOffsets	fixation OFFSET ONSET time (ms)
%	fixX		mean fixation X-position (deg)
%	fixY		mean fixation Y-position (deg)
%	fixD		mean fixation eccentricity (deg)
%
%
% <<part of pype/p2m toolbox>>
%
%
%Mon Feb 17 16:53:20 2003 mazer 
%
%Mon Mar 17 13:39:08 2003 mazer 
%
%   Modified to leave NaN's in place (and keep track of record #):
%
%
%                 /----------------\    f2
%   f1 ----------/                  \
%                                    \------------------  f3
%               a  b               c  d
%
%     a = saccade onset 1
%     b = saccade offset 1
%     c = saccade onset 2
%     d = saccade onset 3
%     f1,f2,f3 = fixation positions
%
%     if a or b are NaNs, then in means the current
%     fixation is invalid and the fixation one back,
%     namely f1 & f2.  If c or d are NaN's then f2
%     and f3 are invalid .. etc..
%
% Wed Jun 30 13:57:51 2004 mazer 
%
%  Separated from p2mFindSaccades.m to take x,y traces raw..
%

% make sure we're at 1khz, no gaps..
newt = min(t0):1:max(t0);
x0 = naninterp1(t0, x0, newt);
y0 = naninterp1(t0, y0, newt);
t0 = newt;

% use massive smoothing to calculate thresholds
ns = 25;
sigma = 10;

% minimum intersaccade interval allowed in secs
minISI = 50.0 / 1000.0;

% smooth trace
t = t0;
x = x0;
y = y0;

f = p2mGauss1d(-ns:ns, 0, sigma);
f = f ./ sum(f);
  
if length(f) > length(x)
  fprintf('Warning: Can''t smooth a trace shorted than smoother.\n');
  fprintf('  Just skipping smoothing on this (SHORT) trace.\n');
else
  x = conv2(x, f, 'valid');
  y = conv2(y, f, 'valid');
  k = (length(t)-length(x))/2;
  t = t(k:end-k-1);
end
d = ((x.^2) + (y.^2)).^0.5;
v = diff([NaN d]);
a = [NaN diff(v)];
athresh = nsigma * nanstd(a);

st = t;
sx = x;
sy = y;
sd = d;
sv = v;
sa = a;

% then revert to normal ploting thresholds
t = t0;
x = x0;
y = y0;
d = ((x.^2) + (y.^2)).^0.5;


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


sacs = [];
sacs_ix = [];

% look for saccade onsets:
%  -,-,+,+
tlen = length(t);
nmax = tlen-3;
for n = 1:nmax
  nn = min(n+3, length(a));
  s = a(n:nn) < athresh;
  if (length(s) == 4 & s == [1 1 0 0])
    sacs(length(sacs)+1) = t(n+1);
    sacs_ix(length(sacs_ix)+1) = n+1;
    while n < nmax
      s = a(n:n+3) < athresh;
      if (s == [0 0 1 1])
	break
      end
      n = n + 1;
    end
  end
end

sacOnsets = [];
sacOnsets_ix = [];
sacOffsets = [];
sacOffsets_ix = [];
fixOnsets = [];
fixOffsets = [];
fixX = [];
fixY = [];
fixD = [];

sn = 1;
for n=1:length(sacs)
  if n == 1 | ((sacs(n) - sacOnsets(end)) > minISI)
    sacOnsets(sn) = sacs(n);
    sacOnsets_ix(sn) = sacs_ix(n);
    sn = sn + 1;
  end
end

for sn=1:length(sacOnsets)
  t1 = sacOnsets_ix(sn);
  if sn < length(sacOnsets)
    t2 = sacOnsets_ix(sn+1)-4;
  else
    t2 = tlen-4;
  end
  sacOffsets(sn) = NaN;
  sacOffsets_ix(sn) = NaN;
  for n = t2:-1:t1
    if n < length(a)
      s = a((n-3):n) < athresh;
      if (s == [0 0 1 1])
	sacOffsets(sn) = t(n+1);
	sacOffsets_ix(sn) = n+1;
	break
      end
    end
  end
end

for sn=2:length(sacOnsets)
  if isnan(sacOnsets(sn)) | isnan(sacOffsets(sn)) | ...
	(sacOnsets(sn) - sacOffsets(sn-1)) < minISI
    sacOffsets(sn) = NaN;
    sacOffsets_ix(sn) = NaN;
    sacOnsets(sn) = NaN;
    sacOnsets_ix(sn) = NaN;
    sn = sn + 1;
  end
end

fn = 1;
for sn=1:length(sacOffsets)
  t1 = sacOffsets_ix(sn);
  if sn < length(sacOnsets)
    t2 = sacOnsets_ix(sn+1);
    fixOffsets(fn) = sacOnsets(sn+1);
  else
    t2 = length(d);
    fixOffsets(fn) = t(end);
  end
  if isnan(t1) | isnan(t2)
    fixX(fn) = NaN;
    fixY(fn) = NaN;
    fixD(fn) = NaN;
  else
    fixOnsets(fn) = sacOffsets(sn);
    fixX(fn) = mean(x(t1:t2));
    fixY(fn) = mean(y(t1:t2));
    fixD(fn) = mean(d(t1:t2));
    if isnan(fixX(fn)) | isnan(fixY(fn)) | isnan(fixD(fn))
      fixX(fn) = NaN;
      fixY(fn) = NaN;
      fixD(fn) = NaN;
    end
  end
  fn = fn + 1;
end

if nargout > 0
  table.recno = -1;
  table.sacOnsets = sacOnsets;
  table.sacOnsets = sacOnsets;
  table.sacOffsets = sacOffsets;
  table.fixOnsets = fixOnsets;
  table.fixOffsets = fixOffsets;
  table.fixX = fixX;
  table.fixY = fixY;
  table.fixD = fixD;
else
  subplot(4,1,1);
  set(plot(t, x, 'k.'), 'markersize', 4);
  hold on;
  set(plot(st, sx, 'g.'), 'markersize', 4);
  for n=1:length(fixOnsets)
    plot([fixOnsets(n) fixOffsets(n)], [fixX(n) fixX(n)], 'r');
    text(mean([fixOnsets(n) fixOffsets(n)]), fixX(n)+2, sprintf('%d', n));
  end
  hold off;
  ylabel('x pos (deg)');

  subplot(4,1,2);
  set(plot(t, y, 'k.'), 'markersize', 4);
  hold on;
  set(plot(st, sy, 'g.'), 'markersize', 4);
  for n=1:length(fixOnsets)
    plot([fixOnsets(n) fixOffsets(n)], [fixY(n) fixY(n)], 'r');
    text(mean([fixOnsets(n) fixOffsets(n)]), fixY(n)+2, sprintf('%d', n));
  end
  hold off;
  ylabel('y pos (deg)');

  subplot(4,1,3);
  set(plot(t, d, 'k.'), 'markersize', 4);
  hold on;
  set(plot(st, sd, 'g.'), 'markersize', 4);
  for n=1:length(fixOnsets)
    plot([fixOnsets(n) fixOffsets(n)], [fixD(n) fixD(n)], 'r');
    text(mean([fixOnsets(n) fixOffsets(n)]), fixD(n)+2, sprintf('%d', n));
  end
  hold off;
  ylabel('f-dist (deg)');
  
  subplot(4,3,12-2);
  plot(fixX, fixY, 'o');
  xlabel('fix positions')
  axis image

  subplot(4,3,12-1);
  hist((fixOffsets-fixOnsets)*1000);
  xlabel('fix dur (ms)')
  
  subplot(4,3,12-0);
  hist((sacOffsets-sacOnsets)*1000);
  xlabel('sac dur (ms)')
end
