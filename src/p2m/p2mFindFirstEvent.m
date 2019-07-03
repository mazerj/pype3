function [ix, ts] = p2mFindFirstEvent(varargin)
% function [ix, ts] = p2mFindFirstEvent(varargin)
%
% like p2mFindEvents, but just first event - this is
% useful for just detecting whether or not the event
% occured.
%
% Wed Jul  3 12:12:46 2019 mazer 

[ix, ts] = p2mFindEvents(varargin{:});
if length(ix)
  ix = ix(1);
  ts = ts(1);
end
