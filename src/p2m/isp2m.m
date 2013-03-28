function b = isp2m(obj)
%function b = isp2m(obj)
%
%  Is argument a p2m data struct (from p2mLoad)?
%
%
% <<part of pype/p2m toolbox>>
%
%Mon Jun  1 13:27:54 2009 mazer 

if isstruct(obj) && isfield(obj, 'src')
  b = 1;
else
  b = 0;
end
