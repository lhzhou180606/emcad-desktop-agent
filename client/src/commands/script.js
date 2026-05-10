import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import chalk from "chalk";
import { executeScript } from "../api.js";

export async function scriptRun(scriptPathOrContent, opts = {}) {
  const env = {};
  if (opts.env) {
    for (const kv of opts.env) {
      const [k, ...v] = kv.split("=");
      if (k) env[k] = v.join("=") || "";
    }
  }

  const options = {
    content: opts.content || false,
    args: opts.arg || [],
    env,
    timeout: parseInt(opts.timeout || "60", 10),
    work_dir: process.cwd(),
  };

  try {
    return await executeScript(scriptPathOrContent, options);
  } catch (err) {
    if (err.code === "ECONNREFUSED") {
      console.error(chalk.red("错误: 代理未运行，请先启动本地代理"));
    } else if (err.response) {
      console.error(chalk.red(`错误 (${err.response.status}): ${JSON.stringify(err.response.data)}`));
    } else {
      console.error(chalk.red(`错误: ${err.message}`));
    }
    return null;
  }
}

export function scriptList() {
  const tmpDir = os.tmpdir();
  try {
    const files = fs.readdirSync(tmpDir).filter(f => f.startsWith("ipd_emcad_script_") && f.endsWith(".py"));
    if (files.length) {
      console.log("临时脚本文件:");
      files.forEach(f => console.log(`  ${path.join(tmpDir, f)}`));
    } else {
      console.log("无");
    }
  } catch {
    console.log("无");
  }
}
