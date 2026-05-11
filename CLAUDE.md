# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

IPD Cadtool — 脚本执行代理。agent 跑在本地执行机上，远程通过 CLI 或 HTTP 调用，执行 Python 脚本并返回结果。

- **`server/`** — Python 代理服务（FastAPI），跑在本地，暴露 `/execute`
- **`client/`** — Node.js CLI 工具（Commander.js），远程通过 HTTP 调用本地 agent

## 启动

### 本地执行机 — 启动 agent

**方式一：源码启动**

```bash
cd server && pip install -e .
ipd-cadtool-agent --host 0.0.0.0 --port 9527
```

**方式二：打包后启动**

Mac:
```bash
cd server/dist/ipd-cadtool-agent
./ipd-cadtool-agent --host 0.0.0.0 --port 9527
```

Windows:
```batch
cd server\dist\ipd-cadtool-agent
ipd-cadtool-agent.exe --host 0.0.0.0 --port 9527
```

agent 启动后监听 `http://0.0.0.0:9527`，暴露 `/health`、`/status`、`/execute` 三个端点。

### 远程调用方 — 安装 CLI

```bash
cd client && npm run build && npm link  # 全局注册 ipd-cadtool-cli
```

使用前配置指向本地执行机：

```bash
ipd-cadtool-cli config set proxy_host <执行机IP>
ipd-cadtool-cli config set proxy_port 9527
```

## Key Commands

```bash
# 本地 — 启动 agent
ipd-cadtool-agent --host 0.0.0.0 --port 9527

# 远程 — CLI 调用
ipd-cadtool-cli config set proxy_host <执行机IP>
ipd-cadtool-cli config set proxy_port 9527
ipd-cadtool-cli script run <script> --arg ... --env KEY=VAL ...
ipd-cadtool-cli proxy status

# 打包
cd client && npm run build                              # esbuild → dist/ipd-cadtool-cli.cjs
cd server && python build.py                            # Mac PyInstaller → dist/ipd-cadtool-agent/
cd server && build.bat                                  # Windows PyInstaller → dist/ipd-cadtool-agent/
```

## 打包

### Mac

```bash
cd server
python build.py
# 产物: dist/ipd-cadtool-agent/ipd-cadtool-agent (单目录，约 25MB)
```

### Windows

在 Windows 机器上运行：

```batch
cd server
build.bat
:: 产物: dist\ipd-cadtool-agent\ipd-cadtool-agent.exe
```

> Windows 无法从 macOS 交叉编译，需在 Windows 环境或 CI 中构建。

### server 打包说明

- PyInstaller 将 Python 解释器 + 依赖 + 源码打包为独立目录 (`--onedir`)
- `--add-data` 在 Mac 用 `:` 分隔，Windows 用 `;` 分隔（`build.py` 和 `build.bat` 各自处理）

### client 打包

```bash
cd client && npm run build
# esbuild 将 ESM 源码打包为 CJS → dist/ipd-cadtool-cli.cjs
# 入口: bin/ipd-cadtool-cli.js → dist/ipd-cadtool-cli.cjs
```

## Architecture

```
├── 本地（执行机）────────────────────────────
│   ipd-cadtool-agent --host 0.0.0.0 --port 9527
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
│   ipd-cadtool-cli script run → POST http://<本地IP>:9527/execute
```

### server (`server/ipd_cadtool_agent/`)

| 文件 | 职责 |
|------|------|
| `main.py` | argparse 入口，启动 uvicorn |
| `server.py` | FastAPI 路由：`/health`, `/status`, `/execute` |
| `executor.py` | `ScriptExecutor.execute()`，subprocess 安全执行 |
| `config.py` | 配置 `~/.ipd-cadtool-cli/config.json`，env `CADTOOL_*` 覆盖 |

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
