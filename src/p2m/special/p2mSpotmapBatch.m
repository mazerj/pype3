function p2mSpotmapBatch(fname)


opts.start = 0;
opts.stop = 300;
opts.binsize = 20;
opts.tstep = 40;
opts.smooth = 1;
opts.color = 1;
opts.contour = 0;

try
  pf = p2mLoad(fname);
  p2mSpotmap(pf, opts, 1);
catch
  lasterr
  p2mExit(1);
end
p2mExit(0);
