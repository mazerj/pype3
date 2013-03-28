function pf = p2mMerge(varargin)
%function pf = p2mMerge(varargin)
%
%  Combine p2m data structures from multiple runs into a single
%  structure. This is really just p2munimerge w/o the uni part..
%
%  This is similar to p2mCombine, but takes loaded pf structs
%  instead of filenames.
%
%INPUT
%  - list of p2m filenames or actual pf structs (from p2mLoad). These can
%    be passed as individual parameters: unimerge(pf1, pf2, ..., pfn) or as a
%    single cell array: unimerge(pflist);
%
%OUTPUT
%  pf - one giant pf data struct with all pf data
%
%NOTE
%  - Assumes uni files all have the same active channels.
%
%Mon Jan 14 15:04:20 2013 mazer - from myunimerge (without uni stuff)

pf.extradata = {};
pf.src = '';
pf.rec = [];

if nargin==1 && iscell(varargin{1})
  input = varargin{1};
else
  input = varargin;
end

for n = 1:length(input)
  p = input{n};
  
  if ischar(p)
    p = p2mLoad(p, [], 0);
  end
  fprintf('merging: %s (%d trials)\n', p.src, length(p.rec));
  
  pf.extradata{length(pf.extradata)+1} = p.extradata;
  if(isempty(pf.src))
      pf.src = p.src;
  else
      pf.src = [pf.src '+' p.src];
  end
  
  
  for j=1:length(p.rec)
    if isempty(pf.rec)
      pf.rec = p.rec(j);
    else
      pf.rec(length(pf.rec)+1) = p.rec(j);
    end
  end
end
