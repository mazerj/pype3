function fname = getf(wildcard)
%function fname = getf(wildcard)
%
%  Get a filename of an existing file using a dialog box.
%  Returns 0 if user selects CANCEL
%
%  **This is almost the same as p2m/getfile()**
%
% <<part of pype/p2m toolbox>>
%

if ~exist('wildcard', 'var'), wildcard='*'; end

[fname, p, ix] = uigetfile(wildcard);

if isstr(p)
  fname = [p fname];
end

