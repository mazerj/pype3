function [L, S] = plx2mat(fname, dolfp, dospk, dosave)
%function plx2mat(fname)
%
% Use plx2asc.py to convert and load the spike and LFP data from a .plx
% file into a compact, generic data stucture and optionally save it
% as a .mat file
%
% Note that the data structure returned is intended to abstract out
% the spike time, spike waveform (aka snippet) and slow lfp signals
% in a way compatible with both the plexon, TDT and anything else
% you might want to use... so eventually there sould be a tdt2mat etc..
%
% INPUT
%   fname -- name of .plx datafile
%   dolfp -- load lfp data? (default 1)
%   dospk -- load lfp data? (default 1)
%   dosave -- save to disk? (default 1)
%
% OUTPUT
%   L -- lfp data
%   S -- spike data
%   side effect -- L and S are saved to <fname>.plx.lfp and <fname>.plx.spk
%
%   'L' in ...plx.lfp file:
%
%     L.haslfp = vector indicating which channels have lfp data
%     L.lfp_chans{1..ntrials} -- spike channel/electrode number (1-based)
%     L.lfp_times{1..ntrials} -- spike time (ms)
%     L.lfp_volts{1..ntrials} -- unit number (0=unsorted)
%
%   'spk' in ...plx.spk file:
%
%     S.nunits -- vector of number of sorted units on each dsp channel
%     S.spk_chans{1..ntrials} -- spike channel/electrode number (1-based)
%     S.spk_units{1..ntrials} -- unit number (0=unsorted)
%     S.spk_times{1..ntrials} -- spike time (ms)
%
%     S.spw -- raw spike waveform data
%       S.spw.trial -- trial number
%       S.spw.channel -- electrode number (1-based)
%       S.spw.unit -- unit number (0-based)
%       S.spw.index -- time index relative to snippet start
%       S.spw.time -- time in ms synced to pype
%       S.spw.voltage -- voltages in mv
%
% SEE ALSO
%   plx2asc(.py), xdacq_spk, xdacq_lfp, xdacq_spw
%
%Tue Jan  8 09:53:18 2008 mazer

if ~exist('dolfp', 'var'), dolfp = 1; end;
if ~exist('dospk', 'var'), dospk = 1; end;
if ~exist('dosave', 'var'), dosave = 1; end;

prefix = tempname();

cmd = sprintf('plx2asc -p %s %s', prefix, fname);
[status, result] = unix(cmd);
if status > 0
  error(result);
end
disp(result);

hdr = load([prefix '.hdr'], '-ascii');
delete([prefix '.hdr']);

L = struct();
S = struct();

if dolfp
  %% save .lfp file %%

  lfp = load([prefix '.lfp'], '-ascii');
  delete([prefix '.lfp']);

  if isempty(lfp)
    nl = 0;
  else
    nl = max(lfp(:,1));
  end

  L.haslfp = hdr(:,3);
  L.lfp_chans = {};
  L.lfp_times = {};
  L.lfp_volts = {};

  for n=1:nl
    if ~isempty(lfp)
      ix = find(lfp(:,1) == n);
      L.lfp_chans{n} = lfp(ix, 2);
      L.lfp_times{n} = lfp(ix, 3);
      L.lfp_volts{n} = lfp(ix, 4);
    else
      L.lfp_chans{n} = [];
      L.lfp_times{n} = [];
      L.lfp_volts{n} = [];
    end
  end

  if dosave
    savefile = [fname '.lfp'];
    save(savefile, 'L', '-mat');
    fprintf('Saved lfp to %s\n', savefile);
  end
end

if dospk
  %% save spike data to .spk file %%

  spk = load([prefix '.spk'], '-ascii');
  delete([prefix '.spk']);

  swaves = load([prefix '.spw'], '-ascii');
  delete([prefix '.spw']);

  if isempty(spk)
    ns = 0;
  else
    ns = max(spk(:,1));
  end


  S.nunits = hdr(:,2);
  S.nsortedunits = zeros(size(hdr(:,2)));
  if ~isempty(spk)
    for i = 1:length(S.nunits)
      %
      % fix nunits by actually scanning the data for any detected
      % spikes on the specified channel.. not sure why this is necessary,
      % but apparently sometimes nunits can be non-zero even when there
      % are no spikes on the channel
      %
      % this will set nunits to 1 if there are any sorted or unsorted
      % spike events on the indicated channel -- then we can just ignore
      % the plexon nunits field and use this. Note that unsorted units
      % count as units here! If you want only sorted units, look at
      % S.nsortedunits instead..
      %
      units = unique(spk(spk(:,2) == i, 3));
      S.nunits(i) = length(units);
      S.nsortedunits(i) = sum(units > 0);
    end
  end

  S.spk_chans = {};
  S.spk_units = {};
  S.spk_times = {};

  for n=1:ns
    if ~isempty(spk)
      ix = find(spk(:,1) == n);
      S.spk_chans{n} = spk(ix, 2);
      S.spk_units{n} = spk(ix, 3);
      S.spk_times{n} = spk(ix, 4);
    else
      S.spk_chans{n} = [];
      S.spk_units{n} = [];
      S.spk_times{n} = [];
    end
  end

  if ~isempty(swaves)
    S.spw.trial = swaves(:,1);
    S.spw.channel = swaves(:,2);
    S.spw.unit = swaves(:,3);
    S.spw.index = swaves(:,4);
    S.spw.time = swaves(:,5);
    S.spw.volt = swaves(:,6);
  else
    S.spw.trial = [];
    S.spw.channel = [];
    S.spw.unit = [];
    S.spw.index = [];
    S.spw.time = [];
    S.spw.volt = [];
  end

  if dosave
    savefile = [fname '.spk'];
    save(savefile, 'S', '-mat');
    fprintf('Saved spikes to %s\n', savefile);
  end
end
