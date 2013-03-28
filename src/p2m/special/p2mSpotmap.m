function rfinfo = p2mSpotmap(pf, params, save)
%function p2mSpotmap(pf)
%
%  Compute spotmap kernel from p2m file.
%
%  INPUT
%    pf = p2m datastructure
%
%  OUTPUT
%    ...None..
%
%Wed Mar 26 18:50:11 2003 mazer 

pf=p2mLoad(pf);

if ~exist('save', 'var');
  save = 0;
end


% Start with reasonable defaults for the options:
opts.start = 0;
opts.stop = 250;
opts.binsize = 32;
opts.tstep = 16;
opts.color = 0;
opts.contour = 1;
opts.smooth = 1;
% Now merge in the options supplied by the user in 'params'
if exist('params', 'var')
  if ~isempty(params)
    fn = fieldnames(params);
    for n = 1:length(fn)
      opts = setfield(opts, fn{n}, getfield(params, fn{n}));
    end
  end
end
opts

nrec = length(pf.rec);
ppd = p2mGetPPD(pf, 1);

S = [];
for recno=1:nrec
  [ix_on,ts_on]=p2mFindEvents(pf, recno, 'spot on');
  for n=1:length(ix_on)
    k = 1+size(S,1);
    ev = strsplit(pf.rec(recno).ev_e{ix_on(n)}, ' ');
    S(k, 1) = str2num(ev{3});
    S(k, 2) = str2num(ev{4});
    S(k, 3) = str2num(ev{5});
  end
end
S = unique(S, 'rows');

T = (opts.start-opts.binsize):1:(opts.stop+opts.binsize);
K = zeros([size(S, 1) size(T,2)]);
Kn = zeros([size(S, 1) size(T,2)]);

for recno=1:nrec
  fprintf('.');
  [ix_on,ts_on]=p2mFindEvents(pf, recno, 'spot on');
  [ix_off,ts_off]=p2mFindEvents(pf, recno, 'spot off');

  for n=1:length(ix_off)
    ev = strsplit(pf.rec(recno).ev_e{ix_on(n)}, ' ');
    x = str2num(ev{3});
    y = str2num(ev{4});
    p = str2num(ev{5});
    row = find(S(:,1)==x & S(:,2)==y & S(:,3)==p);
    
    for k=1:length(pf.rec(recno).spike_times)
      % spike time relative to spot onset
      st = pf.rec(recno).spike_times(k) - ts_on(n);
      v = (T==st);
      K(row, v) = K(row, v) + 1;
    end
    Kn(row, :) = Kn(row, :) + 1;
  end
end
fprintf('\n');
Kn(Kn == 0) = NaN;
K = K ./ Kn;

t = sort([(-(opts.tstep):-(opts.tstep):opts.start) ...
	  0:(opts.tstep):opts.stop]);
k = zeros([size(S, 1) size(t,2)]);
for n=1:size(t,2)
  t1 = t(n) - (opts.binsize/2);
  t2 = t(n) + (opts.binsize/2);
  ix = find(T >= t1 & T < t2);
  k(:, n) = 1000.* mean(K(:,ix),2) / length(ix);
end

xg = unique(S(:,1));
yg = unique(S(:,2));
pg = unique(S(:,3));


Z = NaN.*zeros([size(yg,1) size(xg,1) size(pg,1) size(t, 2)]);
for pn = 1:length(pg)
  for xn = 1:length(xg)
    for yn = 1:length(yg)
      row = find(S(:,1)==xg(xn) & S(:,2)==yg(yn) & S(:,3)==pg(pn));
      if ~isempty(row)
	Z(yn, xn, pn, :) = k(row, :);
      end
    end
  end
end

vmax = -1;
vmaxslice = NaN;
for k = 1:size(Z,4)
  slice = Z(:,:,:,k);
  v = var(slice(:));
  if v > vmax
    vmax = v;
    vmaxslice = k;
  end
end

% kernel weighting function:
% 1 0 -> off; 0 1 -> on; 0.5 0.5 -> on+off; -0.5 0.5 -> on-off
kw = [1 0; 0 1; 0.5 0.5; -0.5 0.5];

