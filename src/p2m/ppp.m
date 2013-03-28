function ppp(pf, n, rawp)
%function ppp(pf, n, rawp)
%
%  pretty print params -- sorts & skips _raw_
%
%  INPUT
%      pf - pypefile
%       n - record number (default is 1)
%    rawp - show raw strings? (default is 0)
%
%  OUTPUT
%    none
%
%
% <<part of pype/p2m toolbox>>
%
%Fri Apr  1 14:46:31 2011 mazer 


if ~exist('n', 'var')
  n = 1;
end
if ~exist('rawp', 'var')
  rawp = 0;
end

f = sort(fieldnames(pf.rec(n).params));

ln = 0; for k = 1:length(f), ln = max(ln, length(f{k})); end

for k = 1:length(f)
  if rawp || ~strcmp(f{k}(max(1,length(f{k})-4:end)), '_raw_')
    fprintf(sprintf('%%-%ds: ', ln), f{k});
    try
      fprintf('%s\n', num2str(pf.rec(n).params.(f{k})));
    catch
      disp(pf.rec(n).params.(f{k}));
    end
  end
end



  
