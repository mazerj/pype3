function fname = p2m_fname(fname)
%
% <<part of pype/p2m toolbox>>
%

% expand DATAROOT
if ~isempty(findstr(fname, '+')) & ~isempty(getenv('DATAROOT'))
  fname = strrep(fname, '+', getenv('DATAROOT'));
end

% expand HOME
if ~isempty(findstr(fname, '~')) & ~isempty(getenv('HOME'))
  fname = strrep(fname, '~', getenv('HOME'));
end
