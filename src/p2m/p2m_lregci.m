function [x, y, ye] = lregci(alpha, beta, x, y, npts)
%function [x, y, ye] = lregci(alpha, beta, x, y, npts)
%
% compute local confidence interval on linear regression results
% (orig matlab central: 55540-plot-confidence-interval-for-the-slope)
%
%INPUT
%  alpha - confidence pval (ie, 0.05 means plot 95% CI bands)
%  beta  - regression line (slope,intercept) -- if [], then fit it
%  x,y   - data
%  npts  - number of points to plot (default is 100)
%
%OUTPUT
%  x,y,ye - local CI estimates based on localized SEM
%

%creates two curves marking the 1 - ALPHA confidence interval for the
%regression line, given BETA coefficience (BETA(1) = intercept, BETA(2) =
%slope). This is the format of STATS.beta when using 
%STATS = REGSTATS(Y,X,'linear','beta');
%[TOP_INT, BOT_INT] = REGRESSION_LINE_CI(ALPHA,BETA,X,Y,N_PTS) defines the
%number of points at which the funnel plot is defined. Default = 100
%[TOP_INT, BOT_INT] = REGRESSION_LINE_CI(ALPHA,BETA,X,Y,N_PTS,XMIN,XMAX)
%defines the range of x values over which the funnel plot is defined

N = length(x);
if(length(x) ~= length(y))
    error(message('regression_line_ci:x and y size mismatch')); 
end

x_min = min(x);
x_max = max(x);
if ~exist('npts', 'var')
  npts = 100;
end

if isempty(beta)
  stats = regstats(y, x, 'linear', 'beta');
  beta = stats.beta;
end

% this is basically computing SE in bins..
X = x_min:(x_max-x_min)/npts:x_max;
Y = ones(size(X))*beta(1) + beta(2)*X;
SE_y_cond_x = sum((y - beta(1)*ones(size(y))-beta(2)*x).^2)/(N-2);
SSX = (N-1)*var(x);
SE_Y = SE_y_cond_x*(ones(size(X))*(1/N + (mean(x)^2)/SSX) + ...
                    (X.^2 - 2*mean(x)*X)/SSX);
Yoff = (2*finv(1-alpha,2,N-2)*SE_Y).^0.5;

% SE_b0 = SE_y_cond_x*sum(x.^2)/(N*SSX)
% sqrt(SE_b0)

if nargout == 0
  h = ishold;
  eshade(X, Y, Yoff, 0.7.*[1 1 1]);
  hold on;
  set(plot(x, y, 'ko'), 'markerfacecolor', 'r');
  xx = linspace(min(x), max(x), 2);
  plot(xx, beta(2).*xx+beta(1), 'r--');
  if ~h, hold off; end
end

x = X;
y = Y;
ye = Yoff;


