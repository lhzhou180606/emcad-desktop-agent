# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

IPD Emcad — 脚本执行代理。agent 跑在本地执行机上，远程通过 CLI 或 HTTP 调用，执行 Python 脚本并返回结果。

- **`server/`** — Python 代理服务（FastAPI），跑在本地，暴露 `/execute`
- **`client/`** — Node.js CLI 工具（Commander.js），远程通过 HTTP 调用本地 agent

## 启动

本地手动启动 agent：

```bash
cd server && pip install -e .         # 安装，注册 ipd-emcad-agent
ipd-emcad-agent --host 0.0.0.0 --port 9527   # 手动启动
```

远程安装 CLI 后调用：

```bash
cd client && npm run build && npm link  # 注册 ipd-emcad-cli
ipd-emcad-cli config set proxy_host <本地IP>
ipd-emcad-cli script run <script> --arg ... --env KEY=VAL ...
```

## Key Commands

```bash
# 本地 — 手动启动 agent
ipd-emcad-agent --host 0.0.0.0 --port 9527

# 远程 — CLI 调用本地 agent
ipd-emcad-cli config set proxy_host <本地IP>    # 指向本地 agent
ipd-emcad-cli config set proxy_port 9527        # 端口
ipd-emcad-cli script run <script> --arg ... --env KEY=VAL ...
ipd-emcad-cli proxy status

# 打包
cd client && npm run build          # esbuild → dist/ipd-emcad-cli.cjs
cd server && python build.py        # PyInstaller → dist/ipd-emcad-agent/
```

## Architecture

```
├── 本地（执行机）────────────────────────────
│   ipd-emcad-agent --host 0.0.0.0 --port 9527
│   ┌───────────────────┐
│   │  FastAPI (:9527)  │
│   │  /health /status  │
│   │  /execute         │
│   └───────┬───────────┘
│           │ subprocess.run("python3", script, ...args)
│           ▼
│   capture stdout/stderr → return
│
├── 远程（调用方）────────────────────────────
│   ipd-emcad-cli script run → POST http://<本地IP>:9527/execute
```

### server (`server/ipd_emcad_agent/`)

| 文件 | 职责 |
|------|------|
| `main.py` | argparse 入口，启动 uvicorn |
| `server.py` | FastAPI 路由：`/health`, `/status`, `/execute` |
| `executor.py` | `ScriptExecutor.execute()`，subprocess 安全执行 |
| `config.py` | 配置 `~/.ipd-emcad-cli/config.json`，env `EMCAD_*` 覆盖 |

### client (`client/src/`)

| 文件 | 职责 |
|------|------|
| `cli.js` | Commander.js 入口，proxy / script / config |
| `commands/proxy.js` | proxy start/stop/status |
| `commands/script.js` | script run/list |
| `commands/config.js` | config show/set |
| `api.js` | axios HTTP client → agent |

### Script I/O

- **入参**: `--arg foo bar` → `sys.argv[1:]`；`--env KEY=VAL` → `os.environ["KEY"]`
- **出参**: `stdout` (JSON)，`stderr` (日志)，`exit_code` (0=成功)
