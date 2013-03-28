function [ix, ts] = p2mFindEvents(pf, n, evname, exact)
%function [ix, ts] = p2mFindEvents(pf, n, evname, exact)
%
% Find events prefix-matching 'evname' in the nth record of pf.
%
% INPUT
%   pf = p2m data strcture
%   n = record number
%   evname = string to search for in event table
%   exact = use exact matching, instead of strmatch
%
% OUTPUT
%   ix = indices of matching events in pf.rec(n).ev_e/ev_t
%   ts = times (in ms!) of matching events.
%
%
% <<part of pype/p2m toolbox>>
%
%Thu Mar 27 22:18:31 2003 mazer 

pf=p2mLoad(pf);

if ~exist('exact', 'var')
  exact = 0;
end

if exact
  ix = strmatch(evname, pf.rec(n).ev_e, 'exact');
else
  ix = strmatch(evname, pf.rec(n).ev_e);
end
ts = pf.rec(n).ev_t(ix);
