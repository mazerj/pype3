function [x,y]=findcontour(x, y, z, level)
%function [x,y]=findcontour(x, y, z, level)
%
% Compute/extract a particular contour from an x,y,z dataset (say,
% the 50% contour from a receptive field map).
%
% INPUTS
%   x, y, z - surface data
%   level - z value to compute
%
% OUTPUT
%   x,y - points along the requested contour
%
% COMMENTS
%
% <<part of pype/p2m toolbox>>
%

c = contourc(x, y, z, [level level]);
[x, y] = c2xy(c);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [x, y] = c2xy(c)
x=[];
y=[];
n = 1;
while n < size(c, 2)
  a = n+1;
  b = a+c(2,n)-1;
  x = [x c(1, a:b)];
  y = [y c(2, a:b)];
  n = b+1;
end
x=x';
y=y';

