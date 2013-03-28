function ical = p2mEyecal(pf, raw, startev, stopev1, stopev2)
%function ical = p2mEyecal(pf, startev, stopev1, stopev2)
%
% Compute and plot eye calibration information.  The
%
%  INPUT
%    pf = p2m datastructure
%    raw = work with raw data?
%    startev = (string) name of event when fixation starts;
%              defaults to 'fix_acquired'; [] for default
%    stopev1 = (string) name of event when fixation ends on
%              correct trials to 'fix_done'; [] for default
%    stopev2 = (string) name of event when fixation ends on
%              error trials to 'fix_lost'; [] for default
%
%  OUTPUT
%    ical = data structe containing calibration info that
%	 p2mEyecalApply() can use to calibrate other datafiles.
%
% For each trial, the program prints a result code on the console
% as it goes. Codes are as follows:
%  '.' = good trial/data point
%  'X' or 'x' = short trial, not enough data (trial excluded)
%  'a' = adjusted trial (raw=0 only); F8 (or equiv) occured; trial excluded)
%
%
% <<part of pype/p2m toolbox>>
%
%Thu Aug 10 14:50:25 2006 mazer
%  derrived from p2mEyecal2.m

pf=p2mLoad(pf);

outlierReject = 1;
oneStep = 0;	% calculate first pass gain & offset correct?
minfix = 0.5;	% minimum fixation duration we accept (secs)

if ~exist('raw', 'var')
  raw = 0;
end

if ~exist('startev', 'var')
  startev = [];
end
if ~exist('stopev1', 'var')
  stopev1 = [];
end
if ~exist('stopev2', 'var')
  stopev2 = [];
end

if isempty(startev)
  startev = 'fix_acquired';
end
if isempty(stopev1)
  stopev1 = 'fix_done';
end
if isempty(stopev2)
  stopev2 = 'fix_lost';
end

% interpolation method & resampling interval (pixels!!!)
method = 'linear';
res = 5;

ppd = p2mGetPPD(pf, 1);
nrec = length(pf.rec);

for recno=1:nrec
  try
    % ztouch and later files -- this is the recomended approach!
    fx(recno) = pf.rec(recno).params.fx / ppd;
    fy(recno) = pf.rec(recno).params.fy / ppd;
  catch
    % eyecalN files
    fx(recno) = pf.rec(recno).rest{1} / ppd;
    fy(recno) = pf.rec(recno).rest{2} / ppd;
  end
  
  ix = p2mFindEvents(pf, recno, startev);
  if isempty(ix)
    t1 = NaN;
  else
    t1 = pf.rec(recno).ev_t(ix(1));
  end

  ix = p2mFindEvents(pf, recno, stopev1);
  if isempty(ix)
    ix = p2mFindEvents(pf, recno, stopev2);
  end
  if isempty(ix)
    t2 = NaN;
  else
    t2 = pf.rec(recno).ev_t(ix(1));
  end

  if isnan(t1) | isnan(t2) | (t2 - t1) < minfix
    % this trial is too short to use..
    fprintf('X');
    mx(recno) = NaN;
    my(recno) = NaN;
  elseif (~raw & (recno+1) < length(pf.rec)) & ...
	(pf.rec(recno).params.INTeye_xgain ~= ...
	 pf.rec(recno+1).params.INTeye_xgain | ...
	 pf.rec(recno).params.INTeye_ygain ~= ...
	 pf.rec(recno+1).params.INTeye_ygain | ...
	 pf.rec(recno).params.INTeye_xoff ~= ...
	 pf.rec(recno+1).params.INTeye_xoff | ...
	 pf.rec(recno).params.INTeye_yoff ~= ...
	 pf.rec(recno+1).params.INTeye_yoff)
   % gain and/or offset changed between this trial and last, don't use
   % this data
   fprintf('a');
   mx(recno) = NaN;
   my(recno) = NaN;
  else
    if raw
      % request raw data:
      [t, x, y, dx, dy, d, v] = p2mGetEyetraceRaw(pf, recno, -1, -1, -1, -1);
      %% put gain back in:
      %x = x .* pf.rec(recno).params.INTeye_xgain;
      %y = y .* pf.rec(recno).params.INTeye_ygain;
    else
      [t, x, y, dx, dy, d, v] = p2mGetEyetraceRaw(pf, recno);
    end
    
    tms = t * 1000;
    % discard any time points where wither X or Y is NaN:
    ix1 = find(tms >= t1);
    ix2 = find(tms >= t2);
    if isempty(ix2)
      ix2 = length(tms);
    end
    xd = x(ix1(1):ix2(1));
    yd = y(ix1(1):ix2(1));
    ix = find(~isnan(xd) & ~isnan(yd));
    k1 = length(xd);
    xd = xd(ix);
    yd = yd(ix);
    k2 = length(xd);
    if k2 < k1
      % * indicates points were removed -- could be blink..
      fprintf('*');
    end
    if k2 > 100
      % need at least 100 samples (200-500ms)
      mx(recno) = mean(xd);
      my(recno) = mean(yd);
      fprintf('.');
    else
      % all points now gone, so no data from this trial..
      fprintf('x');
      mx(recno) = NaN;
      my(recno) = NaN;
    end
  end
end
fprintf('\n');

