function pypever = p2mver(pf)
%function pypever = p2mver(pf)
%
%  Get pype subversion revision number.
%
%
% <<part of pype/p2m toolbox>>
%

try
  pypever = pf.rec(1).params.PypeSvnRev;
catch
  pypever = NaN;
end
