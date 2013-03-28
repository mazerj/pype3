load foo.asc;

co = find(foo(:,1) == 0);
lj = find(foo(:,1) == 1);

ct = foo(co,2);
cy = foo(co,3);

lt0 = 1000*foo(lj,2);
ly0 = foo(lj,3);

lt = round(lt0(1)):1:round(lt0(end));
ly = interp1(lt0, ly0, lt);

ix = find(lt>=ct(1) & lt<=ct(end));
lt = lt(ix);
ly = ly(ix);

cy = (cy - mean(cy)) ./ std(cy);
ly = (ly - mean(ly)) ./ std(ly);

lt = lt-ct(1);
ct = ct-ct(1);

clf;
subplot(2,1,1);
plot(ct, cy, 'k-', lt, ly, 'r-');

subplot(2,1,2);
[c,lags] = xcorr(cy,ly);
plot(lags,c);
xrange(-50,50);
xlabel('neg->comedi leads');

%waveview;



     