#!/usr/bin/env python3
"""PyInstaller 打包脚本 — 将 ipd-cadtool-agent 打包为独立可执行文件

用法:
    python build.py           # 打包当前平台
    python build.py --onefile # 单文件模式
"""

import subprocess
import sys
from pathlib import Path


def build():
    onefile = "--onefile" in sys.argv

    cmd = [
        "pyinstaller",
        "--name", "ipd-cadtool-agent",
        "--add-data", f"ipd_cadtool_agent:ipd_cadtool_agent",
    ]

    if onefile:
        cmd.append("--onefile")
    else:
        cmd.append("--onedir")

    cmd.extend([
        "--clean",
        "--noconfirm",
        "ipd_cadtool_agent/main.py",
    ])

    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)

    dist = Path("dist")
    if onefile:
        print(f"\n打包完成: {dist / 'ipd-cadtool-agent'}")
    else:
        print(f"\n打包完成: {dist / 'ipd-cadtool-agent' / 'ipd-cadtool-agent'}")


if __name__ == "__main__":
    print("注意: 需要先安装 pyinstaller: pip install pyinstaller")
    print()
    build()
