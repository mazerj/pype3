function tf = p2mEyecalNeeded(pf, n)
%
% <<part of pype/p2m toolbox>>
%

tf = ~isfield(pf.rec(n), 'raweyex');
