function PF = p2mCombine(wildcard)
%function PF = p2mCombine(wildcard)
%
%  load a bunch of p2m files into a single large pf struct.
%
%  INPUT
%    wildcard = wildcard list of p2m files to merge
%
%  OUTPUT
%    PF = monster data struct
%
%
% <<part of pype/p2m toolbox>>
%
%Fri Jun  2 10:33:00 2006 mazer -- new

% Check Input: Touryan 10.02.07 %
if strcmp(class(wildcard),'cell')
    files = wildcard;
else
    files = p2m_dir(wildcard);
end

for n = 1:length(files)
  fname = files{n};
  fprintf('%s: ', fname);
  pf = p2mLoad(fname);
  if n == 1
    PF = pf;
  else
    % Check for Field Mismatch: Touryan 02.28.08 %
    if length(fieldnames(PF.rec(1))) ~= length(fieldnames(pf.rec(1)))
        % Skip File %
        fprintf('Warning: p2m file from different system (Plexon, TDT), skipping merge...\n') 
    else
        % Merge File %
        k0 = length(PF.extradata);
        for k = 1:length(pf.extradata)
            PF.extradata{k0+k} = pf.extradata{k};
        end

        k0 = length(PF.rec);
        for k = 1:length(pf.rec)
            PF.rec(k0+k) = pf.rec(k);
        end
        
        PF.src = [PF.src '+' cannonicalfname(fname)];
    end
  end
end

fprintf('%d total trials\n', length(PF.rec));
