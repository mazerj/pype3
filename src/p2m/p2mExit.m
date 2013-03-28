function p2mExit(exitcode)
%
% <<part of pype/p2m toolbox>>
%

[pid, ppid, cmdline] = p2m_getpid;
f = fopen(sprintf('/tmp/%d.exit', ppid), 'w');
fprintf(f, '%d', exitcode);
fclose(f);
exit;
