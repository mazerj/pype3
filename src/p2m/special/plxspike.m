function [Spikes, Trial, Time] = plxspike(S, channel, unit)

% PLXSPIKE extracts spike waveform for given channel-unit
%          from Plexon/TDT spike waveform structure
%
%       [Spikes, Trial, Time] = plxspike(S, channel, unit)
%
%  INPUT
%    S       - plexon/tdt spike data (see plx2mat.m)
%    channel - electrode number (1-based)
%    unit    - unit number (0-based, 0 = unsorted)
%  - OR -
%    channel - string with plexon-style specification (e.g. '005a')
%
%  OUTPUT
%    Spikes - spike waveform         [N points]
%    Trial  - trial number           [N 1]
%    Time   - time of spike waveform [N 1]
%
%  SEE ALSO
%    plx2mat.m, p2mSelect.m
%
% Touryan 03.31.2008

% PARAMETERS %
OFFSET = 100;           % Channel Index Offset

% Plexon Format: "005a" %
if nargin == 2
    temp    = channel;
    channel = str2num(temp(1:end-1));
    unit    = temp(end)-('a') + 1;
end
if channel <= 0
    error('Channel Number Must be > 0!')
end

% Find Wavefore End Index (Separated by NaNs) %
spkend = find(isnan(S.spw.volt));
spklng = mean(diff(spkend));                    % Length of Spike Waveform
spknum = length(S.spw.volt) / spklng;           % Number of Total Spikes

% Reshape Spike Matrix %
Spikes = reshape(S.spw.volt,spklng,spknum);     % [Length Number]
Spikes = Spikes(1:end-1,:);

% Reshape Channel-Unit, Trial and Time Matrix %
CUind = S.spw.channel * OFFSET + S.spw.unit;
CUind = reshape(CUind,spklng,spknum); 
CUind = CUind(1,:);
Trial = reshape(S.spw.trial,spklng,spknum); 
Trial = Trial(1,:);
Time  = reshape(S.spw.time,spklng,spknum); 
Time  = Time(1,:);

% Find Index of Requested Channel-Unit %
Index = find(CUind == (channel*OFFSET+unit));

% Return Result %
if isempty(Index)
    Spikes = [];
    Trial  = [];
    Time   = [];
    fprintf('Warning: No Spikes Found on Channel:%d  Unit:%d \n',channel,unit); 
else
    % Remove All Other Channel-Units %
    Spikes = Spikes(:,Index)';
    Trial  = Trial(Index)';
    Time   = Time(Index)';
end