subplot(3,3,1);
plot(fx, fy, 'b.', mx, my, 'r.');
hold on;
reps = [];
k = 1;
for n=1:length(fx)
  if ~isnan(mx(n))
    plot([fx(n) mx(n)], [fy(n) my(n)], 'k-');
  end
end
hold on;
axis image;
grid;
title('raw: mx->fx (r:mx, b:fx)');

d = unique([fx' fy'], 'rows');
nreps = [];
for k=1:size(d,1)
  FX(k) = d(k,1);
  FY(k) = d(k,2);
  ix = find(fx == FX(k) & fy == FY(k));
  nreps(k) = length(ix);
  if ~isempty(ix)
    if outlierReject
      MX(k) = nanmedian(mx(ix));
      MY(k) = nanmedian(my(ix));
    else
      MX(k) = nanmean(mx(ix));
      MY(k) = nanmean(my(ix));
    end
  else
    MX(k) = NaN;
    MY(k) = NaN;
  end
end
fprintf('min reps = %f\n', min(nreps));
fprintf('max reps = %f\n', max(nreps));
fprintf('avg reps = %f\n', mean(nreps));
ix = find(~isnan(MX) & ~isnan(MY));
FX = FX(ix);
FY = FY(ix);
MX = MX(ix);
MY = MY(ix);

[xg, xoff] = p2m_fitline(FX, MX);
[yg, yoff] = p2m_fitline(FY, MY);

subplot(3,4,5);
[a, b] = p2m_lreg(FX, MX);
line([-20 20], [-20 20]);
axis image;
title('x raw');
grid;

subplot(3,4,7);
[a, b] = p2m_lreg(FY, MY);
line([-20 20], [-20 20]);
axis image;
title('y raw');
grid;

if oneStep
  xg = 1.0
  xoff = 0.0;
  yg = 1.0
  yoff = 0.0;
end

MX = (MX-xoff) ./ xg;
MY = (MY-yoff) ./ yg;


subplot(3,3,2);
plot(FX, FY, 'b.', MX, MY, 'r.');
hold on;
k = 1;
for n=1:length(FX)
  plot([FX(n) MX(n)], [FY(n) MY(n)], 'b-');
end
hold on;
axis image;
grid;
title('+gain correct: mx->fx');

subplot(3,3,3)
tags={};
for n=1:length(FX)
  tags{n} = sprintf('%.0f,%.0f', FX(n), FY(n));
end
% convert to polar coords to see rotation
mt = 180/pi .* atan2(MY, MX);
ft = 180/pi .* atan2(FY, FX);
% handle cases were ft=+179 and mt=-179, which are really
% very close, but cross the phase boundary.. just add 360
% to the smaller of each of these cases before computing
% the difference
ix = find(abs((mt-ft)) > 180);
for n=ix
  if mt(n) < ft(n)
    mt(n) = mt(n)+360;
  else
    ft(n) = ft(n)+360;
  end
end
plot(mt, ft, 'r.');
p2m_abline(1, 0);
title('rotation check');
axis tight;
axis image;

if 0
  % for debugging, this can be used to
  % track down outliers..
  f=gcf;
  figure;
  textplot(mt, ft, tags, 1);
  p2m_abline(1, 0);
  title('rotation');
  axis tight;
  axis image;
  figure(f);
end

subplot(3,4,6);
[a, b] = p2m_lreg(FX, MX);
line([-20 20], [-20 20]);
axis image;
title('x+gain correct');
grid;

subplot(3,4,8);
[a, b] = p2m_lreg(FY, MY);
line([-20 20], [-20 20]);
axis image;
title('y+gain correct');
grid;

X = -25:(res/ppd):25;
Y = -25:(res/ppd):25;
[gx, gy] = meshgrid(X, Y);
xo = griddata(MX, MY, FX, gx, gy, method);
yo = griddata(MX, MY, FY, gx, gy, method);

emin = min(unravel([xo-gx yo-gy]));
emax = max(unravel([xo-gx yo-gy]));

subplot(3,2,5);
imagesc(X, Y, xo-gx);
set(gca, 'YDir', 'normal');
axis image
title('x error');
caxis([emin emax]);
colormap([0.5 0.5 0.5; jet])
colorbar;

[xx, yy] = meshgrid(X, Y);
xx = (~isnan(xo-gx)) .* xx;
xrange(min(xx(:)), max(xx(:)));
yy = (~isnan(xo-gx)) .* yy;
yrange(min(yy(:)), max(yy(:)));
%axis equal

subplot(3,2,6);
imagesc(X, Y, yo-gy);
set(gca, 'YDir', 'normal');
axis image
title('y error');
caxis([emin emax]);
colormap([0.5 0.5 0.5; jet])
colorbar;

[xx, yy] = meshgrid(X, Y);
xx = (~isnan(yo-gy)) .* xx;
xrange(min(xx(:)), max(xx(:)));
yy = (~isnan(xo-gx)) .* yy;
yrange(min(yy(:)), max(yy(:)));
%axis equal

% first stage: gain & offsets
ical.xg = xg;
ical.xoff = xoff;
ical.yg = yg;
ical.yoff = yoff;

% second stage: interpolation
ical.mx = gx;
ical.my = gy;
ical.xo = xo;
ical.yo = yo;
ical.FX = FX;
ical.FY = FY;
ical.MX = MX;
ical.MY = MY;

ical.src = pf.src;
if raw
  banner(['RAW ' ical.src]);
else
  banner(ical.src);
end
