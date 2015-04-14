function pf = p2msummary(pf)

fprintf('%s\n', pf.src);

fprintf('\nCounts\n');
fprintf('-------------------\n');

for t = 'CEMUA'
  n = sum(arrayfun(@(x) x.result(1)==t, pf.rec));
  fprintf('  %s:   %3d  %3.0f%%\n', t, n, 100*n/length(pf.rec));
  if t == 'E'
    n = sum(arrayfun(@(x) strcmp(x.result, 'E FixBreak'), pf.rec));
    fprintf('   FB: %3d  %3.0f%%\n', n, 100*n/length(pf.rec));
  end
end
fprintf('ALL:   %3d\n', length(pf.rec));

fprintf('\nDurations\n');
fprintf('-------------------\n');
for t = 'CEMUA'
  fprintf('  %s meandur:   %.0fs\n', t, ...
          nanmean(arrayfun(@(x) ifel(x.result(1)==t, ...
                                     x.ev_t(end)-x.ev_t(2), NaN), ...
                           pf.rec)))
  if t == 'E'
    fprintf('   FB meandur: %.0fs\n', ...
            nanmean(arrayfun(@(x) ifel(strcmp(x.result, 'E FixBreak'), ...
                                       x.ev_t(end)-x.ev_t(2), NaN), pf.rec)));
  end
end

fprintf('\nTime series\n');
fprintf('-------------------\n');
fprintf('%s\n', arrayfun(@(x) x.result(1), pf.rec));


function r = ifel(cond, t, f)
if cond
  r = t;
else
  r = f;
end