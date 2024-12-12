# -*- coding: utf-8 -*-
# 该程序由fortran程序翻译调整而来，在循环中需要的位置启用pl脚本（里边主要是./lblrtm命令 即运行模型）
import numpy as np
import math
import subprocess
import shutil
import os
# 1.下面是大气分层数（廓线文件列数）和廓线数（廓线文件行数）
lev = 101
prof = 15704#15704
lev1 = 101 # 暂与lev保持一致就好，分开设置其值可能有其他用处，暂时用不到
# 2.下面三行：maxwn为波数区间（一次模拟中期望的范围，LBLRTM要求其最大不能超过2000，因此如果想模拟更大的范围就需要用循环逐个波段模拟后拼接），bwn0为开始波数，ewn0为结束波数。
gase_type = "CO2"
#用不到了，分段模拟直接在起始分辨率循环中加就好了 maxwn = 1000.0 # 期望分段运行模型时有用，单跑一段时，前边乘数是0不起作用
#bwn0 = 1700.0
#ewn0 = 3260.0
## 3.分辨率
#resolution = '5.000E-03'
bwn0_ewn0_resolution_list = [
    (600.0, 1200.0, '3.000E-02'),
    # (1300.0, 1700.0, '1.000E-03'),
    # (1700.0, 3260.0, '5.000E-03'),
    # 可以根据需要继续添加更多项
]
for bwn0, ewn0, resolution in bwn0_ewn0_resolution_list:
    # 4.修改影响输出的气体种类在后面循环中的这一行修改：file.write(f"{wv[i, iprof]:15.8E}{blank[i]:15.8E}{blank[i]:15.8E}

    # 5.修改大气廓线文件大约在五六十行的位置，修改路径，并且注意对应廓线文件分层及廓线数量与最开始设置
    p = np.zeros((lev, prof), dtype=np.float32)
    t = np.zeros((lev, prof), dtype=np.float32)
    ozo = np.zeros((lev, prof), dtype=np.float32)
    wv = np.zeros((lev, prof), dtype=np.float32)
    co2 = np.zeros((lev, prof), dtype=np.float32)

    p1 = np.zeros((lev, prof), dtype=np.float32)
    t1 = np.zeros((lev, prof), dtype=np.float32)
    ozo1 = np.zeros((lev, prof), dtype=np.float32)
    wv1 = np.zeros((lev, prof), dtype=np.float32)
    co21 = np.zeros((lev, prof), dtype=np.float32)

    tem = np.zeros((prof, lev), dtype=np.float32)
    H2O = np.zeros((prof, lev), dtype=np.float32)
    o3 = np.zeros((prof, lev), dtype=np.float32)


    tra2 = np.zeros((lev1, 4), dtype=np.float32)
    trah2 = np.zeros((lev1, 4), dtype=np.float32)
    tra = np.zeros((lev, 4), dtype=np.float32)
    tra1 = np.zeros((lev, 4), dtype=np.float32)

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
    with open('/share/home/liuc/yanjunyu/LBLRTM/share_profile/seebor4profile/pressure_levels_hPa-_SeeBorV4.0_15704.txt', 'r') as file:
        for i in range(lev):
            line = file.readline().strip()
                    # 添加检查文件末尾的逻辑，防止死循环
            while (line.startswith('#') or not line) and line:
                line = file.readline().strip()

            # 如果读取到文件末尾，提前退出循环
            if not line:
                print("Reached end of file or no valid data found for level", i)
                break


            # 将廓线文件的一整行都读给pl（）
            p1[i, :] = np.array(line.split(), dtype=np.float32)
    # 下边是将气压倒序排列
    for i in range(lev):
        p[i, :] = p1[lev - i - 1, :]

    p[p < 0.001] = 0.001
    # Read temperature data
    with open('/share/home/liuc/yanjunyu/LBLRTM/share_profile/seebor4profile/temperature-K-_profile_SeeBorV4.0_15704.txt', 'r') as file:
        for i in range(lev):
            t1[i, :] = np.array(file.readline().split(), dtype=np.float32)
    for i in range(lev):
        t[i, :] = t1[lev - i - 1, :]

#     # Read ozone data
#     with open('/share/home/liuc/yanjunyu/LBLRTM/LBLRTM-master/profile/seebor4profile/ozone-ppmv-_profile_SeeBorV4.0_15704.txt', 'r') as file:
#         for i in range(lev):
#             ozo1[i, :] = np.array(file.readline().split(), dtype=np.float32)
#     for i in range(lev):
#         ozo[i, :] = ozo1[lev - i - 1, :]

