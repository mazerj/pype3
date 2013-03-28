function ph = p2mFixDiode(pf, n, method)
%function ph = p2mFixDiode(pf, n, method)
%
% bandpass filter photodiode signal to get rid of frame-rate modulation
%
% INPUT
%       pf -- p2m structure loaded using p2mLoad
%        n -- record number
%   method -- optional specification of filter method:
%               'fft', 'cheby' or 'butter' (default is 'fft')
%             fft works best, but mangles phase and is probably slowest..
% OUTPUT
%        ph -- filter photodiode signal (should approximate square wave)
%
% Note that the lower bound on the filter is non-zero, so this will
% effectively demean the signal as well, so you be careful with fixed
% thresholds taken from the pype datafile. In theory, the new threshold
% should be close to zero...
%
%
% <<part of pype/p2m toolbox>>
%
%Fri Jan  4 15:17:49 2008 mazer 

if nargin == 2
  method='fft';
end

switch method
 case 'fft'
  low = 3;
  high = 0.95 .* pf.rec(n).params.mon_fps;
 otherwise
   low = 2;
   high = 0.60 .* pf.rec(n).params.mon_fps;
end


% pull the raw photodiode signal
y = pf.rec(n).raw_photo;

% pad signal on either side with reflected versions of the real
% signal (up to 2048 samples)
abuf = y;
bbuf = y;
k=2048;
if length(y) > k
  abuf = abuf(1:k);
  bbuf = bbuf((end-(k-1)):end);
end
y2 = [abuf(end:-1:1) y bbuf(end:-1:1)];

% remove a sample for odd-lengths -- otherwise it'll screw up the fft..
if rem(length(y2),2) == 1
  y2 = y2(1:end-1);
end

% now just filter
switch method
 case 'fft'
  % the fft filter is trivial, but inefficient -- basically use fft/ifft
  % to set all compoents outside the passband to 0 and then just take
  % the real portion of the result (who care about phase here??)
  nyq = 1000 * diff(pf.rec(n).eyet(1:2)) / 2;
  f = nyq .* [linspace(0, 1, length(y2)/2) linspace(1, 0, length(y2)/2)];
  
  Y = fft(y2);
  ix = (f > high) | (f< low);
  Y(ix) = 0.0;
  y2 = ifft(Y);
  y2 = real(y2);
 case 'cheby'
  fs = diff(pf.rec(n).eyet(1:2)) .* 1000.0;
  [b,a] = cheby1(3, .1, 2 * [low high] / fs);
  y2 = filter(b,a,y2);
 case 'butter'
  fs = diff(pf.rec(n).eyet(1:2)) .* 1000.0;
  [b,a] = butter(4, 2 * [low high] / fs);
  y2 = filter(b,a,y2);
 otherwise
  error(['p2mFixDiode -- unknown filter method:' method]);
end

% excise and keep the central (unpaded) portion of the filtered signalb
ph = y2((length(abuf)+1):(length(abuf)+length(y)));

% plot the results, if no output argument..
if nargout == 0
  x = 1:length(y);
  plot(x, y, 'b-', x, ph, 'r');
  title(method);
end
