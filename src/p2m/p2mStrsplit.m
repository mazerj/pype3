function c = p2mStrsplit(str, delim)
%function c = p2mStrsplit(str, delim)
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

if nargin == 1
  delim = [char(9) ' '];               % tab and space
end
c = cell([1 length(str)]);
n = 1;
while ~isempty(str)
  [c{n} str] = strtok(str, delim);
  n = n + 1;
end
c = c(1:(n-1));
