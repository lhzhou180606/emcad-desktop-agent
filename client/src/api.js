import axios from "axios";
import crypto from "node:crypto";
import { getConfig } from "./commands/config.js";

function client() {
  const cfg = getConfig();
  const baseURL = `http://${cfg.proxy_host}:${cfg.proxy_port}`;
  const headers = { "Content-Type": "application/json" };
  if (cfg.auth_token) {
    headers["Authorization"] = `Bearer ${cfg.auth_token}`;
  }
  return axios.create({ baseURL, headers, timeout: 120000 });
}

// ── 代理 API ────────────────────────────────────────

export async function healthCheck() {
  const { data } = await client().get("/health");
  return data;
}

export async function getStatus() {
  const { data } = await client().get("/status");
  return data;
}

export async function executeScript(script, opts = {}) {
  const payload = {
    task_id: crypto.randomUUID(),
    script: opts.content ? script : script,
    script_type: opts.content ? "content" : "path",
    args: opts.args || [],
    timeout: opts.timeout || 60,
    work_dir: opts.work_dir || process.cwd(),
    env: opts.env || {},
  };
  const { data } = await client().post("/execute", payload);
  return data;
}

export async function registerDirect(serverUrl, token = "") {
  const { data } = await client().post("/register_direct", {
    server_url: serverUrl,
    auth_token: token,
  });
  return data;
}

export async function updateConfig(updates) {
  const { data } = await client().post("/config", updates);
  return data;
}
