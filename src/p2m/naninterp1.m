function yi = naninterp1(x, y, xi)
%function yi = naninterp1(x, y, xi)
%
% interp1 with NaN warning's in Y disabled.
%
%
% <<part of pype/p2m toolbox>>
%
%Thu Jun  2 17:53:47 2011 mazer 

% disable interp1's warnings for NaN's in Y:
W = warning('off', 'MATLAB:interp1:NaNinY');

% do the interpolation:
yi = interp1(x, y, xi);

% restore old warning state:
warning(W.state, 'MATLAB:interp1:NaNinY');
