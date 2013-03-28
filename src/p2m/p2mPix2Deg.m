function deg = p2mPix2Deg(pf, npix)
%function deg = p2mPix2Deg(pf, npix)
%
% warning: assumes H & V ppd are the same
%
%
% <<part of pype/p2m toolbox>>
%

deg = npix ./ pf.rec(1).params.mon_ppd;
