function fname = pypefile(d)
%function fname = pypefile(d)
%
%  Ask user to select (existing) pype datafile. If no directory is
%  specified, look in current working dir. Cancel generates an error.
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

fname = uigetfile([d '*.*.[0-9][0-9][0-9]']);
if fname == 0
  error('no p2m file selected');
end
