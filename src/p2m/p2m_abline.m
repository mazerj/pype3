function l = p2m_abline(a, b)
%function l = p2m_abline(a, b)
%
% Plot line on current axis with slope=a, y-intercept=b
%
%
% <<part of pype/p2m toolbox>>
%
%Sun Feb 23 09:37:46 2003 mazer 

ax = axis;
x = ax(1:2);
y = a.*x + b;
l = line(x, y);


