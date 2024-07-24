import numpy as np
import math
import subprocess
import shutil

lev = 55
prof = 50
lev1 = 55

p = np.zeros((lev, prof), dtype=np.float32)
t = np.zeros((lev, prof), dtype=np.float32)
ozo = np.zeros((lev, prof), dtype=np.float32)
wv = np.zeros((lev, prof), dtype=np.float32)

p1 = np.zeros((lev1, prof), dtype=np.float32)
t1 = np.zeros((lev1, prof), dtype=np.float32)
ozo1 = np.zeros((lev1, prof), dtype=np.float32)
wv1 = np.zeros((lev1, prof), dtype=np.float32)

tem = np.zeros((prof, lev), dtype=np.float32)
H2O = np.zeros((prof, lev), dtype=np.float32)
o3 = np.zeros((prof, lev), dtype=np.float32)

tra2 = np.zeros((lev1, 4), dtype=np.float32)
trah2 = np.zeros((lev1, 4), dtype=np.float32)
tra = np.zeros((lev, 4), dtype=np.float32)
trah = np.zeros((lev, 4), dtype=np.float32)

angle = 0.0
va = np.zeros(6, dtype=np.float32)
height = np.zeros(lev, dtype=np.float32)
pp = np.zeros(lev, dtype=np.float32)
tsurf = np.zeros(prof, dtype=np.float32)
scant = np.array([2.58, 2.94, 3.72, 4.83, 6.1, 7.2, 9], dtype=np.float32)
blank = np.zeros(lev, dtype=np.float32)
bwn = 0.0
ewn = 0.0
maxwn = 1000.0
bwn0 = 6500.0
ewn0 = 8500.0
lay = ['001', '002', '003', '004', '005', '006', '007', '008', '009', '010',
       '011', '012', '013', '014', '015', '016', '017', '018', '019', '020',
       '021', '022', '023', '024', '025', '026', '027', '028', '029', '030',
       '031', '032', '033', '034', '035', '036', '037', '038', '039', '040',
       '041', '042', '043', '044', '045', '046', '047', '048', '049', '050',
       '051', '052', '053', '054']

# Read pressure data
with open('./profile/pressure.txt', 'r') as file:
    for i in range(lev):
        p1[i, :] = np.array(file.readline().split(), dtype=np.float32)
for i in range(lev):
    p[i, :] = p1[lev - i - 1, :]

p[p < 0.001] = 0.001

# Read temperature data
with open('./profile/temperature.txt', 'r') as file:
    for i in range(lev):
        t1[i, :] = np.array(file.readline().split(), dtype=np.float32)
for i in range(lev):
    t[i, :] = t1[lev - i - 1, :]

# Read ozone data
# with open('./profile/ozo_test_1573.txt', 'r') as file:
#     for i in range(lev):
#         ozo1[i, :] = np.array(file.readline().split(), dtype=np.float32)
# for i in range(lev):
#     ozo[i, :] = ozo1[lev - i - 1, :]

# Read water vapor data
with open('./profile/wv.txt', 'r') as file:
    for i in range(lev):
        wv1[i, :] = np.array(file.readline().split(), dtype=np.float32)
for i in range(lev):
    wv[i, :] = wv1[lev - i - 1, :]

for i in range(6):
    angle = 1 + 0.25 * i
    va[i] = math.degrees(math.acos(1 / angle))

height.fill(0.0)
blank.fill(0.0)

for iprof in range(prof):
    tsurf[iprof] = t[0, iprof]

for iadd in range(1):
    bwn = bwn0 + iadd * maxwn
    ewn = ewn0 + iadd * maxwn

    for jj in range(1):
        c1 = str(jj + 1)
        for iprof in range(prof):
            c2 = f'{iprof + 1:04d}'
            with open('TAPE5', 'w') as file:
                CXID = '83P 55level profile to creat transmittance database'
                file.write(f"${CXID}\n")
                file.write(f" HI=1 F4=1 CN=1 AE=0 EM=0 SC=0 FI=0 PL=0 TS=1 AM=0 MG=0 LA=0 OD=1 XS=0   00   00\n")
                file.write(f"{bwn:10.3f}{ewn:10.3f}                                                  REJ=0     1.000E-01\n")
                file.write(f"{0:7}{2:5}{-55:5}{1:5}{1:5}{7:5}{1:5}{0:5}{0:10.3f}{0:10.3f}\n")
                file.write(f"{p[lev-1, iprof]:10.3f}{p[0, iprof]:10.3f}{180.000:10.3f}\n")
                column_data = p[:, iprof]
                # 以8个一组分批写入数据
                file.writelines([f"{' '.join([f'{x:10.3f}' for x in column_data[i:i+8]])}\n" for i in range(0, len(column_data), 8)])
                file.write(f"{-55:5}{'INPUT FOR CAMEX':9}\n")
                for i in range(lev):
                    file.write(f"{height[i]:10.3f}{p[i, iprof]:10.3f}{t[i, iprof]:10.3f}  {'AA'} {'L'} {'AAAAAAA'}\n")
                    file.write(f"{wv[i, iprof]:15.8e}{blank[i]:15.8e}{blank[i]:15.8e}{blank[i]:15.8e}{blank[i]:15.8e}{blank[i]:15.8e}{blank[i]:15.8e}\n")
                file.write(f"-1.\n")
                file.write(f"$ Transfer to ASCII plotting data\n")
                file.write(f" HI=0 F4=0 CN=0 AE=0 EM=0 SC=0 FI=0 PL=1 TS=0 AM=0 MG=0 LA=0 OD=0 XS=0 0 0 0\n")
                file.write(f"# Plot title not used\n")
                file.write(f"{bwn:10.4f}{ewn:10.4f}{10.2000:10.4f}{100.000:10.4f}{5:5}{0:5}{12:5}{0:5}{1.000:10.3f}{0:5}{0:5}{0:5}\n")
                file.write(f"{0.0000:10.4f}{1.2000:10.4f}{7.0200:10.3f}{0.2000:10.3f}{4:5}{0:5}{1:5}{1:5}{0:5}{0:5}{0:5}{3:5}{27:5}\n")
                file.write(f"{bwn:10.4f}{ewn:10.4f}{10.2000:10.4f}{100.000:10.4f}{5:5}{0:5}{12:5}{0:5}{1.000:10.3f}{0:5}{0:5}{0:5}\n")
                file.write(f"{0.0000:10.4f}{1.2000:10.4f}{7.0200:10.3f}{0.2000:10.3f}{4:5}{0:5}{1:5}{1:5}{0:5}{0:5}{0:5}{3:5}{28:5}\n")
                file.write(f"-1.\n")
                file.write(f"%%%%%\n")
            # TAPE5制作好后，运行pl脚本，pl脚本中写着运行模型和输出提示的命令
            subprocess.run(['./script_run_example.pl'], check=True)
            bwn_str = f"{bwn:9.3f}".strip()
            source = 'ODint_001'
            destination = f'./OD001save_H2O/ODint_001-{bwn_str}'
            shutil.move(source, destination)