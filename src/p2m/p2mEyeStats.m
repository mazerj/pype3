function vthresh = p2mEyeStats(pf)
%function p2mEyeStats(pf)
%
%  Try to estimate the best threshold for identifying saccades.
%  This assumes that the velocity distribution should be bimodal.
%  The log-velocity distribution is fit with a sum of two independent
%  Gaussian and the different between the peaks uses as the
%  criterion value for saccades..
%
%  INPUT
%    pf = p2m data structure
%
%  OUTPUT
%   (side effect) = nice plot
%   vthresh = best estimate of saccade threshold in deg/s
%
%
% <<part of pype/p2m toolbox>>
%
%Mon Feb 17 16:53:20 2003 mazer 

pf=p2mLoad(pf);

nrec = length(pf.rec);

ppd = p2mGetPPD(pf, 1);
V = [];
for n = 1:nrec
  [t, x, y, dx, dy, d, v] = p2mGetEyetrace(pf, n);
  V = [V v];
end

z = abs(V);
z(z==0) = min(z(z>0))/10;

z = z(abs(z) < 500);

[n, x] = hist(abs(z), 50);
n = n ./ sum(n);
semilogx(x, n, 'ko-');
axis tight
yrange(0, 1);
set(gca, 'XTick', 10.^(0:5))
grid
xlabel('deg/s');
ylabel('frequency');
title('vel distribution');

xlabel('|velocity|');
ylabel('portion of samples');
title(pf.src);



