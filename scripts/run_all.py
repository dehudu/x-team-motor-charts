#!/usr/bin/env python3
"""
X-TEAM Motor Map - 一键运行脚本
================================
依次执行数据生成和图表生成。

用法:
    python scripts/run_all.py
"""

import subprocess
import sys
import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("=" * 60)
    print("🐙 X-TEAM Motor Map - 一键运行")
    print("=" * 60)
    
    # Step 1: Generate data
    print("\n📝 Step 1/2: 生成性能数据...")
    result = subprocess.run(
        [sys.executable, os.path.join(script_dir, "generate_motor_data.py")],
        cwd=script_dir
    )
    
    if result.returncode != 0:
        print("❌ 数据生成失败！")
        sys.exit(1)
    
    # Step 2: Generate charts
    print("\n🎨 Step 2/2: 生成图表...")
    result = subprocess.run(
        [sys.executable, os.path.join(script_dir, "generate_charts.py")],
        cwd=script_dir
    )
    
    if result.returncode != 0:
        print("❌ 图表生成失败！")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✅ 全部完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()
