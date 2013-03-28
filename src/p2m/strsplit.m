function c = strsplit(s, delim)
%function c = strsplit(s, delim)
%
%  split string into token based on specified delimiter
%
% INPUT
%   s - string
%   delim - delimiting character (defaults to space)
%
% OUTPUT
%   c - cell array containing delimited tokens
%
% <<part of pype/p2m toolbox>>
%

if ~exist('delim', 'var')
  delim = ' ';
end

ix = [];
a = 1;
x = {};
for n=1:length(s)
  q = find(s(n) == delim);
  if ~isempty(q)
    b = n-1;
    x{length(x)+1} = s(a:b);
    a = n+1;
  end
end
x{length(x)+1} = s(a:end);
c = {};
for n=1:length(x)
  if ~isempty(x{n})
    c{length(c)+1} = x{n};
  end
end
