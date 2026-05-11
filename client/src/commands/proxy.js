import { spawn } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import chalk from "chalk";
import { getConfig, setConfig } from "./config.js";
import { healthCheck, getStatus } from "../api.js";

const CFG_DIR = path.join(os.homedir(), ".ipd-cadtool-cli");

function pidPath() {
  return path.join(CFG_DIR, "proxy.pid");
}

function _spawn(cmd, args, host, port, onNotFound) {
  const child = spawn(cmd, args, { detached: true, stdio: "ignore" });
  let started = false;
  child.on("spawn", () => {
    started = true;
    fs.mkdirSync(CFG_DIR, { recursive: true });
    fs.writeFileSync(pidPath(), String(child.pid));
    // 等 2 秒确认进程没挂
    setTimeout(() => {
      try { process.kill(child.pid, 0); } catch {
        fs.unlinkSync(pidPath());
        console.error(chalk.red("代理启动后异常退出，请检查端口是否被占用"));
        return;
      }
      console.log(chalk.green(`代理已启动 (PID=${child.pid}): http://${host}:${port}`));
    }, 2000);
  });
  child.on("error", (err) => {
    if (!started && err.code === "ENOENT" && onNotFound) {
      onNotFound();
    } else if (!started) {
      console.error(chalk.red(`启动代理失败: ${err.message}`));
    }
  });
  child.unref();
}

export async function proxyStart(opts = {}) {
  const cfg = getConfig();
  const host = opts.host || cfg.proxy_host;
  const port = opts.port || cfg.proxy_port;

  if (opts.port) setConfig("proxy_port", String(port));
  if (opts.host) setConfig("proxy_host", host);

  try {
    const h = await healthCheck();
    if (h && h.status === "ok") {
      console.log(chalk.yellow(`代理已在运行: http://${host}:${port}`));
      return;
    }
  } catch {}

  const args = [];
  if (host) args.push("--host", host);
  if (port) args.push("--port", String(port));

  // 尝试 ipd-cadtool-agent，找不到则用 python3 -m 兜底
  _spawn("ipd-cadtool-agent", args, host, port, () => {
    _spawn("python3", ["-m", "ipd_cadtool_agent.main", ...args], host, port);
  });
}

export function proxyStop() {
  try {
    const pid = fs.readFileSync(pidPath(), "utf8").trim();
    process.kill(Number(pid), "SIGTERM");
    fs.unlinkSync(pidPath());
    console.log(chalk.green(`代理已停止 (PID=${pid})`));
  } catch {
    const cfg = getConfig();
    const child = spawn("lsof", ["-ti:" + cfg.proxy_port], { stdio: "pipe" });
    child.stdout.on("data", (data) => {
      data.toString().trim().split("\n").forEach((p) => {
        try { process.kill(Number(p), "SIGKILL"); } catch {}
      });
    });
    console.log(chalk.green("代理已停止"));
  }
}

export async function proxyStatus() {
  try {
    return await getStatus();
  } catch {
    return null;
  }
}

