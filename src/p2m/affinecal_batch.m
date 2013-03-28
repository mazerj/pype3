function affinecal_batch(files)
%function affinecal_batch(files)
%
%  apply the affinecal() functio to a list of p2m files without
%  user intervention
%
% <<part of pype/p2m toolbox>>

bad = [];
for n = 1:length(files)
  out = strrep(strrep([files{n} '.aff'], '.gz', ''), '.p2m', '');
  fprintf(' in: %s\nout: %s\n', files{n}, out);
  pf = p2mLoad(files{n});
  try
    clf;
    affinecal(pf, out);
    drawnow;
  catch
    unix(sprintf('/bin/rm -f %s %s.ps', out, out));
    bad = [bad n];
  end
end

if length(bad) > 0
  fprintf('---------- failures -------------\n');
  for n=1:length(bad)
    fprintf('failed: %s\n', files{n});
  end
end

