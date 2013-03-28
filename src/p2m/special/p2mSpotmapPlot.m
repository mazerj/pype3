function p2mSpotmapPlot(pf, S, sigma)
%function p2mSpotmapPlot(pf, S)
%
%  Plot precomputed spotmap
%
%  INPUT
%    pf = p2m datastructure
%    S = p2mSpotmap() kernel
%
%  OUTPUT
%    None.
%
%Mon Mar  3 17:53:40 2003 mazer 

if ~exist('sigma', 'var')
  sigma = 0;
end

R = S.R;
Rt = S.Rt;
xv = S.xv;
yv = S.yv;
allstim = S.allstim;

binw = 16*3;
bins = sort([0:-binw:Rt(1)  binw:binw:Rt(end)]);

xmax = max(xv);
xmin = min(xv);
ymax = max(yv);
ymin = min(yv);
%[x, y] = meshgrid(xmin:2:xmax, ymin:2:ymax);
[x, y] = meshgrid(xv, yv);
xv = unique(x(:));
yv = unique(y(:));

K = zeros([length(yv) length(xv) 2 length(Rt)]);
for n=1:length(Rt)
  ix = find(allstim(:,3) == 0);
  z = R(ix,n);
  [xi, yi, zi] = griddata(allstim(ix,1), allstim(ix,2), z, x, y);
  K(:,:,1,n) = zi(:,:);
  
  ix = find(allstim(:,3) == 1);
  z = R(ix,n);
  [xi, yi, zi] = griddata(allstim(ix,1), allstim(ix,2), z, x, y);
  K(:,:,2,n) = zi(:,:);  
end

kmax = NaN;
for n=2:length(bins)
  ix = find(Rt >= bins(n-1) & Rt < bins(n));
  binsize = (bins(n) - bins(n-1)) / 1000;
  % K & R are in spikes/sec --> just normalize by binw to get s/sec
  on = sum(K(:,:,1,ix),4) ./ binsize;
  off = sum(K(:,:,2,ix), 4) / binsize;
  ksum = (on + off) ./ 2;
  kdiff = (on - off);
  kmax = max(kmax, max(max(on(:)), max(off(:))));
  
  subplot(4,length(bins),(length(bins)*0)+(n-1));
  if sigma>0
    on = smooth2d(on, 5, 5, sigma, 0);
  end
  imagesc(xv, yv, on);
  set(gca, 'ydir', 'normal');
  if n==2
    ylabel('ON');
    vline(0, 'color', 'w');
    hline(0, 'color', 'w');
  end
  title(sprintf('%d-%d', bins(n-1), bins(n)));

  subplot(4,length(bins),(length(bins)*1)+(n-1));
  if sigma>0
    off = smooth2d(off, 5, 5, sigma, 0);
  end
  imagesc(xv, yv, off);
  set(gca, 'ydir', 'normal');
  if n==2
    ylabel('OFF');
    vline(0, 'color', 'w');
    hline(0, 'color', 'w');
  end
  
  subplot(4,length(bins),(length(bins)*2)+(n-1));
  if sigma>0
    ksum = smooth2d(ksum, 5, 5, sigma, 0);
  end
  imagesc(xv, yv, ksum);
  set(gca, 'ydir', 'normal');
  if n==2
    ylabel('ON+OFF/2');
    vline(0, 'color', 'w');
    hline(0, 'color', 'w');
  end
  
  subplot(4,length(bins),(length(bins)*3)+(n-1));
  if sigma>0
    kdiff = smooth2d(kdiff, 5, 5, sigma, 0);
  end
  imagesc(xv, yv, kdiff);
  set(gca, 'ydir', 'normal');
  if n==2
    ylabel('ON-OFF');
    vline(0, 'color', 'w');
    hline(0, 'color', 'w');
  end
end

for n=2:length(bins)
  subplot(4,length(bins),(length(bins)*0)+(n-1));
  caxis([0 kmax]);
  axis square
  if n > 2
    axis off
  else
    colorbar;
  end

  subplot(4,length(bins),(length(bins)*1)+(n-1));
  caxis([0 kmax]);
  axis square
  if n > 2
    axis off
  else
    colorbar;
  end
  
  subplot(4,length(bins),(length(bins)*2)+(n-1));
  caxis([0 kmax]);
  axis square
  if n > 2
    axis off
  else
    colorbar;
  end
  
  subplot(4,length(bins),(length(bins)*3)+(n-1));
  caxis([0 kmax]);
  axis square
  if n > 2
    axis off
  else
    colorbar;
  end
end

banner(pf.src);
colormap(jet);
