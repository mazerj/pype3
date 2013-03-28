function b = isp2mgzfile(obj)
%function b = isp2mgzfile(obj)
%
%  Is argument a compressed p2mLoad file?
%
%
% <<part of pype/p2m toolbox>>
%
%Mon Jun  1 13:27:54 2009 mazer

if ischar(obj)
  b = regexp(obj, '.*p2m.gz$');
else
  b = 0;
end
