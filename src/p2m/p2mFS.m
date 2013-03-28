function p2mFS(pf, n, start, stop)
%
% <<part of pype/p2m toolbox>>
%

range = 500;

nsig = 1.0;

t0 = pf.rec(n).eyet;
x0 = pf.rec(n).eyex;
y0 = pf.rec(n).eyey;

dec_to = pf.rec(1).params.eyefreq;       % decimate down to actual rate

t = t0(1):(1000/dec_to):t0(end);
x = naninterp1(t0, x0, t);
y = naninterp1(t0, y0, t);

% exclude off screen data
ix = abs(x) > range | abs(y) > range;
x(ix) = NaN;
y(ix) = NaN;

if ~exist('start', 'var') || isempty(start), start = t(1); end
if ~exist('stop', 'var') || isempty(stop), stop = t(end); end
ix = find(t >= start & t < stop);
t = t(ix); x = x(ix); y = y(ix);

fsigma = 40;
ft = 0:(1000/pf.rec(n).params.eyefreq):200;
ft = sort([-ft(2:end) ft]);
sf = exp(-(ft.^2) / (2.*fsigma.^2));

starts = [];
stops = [];

xy = ((x.^2)+(y.^2)).^0.5;
vel = abs([NaN diff(conv(xy, sf, 'same'))]);
acc = [NaN diff(conv(vel, sf, 'same'))];
acc2 = [NaN diff(conv(acc, sf, 'same'))];
thresh = nsig * nanstd(acc);

plot(t, xy, 'k-', t(acc>0), xy(acc>0), 'r.', ...
     t(acc<0), xy(acc<0), 'g.', ...
     t, vel, 'm-', ...
     t, acc, 'b-');
hold on;

ix = find([acc(1:end-1) >= thresh & acc(2:end) < thresh]);
starts = [starts t(ix)];
  
ix = find([acc(1:end-1) > -thresh & acc(2:end) <= -thresh]);
stops = [stops t(ix)];

for k = 1:length(starts), vline(starts(k)); end;
for k = 1:length(stops), vline(stops(k)); end;
hline(0);
hline(thresh);
hline(thresh);
hold off;


