function t = filetype(fname)
%function t = filetype(fname)
%
% return filetype/extension for specified filename, or '' for
% no extension.
%

if ~any(fname == '.')
  t = '';
else
  t = p2mStrsplit(fname, '.');
  t = t{end};
end
