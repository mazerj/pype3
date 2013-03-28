function [xo, yo, po, to] = p2mEyecalApply(pf, ical, n, inpix)
%
% <<part of pype/p2m toolbox>>
%

pf=p2mLoad(pf);

if ~exist('n', 'var')
  for n=1:length(pf.rec)
    if isfield(pf.rec(n), 'eyecal') & pf.rec(n).eyecal > 0
      fprintf('o');
    else
      [x, y, p, t] = p2mEyecalApply(pf, ical, n);
      pf.rec(n).raweyet = pf.rec(n).eyet;
      pf.rec(n).raweyex = pf.rec(n).eyex;
      pf.rec(n).raweyey = pf.rec(n).eyey;
      pf.rec(n).raweyep = pf.rec(n).eyep;
      pf.rec(n).eyet = t;
      pf.rec(n).eyex = x;
      pf.rec(n).eyey = y;
      pf.rec(n).eyep = p;
      pf.rec(n).eyecal = 1;
      pf.rec(n).icalsrc = ical.src;
      fprintf('.');
    end
  end
  fprintf('\n');
  xo = pf;
  return
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

method = 'linear';

[t, x, y, dx, dy, d, v, a, p] = p2mGetEyetrace(pf, n);

if ~exist('inpix', 'var')
  % default is return values in pixels & ms
  inpix = 1;
end

if isempty(x) | isempty(y)
  xo = [];
  yo = [];
  po = [];
  to = [];
  return;
end

if 0
  subplot(2,1,1)
  plot(x, 'k-');
  subplot(2,1,2)
  plot(y, 'k-');
end

% first stage:
x = (x-ical.xoff) ./ ical.xg;
y = (y-ical.yoff) ./ ical.yg;

if 0
  subplot(2,1,1)
  hold on; plot(x, 'r-'); hold off;
  subplot(2,1,2)
  hold on; plot(y, 'r-'); hold off;
end

ix = isnan(x) | isnan(y);
x(ix) = 0;
y(ix) = 0;

% second stage:
xo = interp2(ical.mx, ical.my, ical.xo, x, y, method);
yo = interp2(ical.mx, ical.my, ical.yo, x, y, method);

xo(ix) = NaN;
yo(ix) = NaN;

if 0
  subplot(2,1,1)
  hold on; plot(xo, 'g-'); hold off;
  subplot(2,1,2)
  hold on; plot(yo, 'g-'); hold off;
  drawnow
end

if inpix
  % convert x & y coords back to pixels
  ppd = p2mGetPPD(pf, 1);
  xo = xo * ppd;
  yo = yo * ppd;
  
  % and t back into ms
  to = t .* 1000.0;
else
  to = t;
end

% pupil area remains as is..
po = p;

