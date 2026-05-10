#!/usr/bin/env python3
"""调用代理 API 示例 — 演示入参/出参的完整流程"""
import requests
import json
import os

AGENT_URL = "http://localhost:9527"


def execute(script_path, args=None, env=None, timeout=60, content_mode=False):
    """
    调用代理执行脚本。

    入参:
        script_path: 脚本文件路径 (或代码内容，当 content_mode=True)
        args:        命令行参数列表
        env:         环境变量 dict
        timeout:     超时秒数
        content_mode: True=传入代码内容, False=传入文件路径

    出参 (来自 POST /execute 响应):
        exit_code: 退出码 (0=成功)
        stdout:    脚本标准输出
        stderr:    脚本标准错误
        duration:  执行耗时 (秒)
        task_id:   任务 ID
        error:     异常信息
    """
    payload = {
        "task_id": f"task_{abs(hash(script_path))}",
        "script": script_path,
        "script_type": "content" if content_mode else "path",
        "args": args or [],
        "env": env or {},
        "timeout": timeout,
        "work_dir": "",
    }
    resp = requests.post(f"{AGENT_URL}/execute", json=payload)
    return resp.json()


def print_output(result):
    """解析并展示脚本的出参"""
    # 基础出参
    print(f"  退出码:  {result['exit_code']}")
    print(f"  耗时:    {result['duration']}s")
    print(f"  任务ID:  {result['task_id']}")

    # stdout — 通常承载结构化出参 (JSON)
    stdout = result.get("stdout", "").strip()
    if stdout:
        try:
            data = json.loads(stdout)
            print("  出参 (JSON):")
            print(f"    {json.dumps(data, ensure_ascii=False, indent=4)}")
        except json.JSONDecodeError:
            print(f"  出参 (文本): {stdout}")

    # stderr — 日志信息
    stderr = result.get("stderr", "").strip()
    if stderr:
        print(f"  日志:\n{stderr}")

    # error — 异常信息
    if result.get("error"):
        print(f"  异常: {result['error']}")


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # ── 调用1: 文件路径 + 入参 + 出参 ──────────────────
    print("【调用1】执行脚本文件，传入参数和环境变量")
    result = execute(
        script_path=f"{script_dir}/demo_io.py",
        args=["100", "200", "300"],
        env={"TASK_NAME": "批量计算任务", "BATCH_SIZE": "50"},
    )
    print_output(result)

    # ── 调用2: 传入代码内容 ────────────────────────────
    print("\n【调用2】直接传入代码内容执行")
    code = """
import sys, json
data = {"status": "ok", "items": [1, 2, 3], "count": 3}
print(json.dumps(data, ensure_ascii=False))
"""
    result = execute(
        script_path=code,
        args=["--verbose"],
        content_mode=True,
    )
    print_output(result)

    # ── 调用3: 错误处理 ─────────────────────────────────
    print("\n【调用3】脚本异常处理")
    code = 'print(1/0)'
    result = execute(script_path=code, content_mode=True)
    print_output(result)
