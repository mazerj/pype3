function p2mFindFixes(p2mfile, icalfile, inplace, exitOnError)
%function p2mFindFixes(p2mfile, icalfile, inplace, exitOnError)
%
%  Batch engine for calibrating and extracting fixations
%  from .p2m and .ical files.  This addes a '.fixes' table
%  to the p2m file and also calibrated eye traces (if not
%  already calibrated) and rewrites back to the original
%  filename (if inplace is TRUE).
%
%  INPUT
%    p2mfile = name of p2m file
%    icalfile = name of matching ical file
%    inplace = boolean (0/1) specifying where to put p2m files.
%		If true, then matlab (.p2m) files will be
%		written into the same directory the original
%		datafiles came from.
%    exitOnError = boolean (0/1) if 1, then any error will
%               cause an immediate exit from the matlab kernel
%               using p2mExit.m to generate an error status flag.
%
%  OUPUT
%    none -- just writes the datafiles to disk.
%
%
% <<part of pype/p2m toolbox>>
%
%Mon Mar 17 14:16:50 2003 mazer 

%%% Wed Jun 16 14:59:38 2004 mazer -- why was this here:
%%% pf=p2mLoad(pf);

if ~exist('inplace', 'var')
  inplace = 0;
end

if ~exist('exitOnError', 'var')
  exitOnError = 0;
end

try
  pf = p2mLoad(p2mfile);
  if ~strcmp(icalfile, '-')
    ical = p2mLoad(icalfile);
  else
    ical = [];
  end
  newp2mfile = p2m_fname(p2mfile);
  if ~inplace
    ix = find(newp2mfile == '/');
    if length(ix) > 0
      newp2mfile = newp2mfile((ix(end)+1):end);
    end
  end
  if ~isempty(ical)
    pf = p2mEyecalApply(pf, ical);
  end
  pf.fixes = p2mFindSaccades(pf);
  p2mSave(pf, newp2mfile);
  fprintf('%s\n+ %s\n-> %s\n', p2mfile, icalfile, newp2mfile);
catch
  if exitOnError
    p2mExit(1);
  else
    error(lasterr);
  end
end
