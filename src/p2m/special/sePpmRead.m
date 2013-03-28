function [r,g,b] = sePpmRead(fname)

[fid, msg] = fopen(fname, 'r');
if (fid == -1)
  error([fname '\n' msg]);
end

%%% First line contains ID string:
%%% "P1" = ascii bitmap, "P2" = ascii greymap,
%%% "P3" = ascii pixmap, "P4" = raw bitmap, 
%%% "P5" = raw greymap, "P6" = raw pixmap

TheLine = fgetl(fid);
format  = TheLine;		

if ~strcmp(format, 'P3') & ~strcmp(format, 'P6')
  error('PPM file must be of type P3 or P6');
end

%%% Any number of comment lines
TheLine  = fgetl(fid);
while TheLine(1) == '#' 
	TheLine = fgetl(fid);
end

%%% dimensions
sz = sscanf(TheLine,'%d',2);
xdim = sz(1);
ydim = sz(2);
sz = 3 * xdim * ydim;

%%% Maximum pixel value
TheLine  = fgetl(fid);
maxval = sscanf(TheLine, '%d',1);

%%im  = zeros(dim,1);
if (format(2) == '2')
  [im,count]  = fscanf(fid,'%d',sz);
else
  [im,count]  = fread(fid,sz,'uchar');
end

fclose(fid);

if (count == sz)
  n = xdim * ydim;
  r = reshape(im(1:3:end), xdim, ydim)';
  g = reshape(im(2:3:end), xdim, ydim)';
  b = reshape(im(3:3:end), xdim, ydim)';
else
  error('Warning: File ended early!');
end
	  
