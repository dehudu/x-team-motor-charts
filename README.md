# 🐙 X-TEAM Motor Performance Map Generator

> 从电机规格参数自动生成完整的性能地图图表 — 纯 Python 实现，零成本，开箱即用

基于 [lehner-motoren-map](https://github.com/dciliberti/lehner-motoren-map) 架构，专为 X-TEAM 无刷电机系列优化。

---

## ✨ 特性

- 📊 **自动性能曲线生成** — 从 KV、内阻、空载电流等基础参数推算完整性能数据
- 🎨 **6 种图表输出** — 3D 曲面图 + 等高线图（扭矩/效率/轴功率）
- 🔋 **多电压支持** — 自动适配 2S-6S 锂电池配置
- 🐍 **纯 Python** — 无需 MATLAB，`numpy` + `matplotlib` 即可运行
- 📦 **批量处理** — 一键生成全系列电机图表

---

## 📦 安装

```bash
# 克隆仓库
git clone https://github.com/dehudu/x-team-motor-map.git
cd x-team-motor-map

# 安装依赖
pip install numpy matplotlib scipy
```

---

## 🚀 快速开始

### 1. 生成性能数据

```bash
python scripts/generate_motor_data.py
```

输出：`data/<电机型号>/V*.csv` 文件

### 2. 生成图表

```bash
python scripts/generate_charts.py
```

输出：`charts/<电机型号>/*.png` 图表文件

### 3. 一键运行

```bash
python scripts/run_all.py
```

---

## 📁 项目结构

```
x-team-motor-map/
├── data/                    # 电机性能数据 CSV
│   ├── X2212-980KV/
│   │   ├── V11.1.csv
│   │   └── V14.8.csv
│   ├── X2212-1400KV/
│   │   ├── V7.4.csv
│   │   └── V11.1.csv
│   └── ...
├── charts/                  # 生成的图表
│   ├── X2212-980KV/
│   │   ├── X2212-980KV_torque_3d.png
│   │   ├── X2212-980KV_efficiency_3d.png
│   │   ├── X2212-980KV_power_3d.png
│   │   ├── X2212-980KV_torque_contour.png
│   │   ├── X2212-980KV_efficiency_contour.png
│   │   └── X2212-980KV_power_contour.png
│   └── ...
├── scripts/
│   ├── generate_motor_data.py   # 数据生成脚本
│   ├── generate_charts.py       # 图表生成脚本
│   └── run_all.py               # 一键运行
├── README.md
└── LICENSE
```

---

## 🔧 添加自定义电机

编辑 `scripts/generate_motor_data.py` 中的 `X_TEAM_MOTORS` 字典：

```python
X_TEAM_MOTORS = {
    "自定义型号": MotorSpec(
        name="自定义型号",
        kv=1000,          # KV 值 (RPM/V)
        r_internal=0.10,  # 内阻 (Ω)
        i_no_load=1.2,    # 空载电流 (A)
        i_max=25,         # 最大电流 (A)
        v_ref=11.1,       # 参考电压 (V)
        efficiency_peak=0.90  # 峰值效率
    ),
}
```

然后在 `MOTOR_VOLTAGES` 中添加适用电压：

```python
MOTOR_VOLTAGES = {
    "自定义型号": [7.4, 11.1, 14.8],  # 2S-4S
}
```

---

## 📊 图表说明

| 图表类型 | 说明 |
|---------|------|
| 扭矩 3D 曲面 | 转速 × 电流 → 扭矩输出能力 |
| 效率 3D 曲面 | 转速 × 电流 → 效率分布 |
| 轴功率 3D 曲面 | 转速 × 电流 → 功率输出 |
| 扭矩等高线 | 扭矩等值线，快速查找工作点 |
| 效率等高线 | 高效区一目了然 |
| 轴功率等高线 | 功率边界清晰可见 |

---

## ⚙️ 电机模型原理

基于直流无刷电机物理方程：

```
反电动势: E = V - I × R
转速:     RPM = KV × E
扭矩常数: Kt = 60 / (2π × KV)  [N·m/A]
扭矩:     T = Kt × (I - I₀)
输入功率: P_in = V × I
输出功率: P_out = T × ω
效率:     η = P_out / P_in × 100%
```

---

## 📋 已支持电机

| 系列 | 型号 | KV | 最大电流 | 适用电压 |
|------|------|-----|---------|---------|
| 朗宇 X22 | X2212-980KV | 980 | 25A | 3S-4S |
| 朗宇 X22 | X2212-1400KV | 1400 | 20A | 2S-3S |
| 朗宇 X22 | X2216-800KV | 800 | 35A | 3S-5S |
| XXD 2212 | XXD2212-1000KV | 1000 | 22A | 3S |
| XXD 2212 | XXD2212-2200KV | 2200 | 18A | 2S |

---

## 📝 License

MIT License — 详见 [LICENSE](LICENSE)

---

*🐙 Created with ❤️ by GitHub 操作专家*
