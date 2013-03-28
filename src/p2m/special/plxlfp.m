function plxlfp(f, tnum)
%function plxlfp(f, tnum)
%
% generate quick plot of all the stored lfp channels in a plexon .plx
% file
%
%Wed Feb 20 15:34:26 2008 mazer 


x = plx2mat(f, 0, 1, 0);

if ~exist('tnum', 'var')
  % take last trial
  tnum = length(x.lfp_times)-1;
end

chans = x.lfp_chans{tnum};
t = x.lfp_times{tnum};
v = x.lfp_volts{tnum};

if isempty(t)
  error(sprintf('no lfp data for trial %d', tnum));
end

clist = unique(chans);

for n = 1:length(clist)
  subplot(length(clist), 1, n);
  ix = find(chans == (n-1));
  plot(t(ix), v(ix));
  ylabel(sprintf('#%d', n));
end
xlabel('time');

