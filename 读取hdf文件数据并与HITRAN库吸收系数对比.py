# %%
import h5py
import numpy as np
import matplotlib.pyplot as plt

# 读取 HDF5 文件
hdf_file_path = (
    "/Users/user/Desktop/逐层逐廓线整合OD并转化为吸收系数/absorption_data_optimized.h5"
)

with h5py.File(hdf_file_path, "r") as hdf_file:
    # 读取波数数据
    wavenumbers = hdf_file["wavenumbers"][:]

    # 读取吸收系数数据
    absorption_coefficients = hdf_file["absorption_coefficients"][:]

    # 获取廓线编号和层号信息
    num_layers, num_wavenumbers, num_profiles = absorption_coefficients.shape
    print(
        f"Number of layers: {num_layers}, Number of wavenumbers: {num_wavenumbers}, Number of profiles: {num_profiles}"
    )

    # 选择绘制的层号和廓线编号（可以修改）
    selected_layer = 0  # 第10层（从0开始计数）
    selected_profile = 0  # 第1个廓线编号（从0开始计数）

    # 确保索引合法
    if selected_layer >= num_layers or selected_profile >= num_profiles:
        raise ValueError("Selected layer or profile index is out of range.")

    # 提取指定层和廓线的吸收系数
    absorption = absorption_coefficients[selected_layer, :, selected_profile]

# 绘制吸收系数随波数的变化图
plt.figure(figsize=(10, 6))
plt.plot(
    wavenumbers,
    absorption / 100,
    label=f"Layer {selected_layer + 1}, Profile {selected_profile + 1}",
)
# plt.yscale("log")
plt.xlabel("Wavenumber (cm⁻¹)")
plt.ylabel("Absorption Coefficient (m⁻¹)")
plt.title("Absorption Coefficient of Water Vapor")
plt.legend()
plt.grid(True)
plt.show()

# %%
# 导入HAPI库
from hapi import *
import matplotlib.pyplot as plt

# 初始化HAPI数据库文件
db_begin("data")

# 设置水汽的分子ID为1，并指定吸收线宽和温度、压强等参数
molecule_id = 1  # 水汽的HITRAN分子ID
isotope = 1  # 同位素标记
wavenumber_min = 600  # 波数范围最小值 (cm^-1)
wavenumber_max = 1200  # 波数范围最大值 (cm^-1)
temperature = 297.43  # 温度 (开尔文)
pressure = 1.08545  # 压强 (大气压)。

# 下载数据
fetch("H2O", molecule_id, isotope, wavenumber_min, wavenumber_max)

# 自定义波数范围，设置间隔为0.03 cm^-1
custom_wavenumbers = [
    wavenumber_min + i * 0.03
    for i in range(int((wavenumber_max - wavenumber_min) / 0.03) + 1)
]

# 生成吸收系数
nu, coef = absorptionCoefficient_Voigt(
    SourceTables="H2O",
    WavenumberGrid=custom_wavenumbers,  # 使用自定义波数网格
    Environment={"T": temperature, "p": pressure},
    HITRAN_units=True,
)


plt.figure(figsize=(10, 6))
plt.plot(nu, coef, c="r")
# plt.yscale("log")
plt.xlabel("Wavenumber (cm^-1)")
plt.ylabel("Absorption Coefficient ($cm^2 / molecule$)")
plt.title("Absorption Coefficient of Water Vapor  N_0 = 1$molecule/cm^3$  (HITRAN-API)")
plt.legend()
plt.grid(True)
plt.show()

plt.figure(figsize=(10, 6))
plt.plot(nu, coef * 1e-4 * 7.03290505250247e23, c="r", label="HITRAN-API")
plt.plot(
    wavenumbers,
    absorption,
    # c="b",
    linestyle="-",
    label=f"Layer {selected_layer + 1}, Profile {selected_profile + 1}",
)
# plt.plot(
#     wavenumbers,
#     absorption - coef * 1e-4 * 7.03290505250247e23,
#     c="k",
#     label=f"HITRAN - LBLRTM(no_continuum)",
# )
# plt.plot(nu, coef * 1e-4 * 7.03290505250247e23, c="r", label="HITRAN-API")
plt.yscale("log")
plt.xlabel("Wavenumber (cm^-1)")
plt.ylabel("Absorption Coefficient ($m^{-1}$)")
plt.title("Absorption Coefficient of Water Vapor ")
plt.legend()
plt.grid(True)
plt.show()
# %%
