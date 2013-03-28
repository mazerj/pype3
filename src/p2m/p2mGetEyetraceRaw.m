function [t, x, y, dx, dy, ...
	  d, v, a, p] = p2mGetEyetraceRaw(pf, recno, ...
					  ns, sigma, tinterp, ...
					  primary)
%function [t, x, y, dx, dy,
%	  d, v, a, p] = p2mGetEyetraceRaw(pf, recno, ...
%					  ns, sigma, tinterp, ...
%					  primary)
%
%  Extract and cleanup eyetrace record from p2m data structure.
%
%  INPUT
%    pf = p2m data struct
%    recno = record number (starting at 1)
%    (optional) ns = half-length of smoothing filter
%    (optional) sigma = std of Gaussian used for smoothing
%    (optional) tinterp = sampling interval for eye position data (-1=auto)
%    (optional) primary = type of RAW data to return:
%		 1: use eyex/y data as recorded
%		-1: use uncorrected (remove gain and offset) recorded eyepos
%		 0: use c0/c1 alternate datastream
%
%  OUTPUT
%    t = time vector (in secs)
%    x = x position (AD ticks)
%    y = y position (AD ticks)
%    dx = x velocity (AD ticks/s)
%    dy = y velocity (AD ticks/s)
%    d = position re fovea (distance in AD ticks)
%    v = simple overall velocity (AD ticks/s)
%  OPTIONAL OUTPUT
%    a = acceleration profile (in AD ticksdeg/s/s)
%    p = pupil area, if available (in pixels)
%
%
% <<part of pype/p2m toolbox>>
%
% Thu Jul  3 13:38:39 2003 mazer 
%   created
%
% Wed Aug  2 10:28:18 2006 mazer 
%   added primary=-1 to get back uncorrected tracker data (typically
%   the raw values from the eyelink).
% 

pf=p2mLoad(pf);

if ~exist('primary', 'var')
  primary = 1;
end

if ~exist('ns', 'var') | ns < 0
  ns = 25;	% kernel length
end
if ~exist('sigma', 'var') | sigma < 0
  sigma = 5;	% kernel width
end

dt = diff(pf.rec(recno).eyet);
if sum(dt > 1) > 10
  warning('more than 10 dropouts (rec=%d)!', recno);
elseif max(dt) > 10
  warning('dropout > 10 ms (rec=%d)', recno);
end

% convert to seconds and degrees
if 0
  ppd = p2mGetPPD(pf, recno);
end
t = pf.rec(recno).eyet / 1000.0;
if isempty(t)
  x = [];
  y = [];
  dx = [];
  dy = [];
  d = [];
  v = [];
  a = [];
  p = [];
  return
end;

% guess the sampling interval (in secs):
if exist('tinterp', 'var') & tinterp > 0
  tstep = tinterp;
else
  z = diff(t);
  z = z(randperm(min(length(z), 1000)));
  z = z(z>0);
  tstep = median(z);
end

if primary > 0
  x = pf.rec(recno).eyex;
  y = pf.rec(recno).eyey;
  p = pf.rec(recno).eyep;
elseif primary < 0
  % if primary is -1, then convert back to raw data from the tracker
  x = (pf.rec(recno).eyex + pf.rec(recno).params.INTeye_xoff) ./ ...
      pf.rec(recno).params.INTeye_xgain;
  y = (pf.rec(recno).eyey + pf.rec(recno).params.INTeye_yoff) ./ ...
      pf.rec(recno).params.INTeye_ygain;
  p = pf.rec(recno).eyep;
else
  x = pf.rec(recno).c0;
  y = pf.rec(recno).c1;
  p = pf.rec(recno).c4;
end

[ut, ix, jx] = unique(t);
if size(t,2) ~= size(ut,2)
  % duplicate t values in the dataset .. clean them up by just
  % taking the last sample in each run.  This is ugly, but should
  % be good enough for now
  t = t(ix);
  x = x(ix);
  y = y(ix);
  if ~isempty(p)
    p = p(ix);
  end
end

% recompute x,y,t by linear interpolation
% to fill in missing datapoints, if any..
newt = t(1):tstep:t(end);
x = naninterp1(t, x, newt);
y = naninterp1(t, y, newt);
% calc pupil area, if requested & available..
if ~isempty(p)
  p = naninterp1(t, p, newt);
end
t = newt;

if 0
  x(abs(x) > (1024/1)) = NaN;
  y(abs(y) > (1024/1)) = NaN;
  x = x ./ ppd;
  y = y ./ ppd;
end

if sigma > 0
  % smooth with Gaussian
  f = p2mGauss1d(-ns:ns, 0, sigma);
  f = f ./ sum(f);
  
  % If trace is shorter than the smoothing kernel, just print
  % a warning and skip smoothing.  This should almost never
  % happen...
  
  if length(f) > length(x)
    fprintf('Warning: Can''t smooth a trace shorted than smoother.\n');
    fprintf('  Just skipping smoothing on this (SHORT) trace.\n');
    fprintf('  file:  %s (rec #%d)\n', pf.src, recno);
  else
    x = conv2(x, f, 'valid');
    y = conv2(y, f, 'valid');
    k = (length(t)-length(x))/2;
    t = t(k:end-k-1);
    if ~isempty(p)
      p = p(k:end-k-1);
    end
  end
end

% finally compute velocity and distance traces

dx = diff([NaN x]) / tstep;
dy = diff([NaN y]) / tstep;

d = ((x.^2) + (y.^2)).^0.5;
v = diff([NaN d]) / tstep;

% calc acceleration, if requested
if nargout >= 8
  a = diff([NaN v]);
end

