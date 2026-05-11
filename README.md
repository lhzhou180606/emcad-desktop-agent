# IPD Cadtool

脚本执行代理 — agent 跑在本地执行机上，远程通过 CLI 或 HTTP 调用，执行 Python 脚本并返回结果。

## 项目结构

```
server/                  # Python 代理服务 (FastAPI)，跑在本地执行机
├── ipd_cadtool_agent/     # 源码
└── scripts/             # 示例脚本

client/                  # Node.js CLI 工具 (Commander.js)，远程调用
├── src/                 # 源码
├── dist/                # 打包产物
└── bin/                 # CLI 入口
```

## 启动

### 本地（执行机）— 手动启动 agent

```bash
cd server
pip install -e .
ipd-cadtool-agent --host 0.0.0.0 --port 9527
```

### 远程（调用方）— 安装 CLI

```bash
cd client


npm link
```

## 调用

```bash
# 远程 CLI 调用本地 agent
ipd-cadtool-cli config set proxy_host <本地IP>
ipd-cadtool-cli script run demo.py --arg 1 2 3 --env KEY=VAL

# 或 HTTP 直接调用
curl -X POST http://<本地IP>:9527/execute \
  -H "Content-Type: application/json" \
  -d '{"task_id":"t1","script":"/path/to/script.py","script_type":"path","args":[],"env":{}}'
```

## CLI 命令

```
ipd-cadtool-cli [命令]

命令:
  script run <脚本>         执行 Python 脚本
  config show               查看配置
  config set <key> <val>    设置配置
```

### script run 选项

```
--arg <args...>       脚本命令行参数
--env <KEY=VAL ...>   环境变量
--timeout <seconds>   超时秒数 (默认 60)
--content             传入代码内容而非文件路径
```

## 脚本入参/出参

```python
import sys, json, os

# 入参: 命令行参数
args = sys.argv[1:]

# 入参: 环境变量
env_val = os.environ.get("MY_VAR")

# 出参: stdout 输出 JSON
print(json.dumps({"status": "ok", "result": {}}))
```

## HTTP API

agent 启动后暴露以下接口（默认 `http://0.0.0.0:9527`）：

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/health` | 健康检查 |
| POST | `/execute` | 执行脚本 |

### /execute

入参：

```json
{
  "task_id": "唯一任务ID",
  "script": "脚本路径或代码内容",
  "script_type": "path | content",
  "args": ["参数列表"],
  "env": {"KEY": "VAL"},
  "timeout": 60
}
```

出参：

```json
{
  "task_id": "任务ID",
  "exit_code": 0,
  "stdout": "脚本标准输出",
  "stderr": "脚本标准错误",
  "duration": 0.05,
  "error": "异常信息（无异常时为空）"
}
```

调用示例见 `server/scripts/call_agent.py`。

## 打包

```bash
cd client && npm run build          # esbuild → dist/ipd-cadtool-cli.cjs
cd server && python build.py        # PyInstaller → dist/ipd-cadtool-agent/
```

## 配置

配置文件 `~/.ipd-cadtool-cli/config.json`，环境变量 `CADTOOL_<KEY>` 可覆盖：

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| proxy_host | 0.0.0.0 | 本地 agent 监听地址 |
| proxy_port | 9527 | 本地 agent 监听端口 |
