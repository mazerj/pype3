function p2mev(pf, recno)
%function p2mpp(pf, recno)
%
% pretty print just events data
%
% <<part of pype/p2m toolbox>>
%
%Thu Jun 27 10:49:40 2019 mazer 

if nargin < 3
  all = 0;
end

pf=p2mLoad(pf);

nrec = length(pf.rec);
if ~exist('recno', 'var')
  recno = 1;
end

if recno < 1 | recno > nrec
  error('out of bounds');
end


dt = NaN;
lastn = -1;
for n = 1:length(pf.rec(recno).ev_e)
  if ~all && strcmp(pf.rec(recno).ev_e{n}, 'INT_MARKFLIP')
    continue;
  end
  if lastn > 1
    dt = pf.rec(recno).ev_t(n) - pf.rec(recno).ev_t(lastn);
  end
  fprintf('%6d ms\t(%6dms)\t<%s>\n', ...
	  pf.rec(recno).ev_t(n), dt, pf.rec(recno).ev_e{n})
  lastn = n;
end
