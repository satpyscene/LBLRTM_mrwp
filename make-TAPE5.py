import numpy as np
import math
import subprocess
import shutil
# 1.下面是大气分层数（廓线文件行数）和廓线数（廓线文件列数）
lev = 55
prof = 50
lev1 = 55
# 2.下面三行：maxwn为波数区间（一次模拟中期望的范围，LBLRTM要求其最大不能超过2000，因此如果想模拟更大的范围就需要用循环逐个波段模拟后拼接），bwn0为开始波数，ewn0为结束波数。
maxwn = 1000.0
bwn0 = 6500.0
ewn0 = 8500.0
# 3.分辨率
resolution = '1.000E-01'
# 4.修改影响输出的气体种类在后面循环中的这一行修改：file.write(f"{wv[i, iprof]:15.8E}{blank[i]:15.8E}{blank[i]:15.8E}

# 5.修改大气廓线文件大约在五六十行的位置，修改路径，并且注意对应廓线文件分层及廓线数量与最开始设置

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

va = np.zeros(6, dtype=np.float32)
height = np.zeros(lev, dtype=np.float32)
pp = np.zeros(lev, dtype=np.float32)
tsurf = np.zeros(prof, dtype=np.float32)
scant = np.array([2.58, 2.94, 3.72, 4.83, 6.1, 7.2, 9], dtype=np.float32)
blank = np.zeros(lev, dtype=np.float32)


lay = ['001', '002', '003', '004', '005', '006', '007', '008', '009', '010',
       '011', '012', '013', '014', '015', '016', '017', '018', '019', '020',
       '021', '022', '023', '024', '025', '026', '027', '028', '029', '030',
       '031', '032', '033', '034', '035', '036', '037', '038', '039', '040',
       '041', '042', '043', '044', '045', '046', '047', '048', '049', '050',
       '051', '052', '053', '054']

# Read pressure data
with open('./profile/pressure.txt', 'r') as file:
    for i in range(lev):
        # 将廓线文件的一整行都读给pl（行数即为层数，列数代表廓线数）
        p1[i, :] = np.array(file.readline().split(), dtype=np.float32)
# 下边是将气压倒序排列
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
                # 下面一行是LBLRTM设置参数，具体作用查阅html说明文档
                file.write(f" HI=1 F4=1 CN=1 AE=0 EM=0 SC=0 FI=0 PL=0 TS=0 AM=1 MG=0 LA=0 OD=1 XS=0   00   00\n")
                # 下面最后一个位置设置分辨率
                file.write(f"{bwn:10.3f}{ewn:10.3f}                                                            REJ=0     {resolution}\n")
                file.write(f"{0:5}{2:5}{-55:5}{1:5}{1:5}{7:5}{1:5}{0:5}{0:10.3f}{0:10.3f}\n")
                file.write(f"{p[lev-1, iprof]:10.3f}{p[0, iprof]:10.3f}{180.000:10.3f}\n")
                column_data = p[:, iprof]
                # 以8个一组分批写入气压数据
                file.writelines([''.join([f"{x:10.3f}".rstrip() for x in column_data[i:i+8]]) + '\n' for i in range(0, len(column_data), 8)])
                # file.writelines([f"{'   '.join([f'{x:10.3f}' for x in column_data[i:i+8]])}\n" for i in range(0, len(column_data), 8)])
                file.write(f"{-55:5}         {'INPUT FOR CAMEX'}\n")
                for i in range(lev):
                    file.write(f"{height[i]:10.3f}{p[i, iprof]:10.3f}{t[i, iprof]:10.3f}     {'AA'} {'L'} {'AAAAAAA'}\n")
                    file.write(f"{wv[i, iprof]:15.8E}{blank[i]:15.8E}{blank[i]:15.8E}{blank[i]:15.8E}{blank[i]:15.8E}{blank[i]:15.8E}{blank[i]:15.8E}\n")
                # 用哪个开哪个WRITE(44,"(8E15.8)") wv(i,iprof),tra(i,1),ozo(i,iprof),blank(i),blank(i),blank(i),blank(i)!,blank(i),blank(i),blank(i),blank(i),blank(i),tra(i,10),blank(i),blank(i),tra(i,11)!这里开几个气体跟上面的A保持一致，不用的气体就blank
                
                file.write(f"-1.0\n")
                file.write(f"$ Transfer to ASCII plotting data\n")
                file.write(f" HI=0 F4=0 CN=0 AE=0 EM=0 SC=0 FI=0 PL=1 TS=0 AM=0 MG=0 LA=0 OD=0 XS=0   0   0\n")
                file.write(f"# Plot title not used\n")
                file.write(f"{bwn:10.4f}{ewn:10.4f}{10.2000:10.4f}{100.000:10.4f}{5:5}{0:5}{12:5}{0:5}{1.000:10.3f}{0:2}{0:3}{0:5}\n")
                file.write(f"{0.0000:10.4f}{1.2000:10.4f}{7.0200:10.3f}{0.2000:10.3f}{4:5}{0:5}{1:5}{1:5}{0:5}{0:5}{0:2}{3:5}{27:3}\n")
                file.write(f"{bwn:10.4f}{ewn:10.4f}{10.2000:10.4f}{100.000:10.4f}{5:5}{0:5}{12:5}{0:5}{1.000:10.3f}{0:2}{0:3}{0:5}\n")
                file.write(f"{0.0000:10.4f}{1.2000:10.4f}{7.0200:10.3f}{0.2000:10.3f}{4:5}{0:5}{1:5}{1:5}{0:5}{0:5}{0:2}{3:5}{28:3}\n")
                file.write(f"-1.0\n")
                file.write(f"%%%%%\n")
            # # TAPE5制作好后，运行pl脚本，pl脚本中写着运行模型和输出提示的命令
            # subprocess.run(['./script_run_example.pl'], check=True)
            # bwn_str = f"{bwn:9.3f}".strip()
            # source = 'ODint_001'
            # destination = f'./OD001save_H2O/ODint_001-{bwn_str}'
            # shutil.move(source, destination)