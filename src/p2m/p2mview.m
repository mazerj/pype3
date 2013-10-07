function pypever = p2mview(pf, n, varargin)
%function pypever = p2mview(pf, n, ...options...)
%
%  trial viewer -- playback engine
%
%
% <<part of pype/p2m toolbox>>
%

opts.roi = 400;                         % zoom in on this region
opts.showevents = 0;                    % show encodes?
opts.start = '';                        % start event code
opts.stop = '';                         % stop event code

opts = getopts(opts, varargin{:});

if ~exist('n', 'var')
  n = 1;
end
if n < 1
  n = 1;
end

kincr = 1;
viewing = 1;
while viewing
  
  if isempty(opts.start)
    estart = 1;
  else
    [~, estart] = p2mFindEvents(pf, n, opts.start);
    if isempty(estart)
      estart = length(pf.rec(n).eyet);
    else
      estart = find(pf.rec(n).eyet >= estart);
      estart = estart(1)
    end
  end
  if isempty(opts.stop)
    estop = length(pf.rec(n).eyet);
  else
    [~, estop] = p2mFindEvents(pf, n, opts.stop);
    if isempty(estop)
      estop = length(pf.rec(n).eyet);
    else
      estop = find(pf.rec(n).eyet >= estop);
      estop = estop(1)
    end
  end
  
  % x-t window
  subplot(5, 1, [4 5]);
  pts = gca;
  cla;
  ix = estart:estop;
  plot(pf.rec(n).eyet(ix), pf.rec(n).eyex(ix), 'r-',  ...
       pf.rec(n).eyet(ix), pf.rec(n).eyey(ix), 'g-');
  hold on;
  axis tight;
  set(gca, 'YLim', [-opts.roi opts.roi]);
  yr = get(gca, 'YLim');
  xr = get(gca, 'XLim');
  yr(2) = 2*yr(2);
  xr(1) = 0;
  set(gca, 'XLim', xr, 'YLim', yr);
  progh = plot(0, 0, 'k^');
  set(progh, 'markerfacecolor', 'm');

  if opts.showevents
    evtlist = [];
    for k=1:length(pf.rec(n).ev_e)
      t = pf.rec(n).ev_t(k);
      ev = pf.rec(n).ev_e{k};
      ev = strrep(ev, '_', '{\_}');
      set(vline(t), 'linestyle', '-');
      if ~strcmp(ev(1:3), 'TOD')
        set(text(t, 0.40*yr(2), ev), 'rotation', 45);
        evtlist = [evtlist t];
      end
    end
  end
  hold off;
  
  % command window
  subplot(5, 3, [3 6 9]);
  cla;
  set(text(0, 1, {'    n: next', ...
                  '    p: prev', ...
                  '    q: quit', ...
                  '    +: zoom in', ...
                  '    -: zoom out', ...
                  '    s: slower', ...
                  '    f: faster', ...
                  'space: pause'}), ...
      'FontName', 'Courier', 'Fontsize', 15, 'VerticalAlignment', 'top');
  axis off;

  % x-y window
  subplot(5, 3, [1 2 4 5 7 8]);
  pxy = gca;
  plot(pf.rec(n).eyex(ix), pf.rec(n).eyey(ix), 'b-');
  ylabel('time (ms)');
  ylabel('position (pix; 10deg grid)');
  hold on;
  solid(plot(pf.rec(n).eyex(estart), pf.rec(n).eyey(estart), 'go'));
  solid(plot(pf.rec(n).eyex(estop), pf.rec(n).eyey(estop), 'ro'));
  set(gca, 'XLim', [-opts.roi opts.roi], ...
           'YLim', [-opts.roi opts.roi]);
  axis square;
  grid on;
  
  th = linspace(-pi,pi);
  plot(pf.rec(n).params.win_size * cos(th), ...
       pf.rec(n).params.win_size * sin(th), 'r-');

  % 10deg grid
  set(gca, 'ytick', round(100*(-10:10)*pf.rec(n).params.mon_v_ppd)/10);
  set(gca, 'xtick', round(100*(-10:10)*pf.rec(n).params.mon_h_ppd)/10);
  
  eyeh = plot(0, 0, 'ko');
  set(eyeh, 'markerfacecolor', 'y');
  tagh = text(0, 0, '');
  timeh = text(-0.90*opts.roi, 0.90*opts.roi, '');
  set(timeh, 'FontSize', 20, 'FontName', 'Courier');
  
  title(sprintf('%s %3d {\\bf %s}', ...
                pf.src, n, pf.rec(n).result));
  hold off;
  
  set(gcf, 'UserData', 0, 'WindowKeypressFcn', @click);
         
  looping = 1;
  %set(pxy, 'Color', [.5 .7 .5]);

  lastev = '';
  while looping
    k = estart;
    while k < estop
      c = get(gcf, 'UserData'); set(gcf, 'UserData', 0);
      switch c
        case {27, 'q', 'Q'}
          viewing = 0; looping = 0; break
        case ' '
          waitforbuttonpress;
        case {'s', 'S'}
          kincr = max(1, kincr - 1);
        case {'f', 'F'}
          kincr = kincr + 1;
        case {'n', 'N'}
          n = min(length(pf.rec), n + 1);
          looping = 0; break;
        case {'p', 'P'}
          n = max(1, n - 1);
          looping = 0; break;
        case {'+'}
          opts.roi = max(10, opts.roi / 2);
          set(pxy, 'XLim', [-opts.roi opts.roi], 'YLim', [-opts.roi opts.roi]);
          set(pts, 'YLim', [-opts.roi opts.roi]);
        case {'-'}
          opts.roi = opts.roi * 2;
          set(pxy, 'XLim', [-opts.roi opts.roi], 'YLim', [-opts.roi opts.roi]);
          set(pts, 'YLim', [-opts.roi opts.roi]);
      end
      
      ix = find(pf.rec(n).ev_t <= pf.rec(n).eyet(k));
      ix = ix(end);
      ev = strrep(pf.rec(n).ev_e{ix(1)}, '_', '{\_}');
      
      if length(ev) > 20
        ev = sprintf('%s...', ev(1:20));
      end
      
      if strcmp(ev(1:3), 'INT')
        ev = lastev;
      else
        lastev = ev;
      end
      
      set(eyeh, 'XData', pf.rec(n).eyex(k)+10, 'YData', pf.rec(n).eyey(k)+10);
      set(tagh, 'String', ev, ...
                'Position', [pf.rec(n).eyex(k)+30 pf.rec(n).eyey(k)+30 0]);
      set(timeh, 'String', sprintf('%5dms', round(pf.rec(n).eyet(k))));
      if 1
        set(progh, 'XData', pf.rec(n).eyet(k));
      end
      drawnow;
      k = k + kincr;
    end
  end
  set(pxy, 'Color', [1 1 1]);
end


function click(fig, arg)
set(fig, 'UserData', arg.Character)

function solid(hlist)
for h = hlist
  set(h, 'MarkerFaceColor', get(h, 'Color'));
end