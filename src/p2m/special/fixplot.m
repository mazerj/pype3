function fixplot(pf)

% for m0235:
xc=-14.9;
yc=-12.3;
r=8.8;
theta=atan2(yc, xc);

if length(pf.extradata) < 3
  issearch = ones([1 length(pf.rec)]);
else
  issearch = [];
  for n = 1:length(pf.rec)
    tt = pf.extradata{3+n}.data{1};
    if strcmp(tt, 'search');
      issearch(n) = 1;
    else
      issearch(n) = 0;
    end
  end
end
fprintf('%d search trials\n', sum(issearch));
t = 0;
for n = 1:length(pf.rec)
  if issearch(n) & length(pf.rec(n).eyet) > 0
    t = t + (pf.rec(n).eyet(end)-pf.rec(n).eyet(1));
  end
end
fprintf('%d s search data\n', round(t/1000));


d = [];
for n=1:length(pf.rec)
  fx = pf.fs{n}.fixX;
  fy = pf.fs{n}.fixY;
  sx = diff(fx);
  sy = diff(fy);

  subplot(3,1,1);
  set(plot(fx, fy, 'k.'), 'markersize', 1);
  hold on

  subplot(3,1,2);
  set(plot(sx, sy, 'k.'), 'markersize', 1);
  hold on
  
  d = [d 180.*atan2(sy, sx)./pi];
end
subplot(3,1,1);
axis image;
xrange(-30, 30);
yrange(-30, 30);
title({basename(pf.src) sprintf('n=%d', length(d))});
grid on;

z=pf.rec(1).rest{2};
xy=[];
for n=1:length(z)
  xy = [xy; z{n}{2} z{n}{3}];
end
xy=unique(xy,'rows');
ppd = p2mGetPPD(pf);
for n=1:size(xy,1)
  circle(xy(n,:)/ppd,pf.rec(1).params.smooth1/ppd);
end
hold off;

subplot(3,1,2);
axis image;
xrange(-30, 30);
yrange(-30, 30);
circle([xc yc], r, 'r-');
grid on;
hold off;

subplot(3,1,3);
set(rose(d), 'color', 'k', 'markerfacecolor', [0.5 0.5 0.5]);
r = axis;
r = r(2);
line([0 r*cos(theta)], [0 r*sin(theta)]);
axis image;
