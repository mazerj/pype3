function zvs(pf, recno)
%function zvs(pf, recno)
%
%  if recno < 0, then just init data structures -- load sprites,
%  background images and setup the framebuffer, etc..  Don't
%  actually do anything else.
% 
%Sat Mar  8 11:56:38 2003 mazer 


global fb patches bgimage
if recno < 0
  init = 1;
  recno = 1;
else
  init = 0;
end

nrec = length(pf.rec);
if ~exist('recno', 'var')
  recno = 1;
end

if recno < 1 | recno > nrec
  error('out of bounds');
end

P = pf.rec(recno).params;

if init
  framebuffer(round(100+1024), round(100+768));
  
  bgimage = sprite(imagefinder(P.bgimage, pf.src), 0, 0);
  %P.bgimage_dim = 0.80;
  if P.bgimage_dim ~= 0
    bgimage.im = 128 + (1-P.bgimage_dim) .* (bgimage.im-128);
  end
  fprintf('#');
  patches = {};
  for n = 1:size(P.X_files, 2)
    patches{n} = sprite(imagefinder(P.X_files{n}, pf.src), 0, 0);
    fprintf('.');
  end
  fprintf('\n');
end

if init
  return
end

%
% BUG: for zvs files -- first element of seq is
%      sample, then all others in one go -- duplicated
%      for each frame (thisframe didn't get reset!!!!)
%
%      used P.nstim to segment the list
%

% get sample first..

seq = P.X_seq;
f = seq{1};
t = f{1};
S = [0 t{1} t{2} t{3}];

% now parse out the rest...
g = seq{2};
ix = 1;
for frameno = 1:(size(g,2)/P.nstim)
  for patchno = 1:P.nstim
    t = g{ix};
    S = [S; frameno t{1} t{2} t{3}];
    ix = ix + 1;
  end
end

% find frame change times first
changes = [];

[ix,ts] = p2mFindEvents(pf, recno, 'sample_on');
changes = [changes ts];
[ix,ts] = p2mFindEvents(pf, recno, 'sample_off');
changes = [changes ts];
[ix,ts] = p2mFindEvents(pf, recno, 'targets_on');
changes = [changes ts];
[ix,ts] = p2mFindEvents(pf, recno, 'targets_off');
changes = [changes ts];

changes = sort(changes);

% frame number and copies of the frame buffer
fn = 1;
%F = zeros([size(fb.im,1) size(fb.im,2) 0]);

[t, x, y, dx, dy, d, v, a, p] = p2mGetEyetrace(pf, recno);

for frameno=0:max(S(:,1))
  fbclear(1,1,1);
  blit(bgimage);
  if frameno > 0
    % after sample onset, there's a delay..
    flip;
    %F(:,:,fn) = mean(fb.im, 3);
    note(-500, 395, 1, sprintf('Trial #%d', recno));
    note(-500, -395, 1, sprintf('Frame #%d D', round(fn/2)));
    note(500, -395, 0, sprintf('res=%s', pf.rec(recno).result(1)));
    note(500, 395, 0, basename(pf.src));
    eyetrace(pf, recno, changes(fn), changes(fn+1));
    drawnow;
    fn = fn + 1;
  end
  
  ix = find(S(:,1) == frameno);
  for n=ix'
    pn = 1+S(n,2);
    p = alpharing(patches{pn}, P.smooth1, P.smooth2);
    p = moveto(p, S(n,3), S(n,4));
    % is this the sample??
    if S(n,2) == S(1,2)
      p.im(p.d > 10 &  p.d < 15) = 1;
    end
    blit(p);
  end
  flip;
  %F(:,:,fn) = mean(fb.im, 3);
  eyetrace(pf, recno, changes(fn), changes(fn+1));
  note(-500, 395, 1, sprintf('Trial #%d', recno));
  note(-500, -395, 1, sprintf('Frame #%d T', round(fn/2)));
  note(500, -395, 0, sprintf('res=%s', pf.rec(recno).result(1)));
  note(500, 395, 0, basename(pf.src));
  eyetrace(pf, recno, changes(fn), changes(fn+1));
  drawnow;
  fn = fn + 1;
  
  oldfig = gcf;
  figure(2);
  
  t1 = changes(fn-1) / 1000;
  t2 = changes(fn) / 1000;
  ix = find(t >= t1 & t < t2);
  ft = t(ix);
  ft = ft - min(ft);
  fx = x(ix);
  fy = y(ix);

  subplot(2, 1, 1);
  plot(ft, fx, 'r', ft, fy, 'b');
  xrange(min(ft), max(ft));
  set(gca, 'color', 'none')
  legend('X', 'Y')
  xlabel('time (s)')
  ylabel('position (deg)');
  title(sprintf('%s, uncal, rec#%d, fr#%d', ...
		basename(pf.src), recno, round(fn/2)));
  keyboard
  figure(oldfig);
end

keyboard

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function eyetrace(pf, recno, t1, t2)
ix = find(pf.rec(recno).eyet >= t1 & ...
	  pf.rec(recno).eyet < t2);
x = pf.rec(recno).eyex(ix);
y = pf.rec(recno).eyey(ix);
x(abs(x) > (1024/2)) = NaN;
y(abs(x) > (768/2)) = NaN;
[x, y] = fbcoords(x, y);
hold on;
set(plot(x,y,'bo'),'markersize', 5, 'markerfacecolor', 'w');
set(plot(x(1),y(1),'gs'),'markersize', 5, 'markerfacecolor', 'g');
set(plot(x(end),y(end),'rs'),'markersize', 5, 'markerfacecolor', 'r');
hold off;


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function t = note(x, y, left, str)
[x, y] = fbcoords(x, y);
t = text(x, y, str);
if left
  ha = 'left';
else
  ha = 'right';
end
set(t, 'FontSize', 20, 'color', 'w', ...
       'HorizontalAlignment', ha, ...
       'VerticalAlignment', 'middle');

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


function imfile = imagefinder(imfile, src)

ix = find(src == '/');
imfile = [src(1:ix(end)) imfile];
