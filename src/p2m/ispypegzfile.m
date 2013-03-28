function b = ispypegzfile(obj)
%function b = ispypegzfile(obj)
%
%  Is argument a compressed raw pype data file?
%
%
% <<part of pype/p2m toolbox>>
%
%Mon Jun  1 13:27:54 2009 mazer 

if ischar(obj)
  b = regexp(obj, '[a-zA-Z].*[0-9][0-9][0-9][0-9]\..*\.[0-9][0-9][0-9].gz$');
else
  b = 0;
end
