function y = p2mGauss1d(x, mu, sigma)
%function y = p2mGauss1d(x, mu, sigma)
%
% Wed Feb  7 12:10:38 2001 mazer 
%
% compute 1-D gaussian over range 'x' with
% mean 'mu' and deviation 'sigma'
%
%
% <<part of pype/p2m toolbox>>
%
% Wed Apr 18 14:57:03 2001 mazer
%  fixed sigma to be scaled properly

y = exp(-((x - mu) .^ 2) ./ (2*sigma^2)) ./ sqrt(2 * pi * sigma^2);
