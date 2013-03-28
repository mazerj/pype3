function p2mPlotEye(pf, recno, tmin, tmax, findfix)
%function p2mPlotEye(pf, recno, tmin, tmax, findfix)
%
%  Plot eye traces for nth trial in pf (from p2m).
%
%
% <<part of pype/p2m toolbox>>
%
%Mon Feb 17 16:53:20 2003 mazer 

pf=p2mLoad(pf);

nrec = length(pf.rec);

if ~exist('recno', 'var')
  recno = 1;
end
if recno < 0
  recno = -recno;
  browser = 0;
else
  browser = 1;
end

if ~exist('findfix', 'var')
  findfix = 1;
end

if recno < 1 | recno > nrec
  error('out of bounds');
end

plots = [];

[t, x, y, dx, dy, d, v, a, p] = p2mGetEyetrace(pf, recno);

if findfix
  fs = p2mFindSaccades(pf, recno);
end

subplot(5,1,1);
plots(length(plots)+1) = gca;

xix = find(isnan(x));
yix = find(isnan(y));
plot(t, x, 'r-', t, y, 'g-');
legend('xpos', 'ypos');
ylabel('position (deg)');
axis tight
  
if ~isempty(p)
  subplot(10,1,3);
  plots(length(plots)+1) = gca;
  plot(t, p.^0.5, 'k');
  ylabel('p-diam');
  axis tight

  subplot(10,1,4);
  plots(length(plots)+1) = gca;
else
  subplot(5,1,2);
  plots(length(plots)+1) = gca;
end  
  
ix = find(isnan(d));
plot(t, d, 'k-');
hold on;
set(plot(t(ix), nanmean(d)+zeros(size(ix)), 'r.'), 'markersize', 1);
hold off;
legend('pos', 'NaN');
ylabel('pos (deg)');
axis tight
  
subplot(5,1,3);
plots(length(plots)+1) = gca;
set(plot(t, x, 'k.'), 'markersize', 4);
if findfix
  hold on;
  for n=1:length(fs.fixOnsets)
    plot([fs.fixOnsets(n) fs.fixOffsets(n)], ...
	 [fs.fixX(n) fs.fixX(n)], 'r');
    text(mean([fs.fixOnsets(n) fs.fixOffsets(n)]), ...
	 fs.fixX(n)+2, sprintf('%d', n));
  end
  hold off;
end
ylabel('x pos (deg)');
axis tight

subplot(5,1,4);
plots(length(plots)+1) = gca;
set(plot(t, y, 'k.'), 'markersize', 4);
if findfix
  hold on;
  for n=1:length(fs.fixOnsets)
    plot([fs.fixOnsets(n) fs.fixOffsets(n)], ...
	 [fs.fixY(n) fs.fixY(n)], 'r');
    text(mean([fs.fixOnsets(n) fs.fixOffsets(n)]), ...
	 fs.fixY(n)+2, sprintf('%d', n));
  end
  hold off;
end
ylabel('y pos (deg)');
axis tight

if findfix
  subplot(5,3,5*3-2);
  plots(length(plots)+1) = gca;
  plot(fs.fixX, fs.fixY, 'o');
  xlabel('fix positions')
  axis image

  subplot(5,3,5*3-1);
  plots(length(plots)+1) = gca;
  hist((fs.fixOffsets-fs.fixOnsets)*1000);
  vline(nanmean((fs.fixOffsets-fs.fixOnsets)*1000));
  xlabel('fix dur (ms)')
  
  subplot(5,3,5*3-0);
  plots(length(plots)+1) = gca;
  hist((fs.sacOffsets-fs.sacOnsets)*1000);
  vline(nanmean((fs.sacOffsets-fs.sacOnsets)*1000));
  xlabel('sac dur (ms)')
else
  plots(length(plots)+1) = NaN;
  plots(length(plots)+1) = NaN;
  plots(length(plots)+1) = NaN;
end


