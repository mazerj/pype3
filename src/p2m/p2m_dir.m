function files = p2m_dir(pat)
%function files = p2m_dir(pat)
%
%  p2m's private 'ls' function -- use this instead of matlab's DIR function!
%
% INPUT
%   pat - sh-stype glob expression
%
% OUTPUT
%   files - cell array of matching filenames (with attached
%           directory names).
%
% <<part of pype/p2m toolbox>>
%


[ecode, x] = unix(sprintf('/bin/ls -1 %s', pat));
files = {};
if ecode == 0
  nl = find(x == 10);
  a = 1;
  n = 1;
  for ix=1:length(nl)
    b = nl(ix)-1;
    files{n} = x(a:b);
    a = b + 2;
    n = n + 1;
  end
end