% figure out if on & off are the same -- if they are, then
% we should of the on+off kernel for rfinfo..
x = pf.rec(1).params.spot_on;
spoton = [];
for n=1:length(x)
  try
    spoton = [spoton x{n}];
  catch
    spoton = [spoton x];
  end
end

x = pf.rec(1).params.spot_off;
spotoff = [];
for n=1:length(x)
  try
    spotoff = [spotoff x{n}];
  catch
    spotoff = [spotoff x];
  end
end

samecol = 1;
if length(spoton) ~= length(spotoff)
  samcol = 0;
elseif sum(spoton ~= spotoff) > 0
  samecol = 0;
end

% figure out which of the 4 kernels (on,off etc) shows maximal
% tuning and use that one for RF position
knames = {'OFF' 'ON' 'ON+OFF' 'ON-OFF'};
rmaxslice = NaN;
if samecol
  rmaxslice = 3;
elseif ~isnan(vmaxslice)
  rmax = -1;
  rmaxslice = NaN;
  for k = 1:4
    slice = kw(k,1)*Z(:,:,1,vmaxslice) + kw(k,2)*Z(:,:,2,vmaxslice);
    v = var(slice(:));
    if v > rmax
      rmax = v;
      rmaxslice = k;
    end
  end
end

clf
n = size(t,2);
ncol = n+1;
nrow = 5;
sig = [nanmean(Z(:)) nanstd(Z(:))];
for k = 1:n
  subplot(nrow, ncol, k+(ncol*0));
  kp(yg, xg, 1*Z(:,:,1,k) + 0*Z(:,:,2,k), opts, ppd, sig);
  set(gca, 'ydir', 'normal');
  axis image;
  ylabel('off');
  if k > 1
    axis off;
  end
  if k == vmaxslice
    title(sprintf('*%dms', t(k)));
  else
    title(sprintf('%d', t(k)));
  end
  
  subplot(nrow, ncol, k+(ncol*1));
  kp(yg, xg, 0*Z(:,:,1,k) + 1*Z(:,:,2,k), opts, ppd, sig);
  set(gca, 'ydir', 'normal');
  axis image;
  ylabel('on');
  if k > 1
    axis off;
  end

  subplot(nrow, ncol, k+(ncol*2));
  kp(yg, xg, 0.5*Z(:,:,1,k) + 0.5*Z(:,:,2,k), opts, ppd, sig);
  set(gca, 'ydir', 'normal');
  axis image;
  ylabel('on+off');
  if k > 1
    axis off;
  end

  subplot(nrow, ncol, k+(ncol*3));
  kp(yg, xg, 1*Z(:,:,1,k) + -1*Z(:,:,2,k), opts, ppd, sig);
  set(gca, 'ydir', 'normal');
  axis image;
  ylabel('on-off');
  if k > 1
    axis off;
  end
end

c = [];
for k = 1:(nrow-1)
  for n = 1:(ncol-1)
    subplot(nrow, ncol, (k-1) * ncol + n)
    c = [c; caxis];
  end
end

for k = 1:(nrow-1)
  for n = 1:(ncol-1)
    subplot(nrow, ncol, (k-1) * ncol + n)
    caxis(max(c));
  end
end

if isnan(vmaxslice)
  % not enough data!
  fprintf('\nToo many NaN''s to fit\n');
  rinfo = [];
  return
end

