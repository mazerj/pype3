function b = ispypefile(obj)
%function b = ispypefile(obj)
%
%  Is argument a raw pype data file (not compressesed)?
%
%
% <<part of pype/p2m toolbox>>
%
%Mon Jun  1 13:27:54 2009 mazer 

if ischar(obj)
  b = regexp(obj, '[a-zA-Z].*[0-9][0-9][0-9][0-9]\..*\.[0-9][0-9][0-9]$');
else
  b = 0;
end
