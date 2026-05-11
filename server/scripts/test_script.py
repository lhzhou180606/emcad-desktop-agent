import sys
import platform

print("Hello from IPD Cadtool Agent!")
print(f"Python版本: {sys.version}")
print(f"系统: {platform.platform()}")
print(f"参数: {sys.argv[1:] if len(sys.argv) > 1 else '无'}")
