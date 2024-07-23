import numpy as np

def lblrtm_tape11_reader1(fname, opt):
    v = []
    rad = []

    if len(opt) != 1:
        print('wrong number of input parameters, you must specify data type')
        return v, rad

    if opt.lower() == 'f' or opt.lower() == 's':
        shift = 266
        itype = 1
    else:
        shift = 356
        itype = 2

    with open(fname, 'rb') as fid:
        fid.seek(shift * 4, 0)
        test = np.fromfile(fid, dtype=np.int32, count=1)[0]

    if (itype == 1 and test == 24) or (itype == 2 and test == 32):
        endian = '<'  # little-endian
    else:
        endian = '>'  # big-endian

    with open(fname, 'rb') as fid:
        fid.seek(shift * 4, 0)
        endflg = False
        panel = 0

        if itype == 1:
            while not endflg:
                panel += 1
                fid.read(4)
                v1 = np.fromfile(fid, dtype=endian + 'f8', count=1)[0]
                if np.isnan(v1):
                    break
                v2 = np.fromfile(fid, dtype=endian + 'f8', count=1)[0]
                dv = np.fromfile(fid, dtype=endian + 'f4', count=1)[0]
                npts = np.fromfile(fid, dtype=endian + 'i4', count=1)[0]
                if npts != 2400:
                    endflg = True
                fid.read(4)
                LEN = np.fromfile(fid, dtype=endian + 'i4', count=1)[0]
                if LEN != 4 * npts:
                    print('internal file inconsistency')
                    endflg = True
                tmp = np.fromfile(fid, dtype=endian + 'f4', count=npts)
                LEN2 = np.fromfile(fid, dtype=endian + 'i4', count=1)[0]
                if LEN != LEN2:
                    print('internal file inconsistency')
                    endflg = True
                v.extend(np.arange(v1, v2 + dv, dv))
                rad.extend(tmp)
        else:
            while not endflg:
                panel += 1
                fid.read(4)
                tmp = np.fromfile(fid, dtype=endian + 'f8', count=3)
                v1, v2, dv = tmp
                if np.isnan(v1):
                    break
                npts = np.fromfile(fid, dtype=endian + 'i8', count=1)[0]
                if npts != 2400:
                    endflg = True
                fid.read(4)
                LEN = np.fromfile(fid, dtype=endian + 'i4', count=1)[0]
                if LEN != 8 * npts:
                    print('internal file inconsistency')
                    endflg = True
                tmp = np.fromfile(fid, dtype=endian + 'f8', count=npts)
                LEN2 = np.fromfile(fid, dtype=endian + 'i4', count=1)[0]
                if LEN != LEN2:
                    print('internal file inconsistency')
                    endflg = True
                v.extend(np.arange(v1, v2 + dv, dv))
                rad.extend(tmp)
    v=np.array(v)
    rad=np.array(rad)
    # unique_indices=np.where(np.abs(np.diff(v))>1e-2)[0]+1
    # unique_indices=np.insert(unique_indices,0,0)
    # v=v[unique_indices]
    return v,rad
