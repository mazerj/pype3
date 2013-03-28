function fname = p2mfile(d)
%function fname = p2mfile(d)
%
%  Ask user to select (existing) p2m file. If no directory is
%  specified, look in current working dir. Cancel generates an
%  error.
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

fname = uigetfile([d '*.p2m']);
if fname == 0
  error('no p2m file selected');
end
