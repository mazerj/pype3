function [tnums] = p2mFindMarks(pf)

tnums = [];
for n = 1:length(pf.rec)
  [ix, ~] = p2mFindEvents(pf, n, 'TRIAL_TAG');
  if ~isempty(ix)
    tnums = [tnums n];
  end
end