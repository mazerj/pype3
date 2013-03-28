function [xmin, xmax, ymin, ymax] = bound(ical)
%function [xmin, xmax, ymin, ymax] = bound(ical)
%
%  Compute coarse boundaries of ical.
%
% <<part of pype/p2m toolbox>>
%
%Sun Feb 23 15:05:17 2003 mazer 

xo = ical.xo;
yo = ical.yo;
gx = ical.mx;
gy = ical.my;

X = sort(unique(gx(:)));
Y = sort(unique(gy(:)));

imagesc(X, Y, ~isnan(ical.xo .* ical.yo));
set(gca, 'YDir', 'normal');
colormap([1 1 1; 0 0 0])

x = sum((~isnan(xo)&~isnan(yo)),1);
ix = find(x > 0);
xmin=X(ix(1)-1);
xmax=X(ix(end)+1);

y = sum((~isnan(xo)&~isnan(yo)),2);
ix = find(y > 0);
ymin = Y(ix(1)-1);
ymax = Y(ix(end)+1);

vline(xmin, 'color', 'r');
vline(xmax, 'color', 'r');
hline(ymin, 'color', 'r');
hline(ymax, 'color', 'r');
grid;
