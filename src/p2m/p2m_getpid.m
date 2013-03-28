function [pid, ppid, cmdline] = p2m_getpid()
%
% <<part of pype/p2m toolbox>>
%
pid = [];
ppid = [];
cmdline = [];

f = fopen('/proc/self/status', 'r');
while 1
  l = fgets(f);
  if l == -1
    break
  end
  if strcmp(l(1:4), 'Pid:') == 1
    pid=sscanf(l, 'Pid:%d');
  elseif strcmp(l(1:5), 'PPid:') == 1
    ppid=sscanf(l, 'PPid:%d');
  end
end
fclose(f);


f = fopen('/proc/self/cmdline', 'r');
cmdline = fgets(f);
fclose(f);

