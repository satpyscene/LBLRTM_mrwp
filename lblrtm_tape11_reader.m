function [v, rad] = lblrtm_tape11_reader(fname, opt)

% File format illustration
% for single precision
% shift 266*4 bytes
% LOOP
% 1 int        , 24 (block of v1, v2, dv, npts)
% 2 double vars, for v1, and v2
% 1 float      , for dv
% 1 int        , for npts
% 1 int        , 24
% 1 int        , 9600 or npts*4 (beg of block output)
% NPTs float   , rad
% 1 int        , 9600 or npts*4 (end of block of output)
% LOOP ENDS

% for double precision
% shift 356*4 bytes
% LOOP
% 1 int        , 32 (v1, v2, dv and npts, extra 0)
% 3 double vars, for v1, v2, and dv
% 1 long int   , for npts
% 1 int        , 32   
% 1 int        , 19200 or npts*8 (beg of block of output)
% NPTS double  , rad
% 1 int        , 19200 or npts*8 (end of block of output)
% LOOP ENDS

% Author: Xianglei Huang
% Tested on Redhat Linux with pgi-compiler version of LBLRTM

v = [];
rad = [];

if nargin ~= 2
	disp('wrong number of input parameters, you must specify data type');
	return;
end

fid = fopen(fname, 'rb', 'l');

if lower(opt(1)) == 'f' | lower(opt(1)) == 's'
	shift = 266;
	itype   = 1;
else
	shift = 356;
	itype = 2;
end

fseek(fid, shift*4, -1);

% decide whether need to open as big-endian file
test = fread(fid, 1, 'int');

fclose(fid);

if (itype == 1 & test == 24) | (itype ==2 & test == 32)
fid = fopen(fname, 'rb', 'l');
fseek(fid, shift*4, -1);
else
fid = fopen(fname, 'rb', 'b');
fseek(fid, shift*4, -1);
end

endflg = 0;

panel = 0;

if itype == 1
while (endflg == 0)
	panel = panel + 1;
%	disp(['read panel ', int2str(panel)]);
	fread(fid, 1, 'int');
	v1 = fread(fid, 1, 'double');
	if isnan(v1) 
		break;
	end
	v2 = fread(fid, 1, 'double');
	dv = fread(fid, 1, 'float');
	npts = fread(fid, 1, 'int');
    %fprintf('%d\n',npts);
    if npts~=2400 
		endflg = 1;
	end
  	fread(fid, 1, 'int');
	LEN = fread(fid, 1, 'int');
 	if (LEN ~= 4*npts)
		disp('internal file inconsistency');
		endflg = 1;
    end
    tmp = fread(fid, npts, 'float');
	LEN2 = fread(fid, 1, 'int');
	if (LEN ~= LEN2)
		disp('internal file inconsistency');
                endflg = 1;
    end
    %v = [v; [v1, v2, dv]];
	v=[v;transpose(v1:dv:v2)];
	rad = [rad; reshape(tmp, npts, 1)];
end
else
while(endflg == 0)
        panel = panel + 1;
   %     disp(['read panel ', int2str(panel)]);
	fread(fid, 1, 'int');
	tmp = fread(fid, 3, 'double');
	v1 = tmp(1); v2 = tmp(2); dv = tmp(3);
	if isnan(v1) 
		break;
	end
	npts = fread(fid, 1, 'int64');

	if npts ~= 2400
		endflg = 1;
	end

	fread(fid, 1, 'int');
	LEN = fread(fid, 1, 'int');
	%LEN
	%npts
	if (LEN ~= 8*npts)
		disp('internal file inconsistency');
		endflg = 1;
	end
	tmp = fread(fid, npts, 'double');
	LEN2 = fread(fid, 1, 'int');
	if (LEN ~= LEN2)
		 disp('internal file inconsistency');
                endflg = 1;
        end

	%v = [v; [v1, v2, dv]];
    v=[v;transpose(v1:dv:v2)];
	rad = [rad; reshape(tmp, npts, 1)];
end
end

%v = v1:dv:v2;
%v = reshape(v, length(v), 1);
%rad = tmp;
%rad = reshape(rad, length(v), 1);

fclose(fid);