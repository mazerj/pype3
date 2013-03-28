function ex = p2mExist(fname)
%function ex = p2mExist(fname)
%
%  warning: built in EXIST (fname, 'file') walks the search path!!!!
%           this version does NOT!!
%
%
% <<part of pype/p2m toolbox>>
%
%Mon Nov  6 18:09:07 2006 mazer

if fname(1) ~= '/'
  fname = ['./' fname];
end
	   
fid = fopen(fname, 'r');
if fid < 0
  ex = 0;
else
  fclose(fid);
  ex = 1;
end