ix = p2mFindEvents(pf, recno, 'fix_acquired');
for k=1:length(ix)
  t = pf.rec(recno).ev_t(ix(k)) / 1000;
  for n=1:(length(plots)-3)
    subplot(plots(n))
    vline(t);
  end
end

% if this is a fixation trial, try to indicate
% onset and offset of fixation -- this won't work
% for all pypefiles, but will for ztouchNN and
% variants..
ix = p2mFindEvents(pf, recno, 'fix_done');
if isempty(ix)
  ix = p2mFindEvents(pf, recno, 'fix_lost');
end
for k=1:length(ix)
  t = pf.rec(recno).ev_t(ix(k)) / 1000;
  for n=1:(length(plots)-3)
    subplot(plots(n))
    vline(t);
  end
end

if exist('tmin', 'var') & exist('tmax', 'var') & ...
      ~isempty(tmin) &  ~isempty(tmax)
  for n=1:(length(plots)-3)
    subplot(plots(n))
    xrange(tmin, tmax)
  end
end


subplot(plots(1));
try
  ical = pf.rec(1).eyecal;
catch
  ical = 0;
end
if ical
  ical = 'calibrated';
else
  ical = 'uncalibrated';
end
title(sprintf('%s:#%d (%s) ''%s''', ...
	      pf.src, recno, ical, pf.rec(recno).result));

if browser
  w = 40;

  dx = 5;
  x = dx;
  uicontrol('Style', 'pushbutton', 'Position', [x 5 w 20], ...
	    'String', '|<', ...
	    'UserData', -5000, ...
	    'Callback', @jump);
  x = x + (w + dx);
  uicontrol('Style', 'pushbutton', 'Position', [x 5 w 20], ...
	    'String', '<<', ...
	    'UserData', -10, ...
	    'Callback', @jump);
  x = x + (w + dx);
  uicontrol('Style', 'pushbutton', 'Position', [x 5 w 20], ...
	    'String', '<', ...
	    'UserData', -1, ...
	    'Callback', @jump);
  x = x + (w + dx);
  uicontrol('Style', 'pushbutton', 'Position', [x 5 w 20], ...
	    'String', '>', ...
	    'UserData', 1, ...
	    'Callback', @jump);
  x = x + (w + dx);
  uicontrol('Style', 'pushbutton', 'Position', [x 5 w 20], ...
	    'String', '>>', ...
	    'UserData', 10, ...
	    'Callback', @jump);
  x = x + (w + dx);
  uicontrol('Style', 'pushbutton', 'Position', [x 5 w 20], ...
	    'String', '>|', ...
	    'UserData', 5000, ...
	    'Callback', @jump);
  x = x + (w + dx);
  uicontrol('Style', 'checkbox', 'Position', [x 5 60 20], ...
	    'String', 'findfix', ...
	    'Value', findfix, ...
	    'Callback', @togFindfix);
  set(gcf, 'UserData', {pf recno findfix});
end

%%%%%%%%%%%%% internal functions for the browser %%%%%%%%%%%%%%%%%%%%

function togFindfix(varargin)
fig = get(varargin{1}, 'parent');
c = get(fig, 'userdata');
pf = c{1};
n = c{2};
ff = c{3};
ff = ~ff;
clf;
set(gcf, 'UserData', {pf n ff});
p = get(fig, 'pointer');
set(fig, 'pointer', 'watch');
p2mPlotEye(pf, n, [], [], ff);
set(fig, 'pointer', p);

function jump(varargin)
by = get(varargin{1}, 'UserData');
fig = get(varargin{1}, 'parent');
c = get(fig, 'userdata');
pf = c{1};
n = c{2};
ff = c{3};
n = n + by;
n = min(length(pf.rec), n);
n = max(1, n);
clf;
p = get(fig, 'pointer');
set(fig, 'pointer', 'watch');
p2mPlotEye(pf, n, [], [], ff);
set(fig, 'pointer', p);