for k = 1:4
  subplot(nrow, ncol, (k-1)*ncol+vmaxslice);
  z = kw(k,1)*Z(:,:,1,vmaxslice) + kw(k,2)*Z(:,:,2,vmaxslice);
  if opts.smooth > 0
    z = smooth2d(z, 3, 3, opts.smooth, 0);
  end
  z50 = mean([max(z(:)) min(z(:))]);
  [x, y] = findcontour(xg/ppd, yg/ppd, z, z50);
  hold on;
  c = fit_circ('fit', x, y);
  set(circle(c(1:2), c(3), 'k-'), 'linewidth', 2);
  set(circle(c(1:2), c(3), 'w:'), 'linewidth', 2);
  vline(c(1));
  hline(c(2));
  hold off;

  subplot(nrow, ncol, k*ncol);
  if k==rmaxslice
    s = '**************';
    rfinfo.rfx = c(1);
    rfinfo.rfy = c(2);
    rfinfo.rfr = c(3);
    rfinfo.rfe = (c(1).^2 + c(2).^2).^0.5;
    rfinfo.lat = t(vmaxslice);
    rfinfo.ppd = ppd;			% in case we want pixels later!!
  else
    s = '';
  end
  
  if k==1
    scol = sprintf('%d/', spotoff);
  elseif k==2
    scol = sprintf('%d/', spoton);
  else
    scol = '';
  end
  
  txt = text(0, 1, ...
	     {s ...
	      [knames{k} ' ' scol(1:(end-1))] ...
	      sprintf('(%.2f,%.2f) deg', c(1), c(2)) ...
	      sprintf('r=%.2f deg', c(3)) ...
	      sprintf('e=%.2f deg', (c(1).^2 + c(2).^2).^0.5) s});
  set(txt, 'VerticalAlignment', 'top');
  axis off
  box off;
end  
fprintf('\n');
  
subplot(nrow, 2, (2*nrow)-1);
y = 1000 * mean(K);
y = smooth1d(y, 5, 16);
plot(T, y, 'k-');
axis tight;
ylabel('hz');
xlabel('ms');
vline(0*pf.rec(1).params.spot_dur);
vline(1*pf.rec(1).params.spot_dur);
vline(2*pf.rec(1).params.spot_dur);

if ~isnan(vmaxslice)
  vline(t(vmaxslice), 'linestyle', '-', 'color', 'b');
end

rfinfo.spot_dur = pf.rec(1).params.spot_dur;
rfinfo.ir_t = T;			% and let's keep the impulse
rfinfo.ir_y = y;			% response function too

subplot(nrow, 2, (2*nrow));
txt = text(0, 1, ...
	   {basename(pf.src) ...
	    sprintf('binsize=%dms', opts.binsize) ...
	    sprintf('tstep=%dms', opts.tstep) ...
	    sprintf('smooth=%.1f (3x3 boxcar)', opts.smooth)});
set(txt, 'VerticalAlignment', 'top');
axis off
box off;

if (save)
  f = [strrep(pf.src, '.gz', '') '.ps'];
  o = orient;
  orient('landscape');
  print('-dps', f);
  orient(o);
  f = [strrep(pf.src, '.gz', '') '.rf'];
  fid = fopen(f, 'w');
  [cellid, taskname, taskver, fileno] = p2mFileInfo(pf);
  % units,cellid,rfx,rfy,rfr,rfe,lat,src;
  fprintf(fid, 'deg,%s,%03d,%f,%f,%f,%f,%d,%s\n', cellid, ...
	  fileno, ...
	  rfinfo.rfx, rfinfo.rfy, rfinfo.rfr, rfinfo.rfe, ...
	  rfinfo.lat, strrep(basename(pf.src), '.gz', ''));
  fclose(fid);
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%5

function kp(yg, xg, k, opts, ppd, sig)

try
  %imagesc(yg, xg, k);
  if opts.smooth > 0
    sk = ones([3 3]);
    sk = sk ./ sum(sk(:));
    k = conv2(k, sk, 'same');
  end
  if opts.contour
    contourf(xg/ppd, yg/ppd, k, 3);
  else
    imagesc(xg/ppd, yg/ppd, k);
    hold on;
    for n=-3:3
      c = sig(1)-n*sig(2);
      if n > 0
	contour(xg/ppd, yg/ppd, k, [c c], 'k-');
      else
	contour(xg/ppd, yg/ppd, k, [c c], 'k--');
      end
    end
    hold off;
  end
  
  fprintf('.');
  if opts.color
    colormap(hotcold(1));
  else
    colormap(1-gray(256));
  end
catch
  cla;
  text(0.5, 0.5, 'ND')
end

