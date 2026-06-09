#!/usr/bin/env python3
"""
X-TEAM Motor Performance Data Generator
========================================
从电机规格参数（KV、内阻、空载电流等）自动生成完整的性能曲线 CSV 数据。
基于直流无刷电机物理模型，生成与 lehner-motoren-map 兼容的格式。

输出格式 CSV 列：
  电流(A), 输入功率(W), 转速(RPM), 扭矩(Ncm), 输出功率(W), 效率(%)

作者: GitHub 操作专家 🐙
日期: 2026-06-09
"""

import numpy as np
import csv
import os
import json
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class MotorSpec:
    """电机规格参数"""
    name: str           # 型号名称
    kv: float           # KV 值 (RPM/V)
    r_internal: float   # 内阻 (Ω)
    i_no_load: float    # 空载电流 (A) @ 参考电压
    i_max: float        # 最大电流 (A)
    v_ref: float = 11.1 # 参考电压 (V)，默认 3S
    efficiency_peak: float = 0.90  # 峰值效率估计值

def kv_to_kt(kv_rpm_per_v: float) -> float:
    """
    KV (RPM/V) → Kt (N·m/A)
    Kt = 60 / (2π × KV)
    """
    return 60.0 / (2.0 * np.pi * kv_rpm_per_v)

def generate_performance_curve(
    motor: MotorSpec,
    voltage: float,
    n_points: int = 50
) -> List[Dict]:
    """
    生成单个电压下的完整性能曲线数据点。
    
    电机方程：
    - 反电动势: E = V - I × R
    - 转速: RPM = KV × E = KV × (V - I × R)
    - 扭矩常数: Kt = 60 / (2π × KV)  [N·m/A]
    - 有效电流: I_eff = I - I_no_load
    - 扭矩: T = Kt × I_eff  [N·m]
    - 输入功率: P_in = V × I  [W]
    - 角速度: ω = RPM × 2π / 60  [rad/s]
    - 输出功率: P_out = T × ω  [W]
    - 效率: η = P_out / P_in × 100  [%]
    """
    kt = kv_to_kt(motor.kv)
    
    # 空载电流随电压线性缩放
    i_no_load_scaled = motor.i_no_load * (voltage / motor.v_ref)
    
    # 电流范围：从空载到最大
    currents = np.linspace(i_no_load_scaled * 0.5, motor.i_max, n_points)
    
    data_points = []
    
    for i in currents:
        # 反电动势
        emf = voltage - i * motor.r_internal
        
        if emf <= 0:
            continue
            
        # 转速
        rpm = motor.kv * emf
        
        # 有效电流（产生扭矩的部分）
        i_eff = max(0, i - i_no_load_scaled)
        
        # 扭矩 (N·m → Ncm)
        torque_nm = kt * i_eff
        torque_ncm = torque_nm * 100.0
        
        # 输入功率
        p_in = voltage * i
        
        # 角速度
        omega = rpm * 2.0 * np.pi / 60.0
        
        # 输出功率
        p_out = torque_nm * omega
        
        # 效率
        if p_in > 0:
            efficiency = (p_out / p_in) * 100.0
        else:
            efficiency = 0.0
        
        # 效率不能超过物理极限，也不能为负
        efficiency = max(0.0, min(efficiency, motor.efficiency_peak * 100.0 * 1.05))
        
        # 输出功率不能大于输入功率
        p_out = min(p_out, p_in * motor.efficiency_peak * 1.05)
        
        data_points.append({
            'current': round(i, 2),
            'input_power': round(p_in, 2),
            'rpm': round(rpm, 1),
            'torque_ncm': round(torque_ncm, 2),
            'output_power': round(p_out, 2),
            'efficiency': round(efficiency, 1)
        })
    
    return data_points

def generate_all_voltages(
    motor: MotorSpec,
    voltages: List[float],
    output_dir: str
) -> List[str]:
    """为多个电压生成 CSV 文件"""
    os.makedirs(output_dir, exist_ok=True)
    files_created = []
    
    for v in voltages:
        data = generate_performance_curve(motor, v)
        
        if not data:
            continue
            
        filename = f"V{v}.csv"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            for point in data:
                writer.writerow([
                    point['current'],
                    point['input_power'],
                    point['rpm'],
                    point['torque_ncm'],
                    point['output_power'],
                    point['efficiency']
                ])
        
        files_created.append(filepath)
        print(f"  ✅ {filename}: {len(data)} 数据点")
    
    return files_created

# ============================================================
# X-TEAM 全系列电机参数数据库
# ============================================================

X_TEAM_MOTORS = {
    # 朗宇 X22 系列
    "X2212-980KV": MotorSpec(
        name="X2212-980KV", kv=980, r_internal=0.08,
        i_no_load=1.2, i_max=25, v_ref=11.1, efficiency_peak=0.90
    ),
    "X2212-1400KV": MotorSpec(
        name="X2212-1400KV", kv=1400, r_internal=0.12,
        i_no_load=1.0, i_max=20, v_ref=11.1, efficiency_peak=0.89
    ),
    "X2216-800KV": MotorSpec(
        name="X2216-800KV", kv=800, r_internal=0.06,
        i_no_load=1.5, i_max=35, v_ref=11.1, efficiency_peak=0.91
    ),
    # XXD 2212 系列
    "XXD2212-1000KV": MotorSpec(
        name="XXD2212-1000KV", kv=1000, r_internal=0.10,
        i_no_load=1.3, i_max=22, v_ref=11.1, efficiency_peak=0.85
    ),
    "XXD2212-2200KV": MotorSpec(
        name="XXD2212-2200KV", kv=2200, r_internal=0.18,
        i_no_load=1.1, i_max=18, v_ref=7.4, efficiency_peak=0.83
    ),
}

# 各电机适用的电压列表（基于适用电压范围）
MOTOR_VOLTAGES = {
    "X2212-980KV":    [11.1, 14.8],           # 3S-4S
    "X2212-1400KV":   [7.4, 11.1],            # 2S-3S
    "X2216-800KV":    [11.1, 14.8, 18.5],     # 3S-5S
    "XXD2212-1000KV": [11.1],                  # 3S
    "XXD2212-2200KV": [7.4],                   # 2S
}

def main():
    """主函数：批量生成所有电机的性能数据"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    
    print("=" * 60)
    print("🐙 X-TEAM 电机性能数据生成器")
    print("=" * 60)
    
    total_files = 0
    
    for motor_name, motor_spec in X_TEAM_MOTORS.items():
        print(f"\n🔧 生成 {motor_name} 数据...")
        print(f"   KV={motor_spec.kv}, R={motor_spec.r_internal}Ω, "
              f"I₀={motor_spec.i_no_load}A, Imax={motor_spec.i_max}A")
        
        voltages = MOTOR_VOLTAGES.get(motor_name, [11.1])
        motor_dir = os.path.join(data_dir, motor_name)
        
        files = generate_all_voltages(motor_spec, voltages, motor_dir)
        total_files += len(files)
    
    print(f"\n{'=' * 60}")
    print(f"✅ 完成！共生成 {total_files} 个 CSV 文件")
    print(f"📁 数据目录: {data_dir}")
    print(f"{'=' * 60}")

if __name__ == "__main__":
    main()
