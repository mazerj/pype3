function cn = cannonicalfname(f)
%function cn = cannonicalfname(f)
%
%  Return's the cannonical pathname for a file (useful for filenames
%  containing relative paths).
%
%
% <<part of pype/p2m toolbox>>
%
%Mon Feb 24 16:39:36 2003 mazer 

[s,w]=unix(sprintf('sh -c "cd `dirname %s` && pwd"', f));
dirname = w(1:end-1);
ix = find(f == '/');
if isempty(ix)
  cn = [dirname '/' f];
else
  cn = [dirname '/' f((ix(end)+1):end)];
end

