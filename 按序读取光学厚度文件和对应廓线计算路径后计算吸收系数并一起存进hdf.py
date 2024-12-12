import os
import h5py
import numpy as np
import lblrtm_tape11_reader

# 文件路径
pressure_file = (
    "/Users/user/Desktop/二进制廓线读取/pressure_levels_hPa-_SeeBorV4.0_15704.txt"
)
temperature_file = (
    "/Users/user/Desktop/二进制廓线读取/temperature-K-_profile_SeeBorV4.0_15704.txt"
)
mixing_ratio_file = (
    "/Users/user/Desktop/二进制廓线读取/water_vapour-kgkg-_profile_SeeBorV4.0_15704.txt"
)
ozone_file = (
    "/Users/user/Desktop/二进制廓线读取/ozone-ppmv-_profile_SeeBorV4.0_15704.txt"
)
od_folder = "/Users/user/Desktop/逐层逐廓线整合OD并转化为吸收系数/contiue_testfile"

# 常数
R_d = 287.05  # 干空气气体常数 (J/(kg·K))
g = 9.81  # 重力加速度 (m/s^2)

# 获取所有光学厚度文件信息，按廓线编号提取
od_files = []
profile_set = set()  # 用于存储实际使用的廓线编号
for filename in os.listdir(od_folder):
    if filename.startswith("ODint") and "_H2O_" in filename:
        # 提取层号和廓线编号
        parts = filename.split("_")
        layer = int(parts[1])  # 层号
        profile = int(parts[-1])  # 廓线编号

        od_files.append((layer, profile, filename))
        profile_set.add(profile)  # 添加廓线编号到集合

# 按照廓线编号和层号排序
od_files.sort(key=lambda x: (x[1], x[0]))  # 先按廓线编号排序，再按层号排序

# 加载必要的辅助数据
pressure_boundaries = np.loadtxt(pressure_file, usecols=0) * 100  # hPa 转 Pa
temperature = np.loadtxt(temperature_file)  # 温度矩阵
mixing_ratio = np.loadtxt(mixing_ratio_file)  # 水汽混合比矩阵
ozone = np.loadtxt(ozone_file)  # 臭氧矩阵
num_profiles = len(profile_set)  # 实际使用的廓线数
num_layers = len(pressure_boundaries)  # 层数是气压的总层数
wavenumber_set = None  # 波数集合

# 初始化路径长度数组
delta_z_Top_Bottom = None

# 创建 HDF5 文件并逐步写入
with h5py.File("absorption_data_optimized.h5", "w") as hdf_file:
    # 存储完整的气压数据（包括最上面的一层）
    hdf_file.create_dataset("pressure", data=pressure_boundaries)
    hdf_file["pressure"].attrs["description"] = "Pressure boundaries for layers (Pa)"

    # 存储层数信息（1到100层）
    layer_numbers = np.arange(1, num_layers)
    hdf_file.create_dataset("layer_numbers", data=layer_numbers)
    hdf_file["layer_numbers"].attrs["description"] = "Layer numbers (1 to 100)"

    # 创建与廓线相关的数据集
    # 只存储实际使用的廓线数据
    selected_temperature = temperature[:, list(profile_set)]  # 选取实际用到的廓线
    selected_mixing_ratio = mixing_ratio[:, list(profile_set)]  # 选取实际用到的廓线
    selected_ozone = ozone[:, list(profile_set)]  # 选取实际用到的廓线

    hdf_file.create_dataset("temperature", data=selected_temperature)
    hdf_file["temperature"].attrs[
        "description"
    ] = "Temperature profiles (K) for used profiles"
    hdf_file.create_dataset("mixing_ratio", data=selected_mixing_ratio)
    hdf_file["mixing_ratio"].attrs[
        "description"
    ] = "Mixing ratio profiles (kg/kg) for used profiles"
    hdf_file.create_dataset("ozone", data=selected_ozone)
    hdf_file["ozone"].attrs["description"] = "Ozone profiles (ppmv) for used profiles"

    # 创建一个空的数据集，用于存储吸收系数
    # 修改维度顺序：100 layers, 20001 wavenumbers, 13 profiles
    absorption_ds = hdf_file.create_dataset(
        "absorption_coefficients",
        shape=(num_layers - 1, 20001, num_profiles),  # 重新调整维度顺序
        dtype=np.float32,
        compression="gzip",
        compression_opts=9,
        chunks=(1, 20001, 1),  # 为每一层每个波数做压缩
    )
    absorption_ds.attrs["description"] = (
        "Absorption coefficients for layers, wavenumbers, and profiles (k的单位为m^-1)，特别注意第一层的吸收系数是最下层的吸收系数，依次类推"
    )

    # 存储波数
    for layer, profile, filename in od_files:
        filepath = os.path.join(od_folder, filename)

        # 如果路径长度未初始化，则计算
        if delta_z_Top_Bottom is None:
            delta_z_Top_Bottom = np.zeros(len(pressure_boundaries) - 1)
            # 计算路径长度（保留逻辑）
            for i in range(1, len(pressure_boundaries)):
                p_avg = (pressure_boundaries[i - 1] + pressure_boundaries[i]) / 2
                T_avg = (temperature[i - 1, profile] + temperature[i, profile]) / 2
                q_avg = (mixing_ratio[i - 1, profile] + mixing_ratio[i, profile]) / 2
                rho_wet = p_avg / (R_d * T_avg) * (1 / (1 + 0.61 * q_avg))
                delta_p = pressure_boundaries[i - 1] - pressure_boundaries[i]
                delta_z = -delta_p / (rho_wet * g)
                delta_z_Top_Bottom[i - 1] = delta_z
            delta_z_Bottom_Top = delta_z_Top_Bottom[::-1]  # 反转路径长度

        # 读取光学厚度文件
        v, OD = lblrtm_tape11_reader.lblrtm_tape11_reader1(filepath, "s")

        if wavenumber_set is None:
            wavenumber_set = v
            hdf_file.create_dataset("wavenumbers", data=wavenumber_set)
            hdf_file["wavenumbers"].attrs["description"] = "Wavenumbers (cm^-1)"

        # 获取对应层的路径长度
        path_length = delta_z_Bottom_Top[layer - 1]

        # 计算吸收系数
        absorption_coefficient = OD / path_length

        # 获取廓线编号在 HDF5 中的索引
        profile_index = list(profile_set).index(profile)

        # 写入到 HDF5 数据集（维度已调整为 layer, wavenumber, profile）
        absorption_ds[layer - 1, :, profile_index] = absorption_coefficient
