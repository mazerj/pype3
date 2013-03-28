function fname = getfile(d)
%function fname = getfile(d)
%
%  Ask user to select (existing) file. If no directory is
%  specified, look in current working dir. Cancel generates
%  an error.
%
%  **This is almost the same as p2m/getf()**
%
%
% <<part of pype/p2m toolbox>>
%

if nargin < 1
  d = '';
else
  if d(end) ~= '/'
    d = [d '/'];
  end
end

fname = uigetfile([d '*']);
if fname == 0
  error('no p2m file selected');
end
