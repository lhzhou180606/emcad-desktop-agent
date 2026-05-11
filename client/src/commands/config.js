import fs from "node:fs";
import path from "node:path";
import os from "node:os";
import chalk from "chalk";

const CONFIG_DIR = path.join(os.homedir(), ".ipd-cadtool-cli");
const CONFIG_FILE = path.join(CONFIG_DIR, "config.json");

function envOverride(key, value) {
  const envKey = `CADTOOL_${key.toUpperCase()}`;
  const envVal = process.env[envKey];
  return envVal !== undefined ? envVal : value;
}

export function getConfig() {
  let cfg = {};
  try {
    if (fs.existsSync(CONFIG_FILE)) {
      cfg = JSON.parse(fs.readFileSync(CONFIG_FILE, "utf8"));
    }
  } catch {}
  // 默认值
  if (!cfg.proxy_host) cfg.proxy_host = "0.0.0.0";
  if (!cfg.proxy_port) cfg.proxy_port = "9527";
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
}

export function configSet(key, value) {
  if (!value && value !== "") {
    const c = getConfig();
    console.log(`${key} = ${c[key] || "(未设置)"}`);
    return;
  }
  setConfig(key, value);
  console.log(chalk.green(`已设置 ${key}=${value}`));
}
