#!/usr/bin/env python3
"""
X-TEAM Motor Performance Chart Generator
=========================================
从 CSV 性能数据自动生成电机性能地图图表。
替代 MATLAB 版本，纯 Python 实现（matplotlib + numpy）。

输出图表：
1. 扭矩 3D 曲面图 (RPM × 电流 → 扭矩)
2. 效率 3D 曲面图 (RPM × 电流 → 效率)
3. 轴功率 3D 曲面图 (RPM × 电流 → 功率)
4. 扭矩等高线图
5. 效率等高线图
6. 轴功率等高线图

作者: GitHub 操作专家 🐙
日期: 2026-06-09
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
import csv
import os
import glob
from scipy.interpolate import griddata
import warnings
warnings.filterwarnings('ignore')

# 中文字体设置
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def load_csv_data(csv_dir):
    """加载目录下所有 CSV 文件的数据"""
    all_currents = []
    all_input_powers = []
    all_rpms = []
    all_torques = []
    all_output_powers = []
    all_efficiencies = []
    voltage_labels = []
    
    csv_files = sorted(glob.glob(os.path.join(csv_dir, "V*.csv")))
    
    for filepath in csv_files:
        filename = os.path.basename(filepath)
        voltage = filename.replace("V", "").replace(".csv", "")
        voltage_labels.append(f"{voltage}V")
        
        with open(filepath, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 6:
                    all_currents.append(float(row[0]))
                    all_input_powers.append(float(row[1]))
                    all_rpms.append(float(row[2]))
                    all_torques.append(float(row[3]))
                    all_output_powers.append(float(row[4]))
                    all_efficiencies.append(float(row[5]))
    
    return {
        'current': np.array(all_currents),
        'input_power': np.array(all_input_powers),
        'rpm': np.array(all_rpms),
        'torque': np.array(all_torques),
        'output_power': np.array(all_output_powers),
        'efficiency': np.array(all_efficiencies),
        'voltages': voltage_labels
    }

def generate_3d_surface(x, y, z, x_label, y_label, z_label, title, save_path):
    """生成 3D 曲面图"""
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # 网格化
    xi = np.linspace(min(x), max(x), 100)
    yi = np.linspace(min(y), max(y), 100)
    Xi, Yi = np.meshgrid(xi, yi)
    Zi = griddata((x, y), z, (Xi, Yi), method='cubic')
    
    # 绘制曲面
    surf = ax.plot_surface(Xi, Yi, Zi, cmap=cm.viridis, 
                           alpha=0.9, edgecolor='none', antialiased=True)
    
    ax.set_xlabel(x_label, fontsize=12)
    ax.set_ylabel(y_label, fontsize=12)
    ax.set_zlabel(z_label, fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    
    fig.colorbar(surf, ax=ax, shrink=0.5, aspect=10, label=z_label)
    
    ax.view_init(elev=25, azim=-120)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  📊 {save_path}")

def generate_contour(x, y, z, x_label, y_label, z_label, title, save_path, levels=20):
    """生成等高线图"""
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # 网格化
    xi = np.linspace(min(x), max(x), 200)
    yi = np.linspace(min(y), max(y), 200)
    Xi, Yi = np.meshgrid(xi, yi)
    Zi = griddata((x, y), z, (Xi, Yi), method='cubic')
    
    # 绘制等高线
    if z_label == '效率 (%)':
        levels = np.arange(0, 100, 5)
    elif z_label == '扭矩 (Ncm)':
        levels = 25
    else:
        levels = 20
    
    contour = ax.contourf(Xi, Yi, Zi, levels=levels, cmap=cm.viridis, alpha=0.9)
    ax.contour(Xi, Yi, Zi, levels=levels, colors='white', linewidths=0.5, alpha=0.5)
    
    ax.set_xlabel(x_label, fontsize=12)
    ax.set_ylabel(y_label, fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    
    cbar = fig.colorbar(contour, ax=ax, shrink=0.8, aspect=20, label=z_label)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  📊 {save_path}")

def generate_all_charts(motor_name, data_dir, output_dir):
    """为单个电机生成所有图表"""
    data = load_csv_data(data_dir)
    
    if not data['current'].size:
        print(f"  ⚠️ 无数据，跳过 {motor_name}")
        return
    
    os.makedirs(output_dir, exist_ok=True)
    
    rpm = data['rpm']
    current = data['current']
    torque = data['torque']
    efficiency = data['efficiency']
    output_power = data['output_power']
    
    print(f"\n🎨 生成 {motor_name} 图表...")
    
    # 1. 扭矩 3D 曲面
    generate_3d_surface(
        rpm, current, torque,
        '转速 (RPM)', '电流 (A)', '扭矩 (Ncm)',
        f'{motor_name} - 扭矩特性',
        os.path.join(output_dir, f'{motor_name}_torque_3d.png')
    )
    
    # 2. 效率 3D 曲面
    generate_3d_surface(
        rpm, current, efficiency,
        '转速 (RPM)', '电流 (A)', '效率 (%)',
        f'{motor_name} - 效率特性',
        os.path.join(output_dir, f'{motor_name}_efficiency_3d.png')
    )
    
    # 3. 轴功率 3D 曲面
    generate_3d_surface(
        rpm, current, output_power,
        '转速 (RPM)', '电流 (A)', '轴功率 (W)',
        f'{motor_name} - 轴功率特性',
        os.path.join(output_dir, f'{motor_name}_power_3d.png')
    )
    
    # 4. 扭矩等高线
    generate_contour(
        rpm, current, torque,
        '转速 (RPM)', '电流 (A)', '扭矩 (Ncm)',
        f'{motor_name} - 扭矩等高线',
        os.path.join(output_dir, f'{motor_name}_torque_contour.png')
    )
    
    # 5. 效率等高线
    generate_contour(
        rpm, current, efficiency,
        '转速 (RPM)', '电流 (A)', '效率 (%)',
        f'{motor_name} - 效率等高线',
        os.path.join(output_dir, f'{motor_name}_efficiency_contour.png')
    )
    
    # 6. 轴功率等高线
    generate_contour(
        rpm, current, output_power,
        '转速 (RPM)', '电流 (A)', '轴功率 (W)',
        f'{motor_name} - 轴功率等高线',
        os.path.join(output_dir, f'{motor_name}_power_contour.png')
    )

def main():
    """主函数：批量生成所有电机的图表"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    charts_dir = os.path.join(base_dir, "charts")
    
    print("=" * 60)
    print("🐙 X-TEAM 电机性能图表生成器")
    print("=" * 60)
    
    motor_dirs = sorted([
        d for d in os.listdir(data_dir) 
        if os.path.isdir(os.path.join(data_dir, d))
    ])
    
    if not motor_dirs:
        print("❌ 未找到电机数据！请先运行 generate_motor_data.py")
        return
    
    for motor_name in motor_dirs:
        motor_data_dir = os.path.join(data_dir, motor_name)
        motor_charts_dir = os.path.join(charts_dir, motor_name)
        generate_all_charts(motor_name, motor_data_dir, motor_charts_dir)
    
    print(f"\n{'=' * 60}")
    print(f"✅ 完成！图表已保存到: {charts_dir}")
    print(f"{'=' * 60}")

if __name__ == "__main__":
    main()
