function [a, b] = p2m_lreg(x, y, style1, style2)
%function [a, b] = p2m_lreg(x, y, style1, style2)
%
%  simple linear regression - computes a and b, where y = ax + b
%
% INPUT
%   x, y - input data
%   style1 - marker style for datapoints
%   style2 - line style for regression line
%
% OUTPUT
%   a - repression slope
%   b - repression intercept
%
% <<part of pype/p2m toolbox>>
%

% get rid of any nan's first..
ix = ~isnan(x) & ~isnan(y);
x=x(ix);
y=y(ix);

[a, b] = p2m_fitline(x, y);
xe = [min(x) max(x)];
ye = (a * xe) + b;

if ~exist('style1')
  style1='ko';
end

if ~exist('style2')
  style2='r-';
end

if length(style1) > 0
  plot(x, y, style1);
end

if length(style2) > 0
  hold on;
  plot(xe, ye, style2);
  hold off;
end
