function p2mEyecalBatch(wildcard, inplace, exitOnError)
%function p2mEyecalBatch(wildcard, inplace, exitOnError)
%
%  Batch engine for generating .ical files from .p2m files
%
%  INPUT
%    wildcard = CSH-style wildcard pattern of files to crunch
%    inplace = Boolean (0/1) specifying where to put p2m files.
%		If true, then matlab (.p2m) files will be
%		written into the same directory the original
%		datafiles came from.
%  OUPUT
%    none -- just writes the datafiles to disk.
%
%
% <<part of pype/p2m toolbox>>
%
%Fri Feb 28 18:29:16 2003 mazer 

if ~exist('inplace', 'var')
  inplace = 0;
end

if ~exist('exitOnError', 'var')
  exitOnError = 0;
end

files = p2m_dir(wildcard);
for n = 1:length(files)
  p2mfile = char(files(n));
  
  icalfile = strrep(p2mfile, '.p2m', '.ical');
  if ~inplace
    ix = find(icalfile == '/');
    if length(ix) > 0
      icalfile = icalfile((ix(end)+1):end);
    end
  end
  icalfile = strrep(icalfile, '.gz', '');
  epsfile = strrep(icalfile, '.ical', '.ical.ps');

  try
    fprintf('%s -> %s\n', p2mfile, icalfile);
    pf = p2mLoad(p2mfile);
    figure;
    ical = p2mEyecal(pf);
    save(icalfile, 'ical', '-mat');
    print('-depsc', epsfile);
    close;
  catch
    if exitOnError
      exit(1);
    else
      error(lasterr);
    end
  end
end


