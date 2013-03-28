function pf = p2mEyecalUnapply(pf)
%function pf = p2mEyecalUnapply(pf)
%
%
% revert calibrated pf structure back to raw data
%
%
% <<part of pype/p2m toolbox>>
%
%Wed Mar 19 11:17:23 2003 mazer 

pf=p2mLoad(pf);

for n=1:length(pf.rec)
  if isfield(pf.rec(n), 'eyecal') & pf.rec(n).eyecal > 0
    pf.rec(n).eyet = pf.rec(n).raweyet;
    pf.rec(n).eyex = pf.rec(n).raweyex;
    pf.rec(n).eyey = pf.rec(n).raweyey;
    pf.rec(n).eyep = pf.rec(n).raweyep;

    rmfield(pf.rec(n), 'raweyet');
    rmfield(pf.rec(n), 'raweyex');
    rmfield(pf.rec(n), 'raweyey');
    rmfield(pf.rec(n), 'raweyep');
    rmfield(pf.rec(n), 'eyecal');
    rmfield(pf.rec(n), 'icalsrc');
    fprintf('.');
  else
    fprintf('o');
  end
  fprintf('\n');
end
