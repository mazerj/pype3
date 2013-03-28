function p2mShow(pf, recno)
%function p2mShow(pf, recno)
%
%
% <<part of pype/p2m toolbox>>
%
%Mon Feb 24 00:52:09 2003 mazer 

pf=p2mLoad(pf);

nrec = length(pf.rec);
if ~exist('recno', 'var')
  recno = 1;
end

if recno < 1 | recno > nrec
  error('out of bounds');
end

[t, x, y, dx, dy, d, v, a, p] = p2mGetEyetrace(pf, recno);

plots = [];

ix = find(~isnan(x) & ~isnan(y));
nix = find(isnan(x) | isnan(y));

clf;

subplot(3,1,1);
plots(length(plots)+1) = gca;
m = mean(x(ix)) + zeros(size(nix));
set(plot(t, x, 'k-', t(nix), m, 'r.'), ...
    'markersize', 3);
ylabel('x (deg)');
axis tight

subplot(3,1,2);
plots(length(plots)+1) = gca;
m = mean(y(ix)) + zeros(size(nix));
set(plot(t, y, 'k-', t(nix), m, 'r.'), ...
    'markersize', 3);
ylabel('y (deg)');
axis tight

subplot(3,1,3);
plots(length(plots)+1) = gca;
if ~isempty(p)
  set(plot(t, p.^0.5, 'k-'), ...
      'markersize', 3);
else
  text(0.5, 0.5, 'NO PUPIL DATA');
end
ylabel('pupil (pix)');
axis tight

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
uicontrol('Style', 'pushbutton', 'Position', [x 5 w 20], ...
	  'String', 'z', ...
	  'UserData', 1, ...
	  'Callback', @zoom);
x = x + (w + dx);
uicontrol('Style', 'pushbutton', 'Position', [x 5 w 20], ...
	  'String', 'u', ...
	  'UserData', -1, ...
	  'Callback', @zoom);
x = x + (w + dx);
uicontrol('Style', 'pushbutton', 'Position', [x 5 w 20], ...
	  'String', 'c', ...
	  'Callback', @center);
x = x + (w + dx);
uicontrol('Style', 'pushbutton', 'Position', [x 5 w 20], ...
	  'String', '<-', ...
	  'UserData', -1, ...
	  'Callback', @shift);
x = x + (w + dx);
uicontrol('Style', 'pushbutton', 'Position', [x 5 w 20], ...
	  'String', '->', ...
	  'UserData', 1, ...
	  'Callback', @shift);

set(gcf, 'UserData', {pf recno plots}, 'DoubleBuffer', 'on');

%%%%%%%%%%%%% internal functions for the browser %%%%%%%%%%%%%%%%%%%%

function jump(varargin)
by = get(varargin{1}, 'UserData');
fig = get(varargin{1}, 'parent');
c = get(fig, 'userdata');
pf = c{1};
n = c{2};
n = n + by;
n = min(length(pf.rec), n);
n = max(1, n);
p = get(fig, 'pointer');
set(fig, 'pointer', 'watch');
p2mShow(pf, n);
set(fig, 'pointer', p);

function zoom(varargin)
dir = get(varargin{1}, 'UserData');
fig = get(varargin{1}, 'parent');
c = get(fig, 'userdata');
pf = c{1};
n = c{2};
plots = c{3};

subplot(plots(1))
ax=axis;
d = ax(2)-ax(1);
x1 = ax(1) + sign(dir)*0.25*d;
x2 = ax(2) - sign(dir)*0.25*d;
for n=1:length(plots)
  subplot(plots(n))
  xrange(x1, x2);
end

function shift(varargin)
dir = get(varargin{1}, 'UserData');
fig = get(varargin{1}, 'parent');
c = get(fig, 'userdata');
pf = c{1};
n = c{2};
plots = c{3};

subplot(plots(1))
ax=axis;
d = ax(2)-ax(1);
x1 = ax(1)+(sign(dir) * 0.10 * d);
x2 = ax(2)+(sign(dir) * 0.20 * d);
for n=1:length(plots)
  subplot(plots(n))
  xrange(x1, x2);
end

function center(varargin)
fig = get(varargin{1}, 'parent');
c = get(fig, 'userdata');
pf = c{1};
n = c{2};
plots = c{3};

subplot(plots(1))
[x1, y2] = ginput(1);
[x2, y2] = ginput(1);
for n=1:length(plots)
  subplot(plots(n))
  xrange(x1, x2);
end

