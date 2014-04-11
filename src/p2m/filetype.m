function t = filetype(fname)
%function t = filetype(fname)
%
% return filetype/extension for specified filename, or '' for
% no extension.
%

if ~any(fname == '.')
  t = '';
else
  t = strsplit(fname, '.');
  t = t{end};
end
