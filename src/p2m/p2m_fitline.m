function [ a, b, estsema ] = p2m_fitline( abscissa, ordinate, outlierdist )
%function [ a, b, estsema ] = p2m_fitline( abscissa, ordinate, outlierdist )
%
%	[ a, b ] = p2m_fitline( abscissa, ordinate )
%	gives a and b such that a abscissa + b approximates ordinate 
%
%	[ a, b, estsema ] = p2m_fitline( abscissa, ordinate )
%	also gives you the estimated SEM of the slope a 
%
%	[ a, b ] = p2m_fitline( abscissa, ordinate, outlierdist )
%	is for robust estimation: it ignores points > outlierdist from line 
%
%	pred = p2m_fitline( abscissa, ordinate ) 
%	gives the predicted ordinate obtained from the fit.
%
%	if there are NaNs in the ordinate, it ignores them
%
%	Matteo 1995, 98
%
% <<part of pype/p2m toolbox>>
%



abscissa = abscissa(:);
ordinate = ordinate(:);

if length(abscissa)~=length(ordinate)
   error('Abscissa and ordinate must have same length');
end

notnans = find(~isnan(ordinate));
xx = abscissa(notnans);
yy = ordinate(notnans);

if length(xx)<=2
   pars = [ NaN; NaN ];
else
   pars = [ xx, ones(size(xx)) ] \ yy;
end

if nargout ==1,
   a = [ abscissa, ones(size(abscissa)) ] * pars;
else
   a = pars(1); b = pars(2);
end

if nargout == 3
   n = length(xx);
	foo = corrcoef(xx,yy);
	r = foo(1,2);
	estsema = var(yy)/var(xx)*(1-r^2)/(n-2);
end

if nargin == 3 & outlierdist>0 & outlierdist<inf
  ab = fmins( 'robustlineerror', ...
	      [ a b ], [], [], abscissa, ordinate, outlierdist );
  a = ab(1);
  b = ab(2);
  % robustlineerror([a b], abscissa, ordinate,outlierdist)
  % robustlineerror(ab, abscissa, ordinate,outlierdist)
end
