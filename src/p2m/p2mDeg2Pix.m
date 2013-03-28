function pix = p2mDeg2Pix(pf, ndeg)
%function pix = p2mDeg2Pix(pf, ndeg)
%
% warning: assumes H & V ppd are the same
%
%
% <<part of pype/p2m toolbox>>
%

pix = ndeg .* pf.rec(1).params.mon_ppd;
