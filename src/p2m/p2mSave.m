function p2mSave(s, matfile)
%function p2mSave(s, matfile)
%
%  Save p2m structure to a file in a way p2mLoad can read.
%  Works for ical structs too..
%
%
% <<part of pype/p2m toolbox>>
%
%Sat Mar  1 12:21:16 2003 mazer 

if isfield(s, 'rec')
  % must be a p2m file..
  PF = s;
  save(matfile, 'PF', '-mat');
  fprintf('Saved p2m to ''%s''\n', matfile);
elseif isfield(s, 'MX')
  % must be a ical file..
  ical = s;
  save(matfile, 'ical', '-mat');
  fprintf('Saved ical to ''%s''\n', matfile);
else
  error(['unknown structure type: ' fname]);
end
  
