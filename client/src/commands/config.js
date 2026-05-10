import fs from "node:fs";
import path from "node:path";
import os from "node:os";
import chalk from "chalk";

const CONFIG_DIR = path.join(os.homedir(), ".ipd-emcad-cli");
const CONFIG_FILE = path.join(CONFIG_DIR, "config.json");

const DEFAULTS = {
  proxy_host: "0.0.0.0",
  proxy_port: "9527",
  server_url: "",
  auth_token: "",
  agent_id: "",
  heartbeat_interval: "30",
  pull_interval: "10",
};

function envOverride(key, value) {
  const envKey = `EMCAD_${key.toUpperCase()}`;
  const envVal = process.env[envKey];
  return envVal !== undefined ? envVal : value;
}

export function getConfig() {
  let cfg = { ...DEFAULTS };
  try {
    if (fs.existsSync(CONFIG_FILE)) {
      const raw = JSON.parse(fs.readFileSync(CONFIG_FILE, "utf8"));
      cfg = { ...cfg, ...raw };
    }
  } catch {}
  for (const key of Object.keys(cfg)) {
    cfg[key] = envOverride(key, cfg[key]);
  }
  return cfg;
}

export function setConfig(key, value) {
  const cfg = getConfig();
  cfg[key] = value;
  fs.mkdirSync(CONFIG_DIR, { recursive: true });
  fs.writeFileSync(CONFIG_FILE, JSON.stringify(cfg, null, 2));
  return cfg;
}

export function configShow() {
  const c = getConfig();
  console.log(`配置目录:    ${CONFIG_DIR}`);
  console.log(`代理地址:    ${c.proxy_host}:${c.proxy_port}`);
  console.log(`服务端:      ${c.server_url || "(未配置)"}`);
  console.log(`Agent ID:    ${c.agent_id || "(未注册)"}`);
  console.log(`认证Token:   ${c.auth_token ? "***" : "(未配置)"}`);
  console.log(`心跳间隔:    ${c.heartbeat_interval}s`);
  console.log(`拉取间隔:    ${c.pull_interval}s`);
}

export function configSet(key, value) {
  if (!value) {
    const c = getConfig();
    const envKey = `EMCAD_${key.toUpperCase()}`;
    console.log(`${key} = ${c[key] || process.env[envKey] || "(未设置)"}`);
    return;
  }
  setConfig(key, value);
  console.log(chalk.green(`已设置 ${key}=${value}`));
}