#     # Read water vapor data
#     with open('/share/home/liuc/yanjunyu/LBLRTM/LBLRTM-master/profile/seebor4profile/water_vapour-kgkg-_profile_SeeBorV4.0_15704.txt', 'r') as file:
#         for i in range(lev):
#             wv1[i, :] = np.array(file.readline().split(), dtype=np.float32)
#     for i in range(lev):
#         wv[i, :] = wv1[lev - i - 1, :]
#     wv = wv * 1000# 下面wv单位选为C的话，即g/kg，如果廓线中水汽的质量混合比单位为kg/kg，需要*1000    
    # Read tra data,第一列就是CO2
    with open('/share/home/liuc/yanjunyu/LBLRTM/share_profile/US_STANDARD_ATMOSPHERE_tra.txt', 'r') as file:
        for i in range(lev):
            tra1[i, :] = np.array(file.readline().split(), dtype=np.float32)
    for i in range(lev):
        tra[i, :] = tra1[lev - i - 1, :]

    for i in range(6):
        angle = 1 + 0.25 * i
        va[i] = math.degrees(math.acos(1 / angle))

    height.fill(0.0)
    blank.fill(0.0)

    for iprof in range(prof):
        tsurf[iprof] = t[0, iprof]

    for iadd in range(1):
        bwn = bwn0# + iadd * maxwn
        ewn = ewn0# + iadd * maxwn

        for jj in range(1):
            c1 = str(jj + 1)
            for iprof in range(1000):
                bwn0_str = f"{bwn0:9.3f}".strip()
                ewn0_str = f"{ewn0:9.3f}".strip()
                print(f'TAPE5_{bwn0_str}_{ewn0_str}_{resolution}_{gase_type}廓线{iprof}正在创建')
                c2 = f'{iprof + 1:04d}'
                with open('TAPE5', 'w') as file:
                    CXID = '83P 100level profile to creat transmittance database'
                    file.write(f"${CXID}\n")
                    # 下面一行是LBLRTM设置参数，具体作用查阅html说明文档
                    file.write(f" HI=1 F4=1 CN=1 AE=0 EM=0 SC=0 FI=0 PL=0 TS=0 AM=1 MG=0 LA=0 OD=1 XS=0   00   00\n")
                    # 下面最后一个位置设置分辨率
                    file.write(f"{bwn:10.3f}{ewn:10.3f}                                                            REJ=0     {resolution}\n")
                    file.write(f"{0:5}{2:5}{-101:5}{1:5}{1:5}{7:5}{1:5}{0:5}{0:10.3f}{0:10.3f}\n")
                    file.write(f"{p[lev-1, iprof]:10.3f}{p[0, iprof]:10.3f}{180.000:10.3f}\n")
                    print(p.shape)
                    column_data = p[:, iprof]
                    # 以8个一组分批写入气压数据
                    file.writelines([''.join([f"{x:10.3f}".rstrip() for x in column_data[i:i+8]]) + '\n' for i in range(0, len(column_data), 8)])
                    # file.writelines([f"{'   '.join([f'{x:10.3f}' for x in column_data[i:i+8]])}\n" for i in range(0, len(column_data), 8)])
                    file.write(f"{-101:5}         {'INPUT FOR CAMEX'}\n")
                    for i in range(lev):
                        file.write(f"{height[i]:10.3f}{p[i, iprof]:10.3f}{t[i, iprof]:10.3f}     {'AA'} {'L'} {'CAAAAAA'}\n")
                        file.write(f"{blank[i]:15.8E}{tra[i,0]:15.8E}{blank[i]:15.8E}{blank[i]:15.8E}{blank[i]:15.8E}{blank[i]:15.8E}{blank[i]:15.8E}\n")
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
                # # TAPE5制作好后，运行pl脚本，pl脚本中写着运行模型和输出提示的命令    ##算逑，pl脚本似乎会导致作业失败，直接用py里的系统命令吧
                # 创建目标文件夹，如果不存在则创建
                destination_folder = f'./OD_{gase_type}_seebro4'
                os.makedirs(destination_folder, exist_ok=True)
                # 打印信息
                print("*************************************************")
                # 打印当前工作目录
                subprocess.run(['pwd'])
                print("*************************************************")

                # 删除TAPE3文件（如果存在）
                if os.path.exists('TAPE3'):
                    os.remove('TAPE3')

                # 创建TAPE3的符号链接
                os.symlink('../LNFL-master/TAPE3', 'TAPE3')

                # 运行LBLRTM可执行文件
                print("\nRunning exec: lblrtm\n")
                subprocess.run('time ./lblrtm_v12.17_linux_intel_sgl',shell=True, check=True)
                # subprocess.run(['./script_run_example.pl'], check=False)
                
                for i in range(1,101):

                    bwn_str = f"{bwn:9.3f}".strip()
                    ewn_str = f"{ewn:9.3f}".strip()
                    source = f'ODint_{i:03d}'
                    destination = os.path.join(destination_folder,f'ODint_{i:03d}_{bwn_str}_{ewn_str}_{resolution}_{gase_type}_{iprof}')
                    # 移动并重命名文件
                    #try:
                    os.system(f'mv {source} {destination}')
                    #shutil.move(source, destination)
                        # print(f'Successfully moved {source} to {destination}')
                    #except FileNotFoundError:
                    #    print(f'File {source} not found. Skipping...')
                print(f'ODint_{bwn_str}_{ewn_str}_{resolution}_{gase_type}_{iprof}已改名并归档')
                
