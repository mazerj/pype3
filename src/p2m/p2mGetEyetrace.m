function [t, x, y, dx, dy, d, v, a, p] = p2mGetEyetrace(pf, recno, ...
						  ns, sigma, tinterp)
%function [t, x, y, dx, dy, d, v, a, p] = p2mGetEyetrace(pf, recno,
%						ns, sigma, tinterp)
%
%  Extract and cleanup eyetrace record from p2m data structure.
%
%  INPUT
%    pf = p2m data struct
%    recno = record number (starting at 1)
%    (optional) ns = half-length of smoothing filter
%    (optional) sigma = std of Gaussian used for smoothing
%    (optional) tinterp = sampling interval for eye position data (-1=auto)
%
%  OUTPUT
%    t = time vector (in secs)
%    x = x position (deg)
%    y = y position (deg)
%    dx = x velocity (deg/s)
%    dy = y velocity (deg/s)
%    d = position re fovea (distance in deg)
%    v = simple overall velocity (deg/s)
%  OPTIONAL OUTPUT
%    a = acceleration profile (in deg/s/s)
%    p = pupil area, if available (in pixels)
%
%
% <<part of pype/p2m toolbox>>
%
%Tue Feb 18 11:12:41 2003 mazer 

pf=p2mLoad(pf);

if ~exist('ns', 'var') || ns < 0
  ns = 25;	% kernel length
end
if ~exist('sigma', 'var') || sigma < 0
  sigma = 5;	% kernel width
end

dt = round(2000*diff(pf.rec(recno).eyet))/2000; %round to .5ms; eye tracker runs at 1 KHz
if sum(dt > 1) > 10
  warning('GetEyetrace:ManyDropout', 'more than 10 dropouts (rec=%d)!', recno);
elseif max(dt) > 10
  warning('GetEyetrace:LongDrop', 'dropout > 10 ms (rec=%d)', recno);
end


% convert to seconds and degrees
ppd = p2mGetPPD(pf, recno);
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
if exist('tinterp', 'var') && tinterp > 0
  tstep = tinterp;
else
  z = diff(t);
  z = z(randperm(min(length(z), 1000)));
  z = z(z>0);
  tstep = median(z);
end

x = pf.rec(recno).eyex;
y = pf.rec(recno).eyey;
p = pf.rec(recno).eyep;

[ut, ix, ~] = unique(t);
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

x(abs(x) > (1024/1)) = NaN;
y(abs(y) > (1024/1)) = NaN;
x = x ./ ppd;
y = y ./ ppd;

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

