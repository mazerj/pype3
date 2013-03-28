function [cellid, taskname, taskver, fileno] = p2mFileInfo(pf)
%function [cellid, taskname, taskver, fileno] = p2mFileInfo(pf)
%
%  Mine pf.src to get file information.
%
%  OUPUT:
%    cellid = string containing cell id (ie, 'm0225' etc)
%    taskname = string containg task name WITHOUT TRAILING NUMBER
%    taskver = version number for task
%    fileno = file number for this cell (sequence id)
%
%
% <<part of pype/p2m toolbox>>
%
%Sat Mar 22 13:18:06 2003 mazer 

pf=p2mLoad(pf);

x = strsplit(pf.src, '/');
fname = strrep(x{end}, '.gz', '');
x = strsplit(fname, '.');
cellid = x{1};
t = x{2};
for n=1:length(t)
  if (t(n) >= '0') & (t(n) < '9')
    break;
  end
end
taskname = t(1:(n-1));
taskver = str2num(t(n:end));
fileno = str2num(x{3});
