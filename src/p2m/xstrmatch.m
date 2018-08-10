function ix = xstrmatch(str, strs, exact)
%function xstrmatch(str, strs, [exact])
%
% Replacement for mathworks depreciated strmatch.m
%
% From MATLAB docs:
% 
% x = strmatch(str, strarray) looks through the rows of the character
% array or cell array of character vectors strarray to find character
% vectors that begin with the text contained in str, and returns the
% matching row indices. If strmatch does not find str in strarray, x is
% an empty matrix ([]). Any trailing space characters in str or strarray
% are ignored when matching. strmatch is fastest when strarray is a
% character array.
% 
% x = strmatch(str, strarray, 'exact') compares str with each row of
% strarray, looking for an exact match of the entire character
% vector. Any trailing space characters in str or strarray are
% ignored when matching.
% 

if nargin == 2, exact = 'prefix'; end

if strcmp(exact, 'exact')
  % equiv to: strmatch(str, strs, 'exact')
  ix = find(strcmp(str, strs));
else
  % equiv to: strmatch(str, strs)
  ix = find(strncmp(str, strs, length(str)));
end
