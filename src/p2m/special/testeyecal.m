function testeyecal(pf)

if 1
  nrec = length(pf.rec);

  % use 50% of the data in the first pass
  p1 = (rand([nrec 1]) < 0.50);

  % rest in second pass
  p2 = ~p1;

  pf1 = pf;
  pf1.rec = pf.rec(p1);
  
  pf2 = pf;
  pf2.rec = pf.rec(p2);

  figure(1)
  ical = p2mEyecal(pf1, 0);
  suptitle('calibration data set');
  
  figure(2);
  pf2 = p2mEyecalApply(pf2, ical);
  p2mEyecal(pf2, 0);
  suptitle('validation set');
end

if 0
  % iteration is BAD... don't do this..
  iter = 1;
  while 1
    figure;
    ical = p2mEyecal(pf, 0);
    suptitle(sprintf('iter=%d', iter));
    drawnow;
    pf = p2mEyecalApply(pf, ical);
    iter = iter + 1;
  end
end


