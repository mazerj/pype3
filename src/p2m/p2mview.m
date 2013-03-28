function pypever = p2mview(pf, n, ROI)
%function pypever = p2mview(pf, n, ROI)
%
%  trial viewer -- playback engine
%
%
% <<part of pype/p2m toolbox>>
%

if ~exist('n', 'var')
  n = 1;
end

if ~exist('ROI', 'var')
  ROI = 400;
end

kincr = 1;
viewing = 1;
while viewing
  % x-t window
  subplot(5, 1, [4 5]);
  pts = gca;
  cla;
  plot(pf.rec(n).eyet, pf.rec(n).eyex, 'r-',  ...
       pf.rec(n).eyet, pf.rec(n).eyey, 'g-');
  hold on;
  axis tight;
  set(gca, 'YLim', [-ROI ROI]);
  yr = get(gca, 'YLim');
  xr = get(gca, 'XLim');
  yr(2) = 2*yr(2);
  xr(1) = 0;
  set(gca, 'XLim', xr, 'YLim', yr);
  progh = plot(0, 0, 'k^');
  set(progh, 'markerfacecolor', 'm');
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
  plot(pf.rec(n).eyex, pf.rec(n).eyey, 'b-');
  ylabel('time (ms)');
  ylabel('position (pix; 1deg grid)');
  hold on;
  solid(plot(pf.rec(n).eyex(1), pf.rec(n).eyey(1), 'go'));
  solid(plot(pf.rec(n).eyex(end), pf.rec(n).eyey(end), 'ro'));
  set(gca, 'XLim', [-ROI ROI], ...
           'YLim', [-ROI ROI]);
  axis square;
  grid on;
  
  th = linspace(-pi,pi);
  plot(pf.rec(n).params.win_size * cos(th), ...
       pf.rec(n).params.win_size * sin(th), 'k:');
  
  set(gca, 'ytick', (-10:10)*pf.rec(n).params.mon_v_ppd);
  set(gca, 'xtick', (-10:10)*pf.rec(n).params.mon_h_ppd);
  
  
  eyeh = plot(0, 0, 'ko');
  set(eyeh, 'markerfacecolor', 'y');
  tagh = text(0, 0, '');
  timeh = text(-0.90*ROI, 0.90*ROI, '');
  set(timeh, 'FontSize', 20, 'FontName', 'Courier');
  
  title(sprintf('%s %3d {\\bf %s}', ...
                pf.src, n, pf.rec(n).result));
  hold off;
  
  set(gcf, 'UserData', 0, 'WindowKeypressFcn', @click);
         
  looping = 1;
  set(pxy, 'Color', [.5 .7 .5]);
  while looping
    k = 1;
    while k < length(pf.rec(n).eyet)
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
          ROI = max(10, ROI / 2);
          set(pxy, 'XLim', [-ROI ROI], 'YLim', [-ROI ROI]);
          set(pts, 'YLim', [-ROI ROI]);
        case {'-'}
          ROI = ROI * 2;
          set(pxy, 'XLim', [-ROI ROI], 'YLim', [-ROI ROI]);
          set(pts, 'YLim', [-ROI ROI]);
      end
      
      ix = find(pf.rec(n).ev_t <= pf.rec(n).eyet(k));
      ix = ix(end);
      ev = strrep(pf.rec(n).ev_e{ix(1)}, '_', '{\_}');
      set(eyeh, 'XData', pf.rec(n).eyex(k), 'YData', pf.rec(n).eyey(k));
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