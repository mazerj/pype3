function [A, nex, ney] = affinecal(pf, A_or_outfile, EX, EY)
% function [cal, nex, ney] = affinecal(pf, A_or_outfile, EX, EY)
%
% Sun Apr 11 14:43:44 2004 mazer 
%  Given only a datafile (pf), compute and return the affine
%  transformation matrix required to map eyetrackker units into
%  affine-corrected eye position in degrees visual angle (DVA).
%
%  If A, EX and EY are provided (pf is no longer needed), just
%  apply the affine matrix to an existing set of eyetraces (x,y)
%  vectors and return the corrected eye trace.
%
%  A_or_outfile is either the precomputed transform matrix (A) or
%  the name of the file to write the matrix to for later use (outfile).
%  If outfile is specified, then a postscript version of the summary
%  plot is also saved..
%
%  usages:
%    A = affinecal(pf, 'savefile.aff');
%    A = affinecal('loadfile.aff');
%    [A, x, y] = affinecal([], A, x, y);
%
% <<part of pype/p2m toolbox>>

% if you want to skip dva and just work in pixels... change
% the following to 0:
dva = 1;

if ischar(pf)
  load(pf, '-mat');
  return;
end

if ~isempty(pf)
  if dva
    ppd = p2mGetPPD(pf);
  else
    ppd = 1;
  end

  fixes = []; EX = []; EY = []; FX = []; FY = [];

  f = [];
  for nr = 1:length(pf.rec)
    [ix1, ts1] = p2mFindEvents(pf, nr, 'fix_acquired');
    [ix2, ts2] = p2mFindEvents(pf, nr, 'fix_done');
    % trim a bit from the edges
    if ~isempty(ts1)
      ts1 = ts1 + 200;
      ts2 = ts2 - 200;
    end
    if ~isempty(ts1) & (ts2 - ts1) > 500
      % more than 500ms of data, this one's a keeper:
      n = 1+size(f,1);
      if isfield(pf.rec(nr).params, 'fx')
	fx = pf.rec(nr).params.fx / ppd;
	fy = pf.rec(nr).params.fy / ppd;
      else
	fx = pf.rec(nr).rest{1} / ppd;
	fy = pf.rec(nr).rest{2} / ppd;
      end
      fixes(n, 1) = fx;
      fixes(n, 2) = fy;
      
      ix = find(pf.rec(nr).eyet >= ts1 & pf.rec(nr).eyet < ts2);
      t = pf.rec(nr).eyet(ix);
      if isempty(pf.rec(nr).eyep)
	ep = [];
      else
	ep = pf.rec(nr).eyep(ix);
      end
      ex = pf.rec(nr).eyex(ix);
      ey = pf.rec(nr).eyey(ix);

      % cut out blinks (set to NaN), IF THERE'S PUPIL DATA!!!)
      if ~isempty(ep)
	for n=1:length(t)
	  if ep(n) < 500
	    % until eyelink stabilizes:
	    % ix = find(t > (t(n)-50) & t < (t(n)+200));
	    % until coil stabilizes:
	    ix = find(t > (t(n)-180) & t < (t(n)+275));
	    ep(ix) = NaN;
	    ex(ix) = NaN;
	    ey(ix) = NaN;
	  end
	end
      end

      EX = [EX nanmean(ex)];
      EY = [EY nanmean(ey)];
      FX = [FX fx];
      FY = [FY fy];
    end
  end
  
  % Given a set of veridical fixation points (the real target
  % locations) and a set of measured eye position values, compute
  % the affine transformation matrix (linear) that warps measured
  % eye positions onto veridical position...
  %
  % this combines: shift, scale, rotation and shear into a
  % single affine transform matrix (from fitaffine.cal)
  
  fixpoints = [FX; FY]';
  eyepos = [EX; EY]';  
  
  o = ones(size(fixpoints(:,1)));
  A.mat = [fixpoints o]' / [eyepos o]';
  A.src = pf.src;
  A.dva = dva;
  
  if exist('A_or_outfile', 'var')
    save(A_or_outfile, 'A');
  end
else
  A = A_or_outfile;
end

% make sure inputs are correct form (row vs col vectors.. I think :-)
if size(EX, 2) == 1
  % make sure inputs are correct form (row vs col vectors.. I think :-)
  EX=EX';
  EY=EY';
  trans = 1;
else
  trans = 0;
end

m = (A.mat * [[EX;EY]' ones([size(EX,2) 1])]')';
nex = m(:,1)';
ney = m(:,2)';

if trans
  nex = nex';
  ney = ney';
end

if ~isempty(pf)
  subplot(3,4,[1 2 5 6]);
  l = plot(FX, FY, 'ko', nex, ney, 'ro');
  set(l(1), 'markerfacecolor', 'k');
  legend('fixpoints', 'corrected gaze', 3);
  if dva
    xlabel('DVA');
    ylabel('DVA');
  else
    xlabel('pix');
    ylabel('pix');
  end
  title(pf.src);
  axis image;
  
  subplot(3,4,[3 4 7 8]);
  k = max([max(abs(EX)) max(abs(EY))]);
  [xin, yin] = meshgrid(linspace(-k, k, 10), linspace(-k, k, 10));
  [A, xout, yout] = affinecal([], A, xin(:), yin(:));
  l = plot(xin(:), yin(:), 'ko', ppd*xout, ppd*yout, 'ro');
  set(l(1), 'markerfacecolor', 'k');
  for n=1:length(xout)
    line([xin(n) ppd*xout(n)], [yin(n) ppd*yout(n)]);
  end
  legend('measured', 'veridical', 3);
  title(['affine eye calibration:' date]);

  axis image
  xlabel('pixels');
  ylabel('pixels');
  
  xer = FX-nex;
  yer = FY-ney;
  
  subplot(3,3,7)
  hist(xer);
  xrange(-max([abs(xer) abs(yer)]), max([abs(xer) abs(yer)]));
  %xrange(min([min(xer) min(yer)]), max([max(xer) max(yer)]));
  if dva
    xlabel('resid. x error (dva)');
  else
    xlabel('resid. x error (pix)');
  end

  subplot(3,3,8)
  hist(FY-ney);
  xrange(-max([abs(xer) abs(yer)]), max([abs(xer) abs(yer)]));
  %xrange(min([min(xer) min(yer)]), max([max(xer) max(yer)]));
  if dva
    xlabel('resid. y error (dva)');
  else
    xlabel('resid. y error (pix)');
  end
  
  t = {};
  t{1,1} = ' ';
  t{1,2} = 'x err';
  t{1,3} = 'y err';
  
  t{2,1} = 'mean';
  t{2,2} = mean(xer);
  t{2,3} = mean(yer);
  
  t{3,1} = 'std';
  t{3,2} = std(xer);
  t{3,3} = std(yer);

  subplot(3,3,9)
  cla;
  table(t, '%.2f');

  if exist('A_or_outfile', 'var')
    print('-dpsc', [A_or_outfile '.ps']);
  end
end
