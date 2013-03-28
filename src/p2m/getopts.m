function defaults = getopts(defaults, varargin)
%function defaults = getopts(defaults, varargin)
%
%  Build a structure from optional/variable argument list.  Input
%  is a structure of default values.  Fields are added or modified
%  in the default structure according to the vararin values:
%    s.foo = 1;
%    s.baz = 2;
%    s = getopts(defaults, 'foo', 10, 'baz', -1)
%    s = 
%        foo: 10
%        baz: -1
%
%  And so on.  This is most useful in the following way:
%    function f(x, y, z, varargin}
%    opts.a = 1;
%    opts.b = 2;
%    opts = getops(opts, varargin{:});
%    ....
%
%  You can also use '+foo'/'-foo' to set foo to 1/0, respectively
%  in a single argument for ease-of-use
%
%
% <<part of pype/p2m toolbox>>
%
%
%Tue Mar  4 15:19:19 2003 mazer 
%
%Tue Jan 12 10:15:15 2010 mazer 
%  added +var/-var syntax for boolean 1/0
%
%Wed Mar  6 12:12:52 2013 mazer 
%  added support for a single option list to be passed in as
%  a struct (ie, an old option list)
%

if length(varargin) > 0 && strcmp(varargin{1}, '?help')
  f = fieldnames(defaults);
  for n = 1:length(f)
    disp({f{n} getfield(defaults, f{n})});
  end
  error('getopt: stopped after help');
elseif length(varargin) == 1 && isstruct(varargin{1})
  opts = varargin{1};
  fn = fields(opts);
  for n = 1:length(fn)
    defaults = setfield(defaults, fn{n}, getfield(opts, fn{n}));
  end
else
  n = 1;
  while n <= length(varargin)
    if varargin{n}(1) == '+'
      defaults = setfield(defaults, varargin{n}(2:end), 1);
      n = n + 1;
    elseif varargin{n}(1) == '-'
      defaults = setfield(defaults, varargin{n}(2:end), 0);
      n = n + 1;
    else
      defaults = setfield(defaults, varargin{n}, varargin{n+1});
      n = n + 2;
    end
  end
end
  
