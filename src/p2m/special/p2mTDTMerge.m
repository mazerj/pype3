function pf = p2mTDTMerge(pf)
%function pf = p2mTDTMerge(pf)
%
% Merge TDT spike time data into pf structure. This actually uses an
% underlying python program to talk to the TDT TTank.X active-x
% component -- ttank.py server must be running on the tdt box..
%
% INPUT
%
%   pf = p2m data structure (from p2mLoad etc)
%
% OUTPUT
%
%   pf = new p2m data structure; function adds:
%        pf.rec(n).plx_times	spike times in pype-time ms
%        pf.rec(n).plx_channels spike channel number (1-based electrode #)
%        pf.rec(n).plx_units	spike unit number (1-based sort code)
%
%Tue Jan 22 14:33:32 2008 mazer 

tmp = tempname();
cmd = sprintf('tdtgetspikes.py -s "%s" -t "%s" -b "%s" >%s', ...
	      pf.rec(1).params.tdt_server, ...
	      pf.rec(1).params.tdt_tank, ...
	      pf.rec(1).params.tdt_block, ...
	      tmp);
[exitcode, result] = unix(cmd);
if exitcode ~= 0
  error(result);
end
m = load(tmp, '-ascii');
delete(tmp);
for n=1:length(pf.rec)
  % note trial numbers in tdtspikes output are 0-based!
  ix = find(m(:,1) == (n-1));
  pf.rec(n).plx_times = m(ix,2)';
  pf.rec(n).plx_channels = m(ix,3)';
  pf.rec(n).plx_units = m(ix,4)';
end

