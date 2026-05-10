#!/usr/bin/env python3
"""演示脚本：入参/出参模式"""
import sys
import json
import os

# ── 入参 ────────────────────────────────────
# 方式1: 命令行参数 (--arg key value ...)
args = sys.argv[1:] if len(sys.argv) > 1 else []

# 方式2: 环境变量
env_name = os.environ.get("TASK_NAME", "未设置")

# ── 业务逻辑 ────────────────────────────────
result = {
    "success": True,
    "message": f"处理完成，收到 {len(args)} 个参数",
    "input": {
        "args": args,
        "env_task_name": env_name,
    },
    "output": {
        "sum": sum(int(a) for a in args if a.lstrip("-").isdigit()),
        "count": len(args),
    },
}

# ── 出参 ────────────────────────────────────
# stdout: 结构化结果（JSON）
print(json.dumps(result, ensure_ascii=False, indent=2))

# stderr: 日志信息
print(f"[INFO] 脚本开始，参数: {args}", file=sys.stderr)
print(f"[INFO] 脚本结束", file=sys.stderr)

sys.exit(0)
