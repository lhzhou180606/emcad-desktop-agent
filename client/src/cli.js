#!/usr/bin/env node
import { program } from "commander";
import chalk from "chalk";
import { proxyStart, proxyStop, proxyStatus, proxyRegister } from "./commands/proxy.js";
import { scriptRun, scriptList } from "./commands/script.js";
import { configShow, configSet, getConfig } from "./commands/config.js";

program
  .name("ipd-emcad-cli")
  .description("IPD Emcad CLI")
  .version("0.1.0");

// ── proxy ────────────────────────────────────────────

const proxyCmd = program.command("proxy").description("管理本地代理");

proxyCmd
  .command("start")
  .description("启动本地代理服务")
  .option("--host <host>", "监听地址")
  .option("--port <port>", "监听端口")
  .option("--server <url>", "远程服务端地址")
  .action(async (opts) => {
    await proxyStart(opts);
  });

proxyCmd
  .command("stop")
  .description("停止本地代理")
  .action(() => proxyStop());

proxyCmd
  .command("status")
  .description("查看代理状态")
  .action(async () => {
    const s = await proxyStatus();
    if (!s) {
      console.log(chalk.yellow("代理未运行"));
      return;
    }
    console.log(`代理 ID:     ${s.agent_id || "(未注册)"}`);
    console.log(`状态:        ${s.status}`);
    console.log(`服务端:      ${s.server_url || "(未配置)"}`);
    console.log(`任务拉取:    ${s.pull_enabled ? "开启" : "关闭"}`);
    console.log(`监听地址:    http://${s.proxy_host}:${s.proxy_port}`);
  });

proxyCmd
  .command("register <serverUrl>")
  .description("向远程服务端注册代理")
  .option("--token <token>", "认证 Token")
  .action(async (serverUrl, opts) => {
    await proxyRegister(serverUrl, opts.token);
  });

// ── script ───────────────────────────────────────────

const scriptCmd = program.command("script").description("管理脚本执行");

scriptCmd
  .command("run <script>")
  .description("执行 Python 脚本")
  .option("--arg <args...>", "脚本参数")
  .option("--env <vars...>", "环境变量 (KEY=VAL ...)")
  .option("--timeout <seconds>", "超时秒数", "60")
  .option("--content", "将参数作为脚本内容而非路径")
  .action(async (script, opts) => {
    const result = await scriptRun(script, opts);
    if (!result) return;
    console.log(`任务ID:  ${result.task_id}`);
    console.log(`退出码:  ${result.exit_code}`);
    console.log(`耗时:    ${result.duration}s`);
    if (result.stdout) {
      console.log("── stdout ──");
      process.stdout.write(result.stdout);
    }
    if (result.stderr) {
      console.log("── stderr ──");
      process.stderr.write(result.stderr);
    }
    if (result.error) {
      console.error(chalk.red(`错误: ${result.error}`));
    }
  });

scriptCmd
  .command("list")
  .description("列出临时脚本")
  .action(scriptList);

// ── config ───────────────────────────────────────────

const configCmd = program.command("config").description("管理配置");

configCmd
  .command("show")
  .description("显示当前配置")
  .action(() => {
    configShow();
  });

configCmd
  .command("set <key> [value]")
  .description("设置配置项")
  .action((key, value) => {
    configSet(key, value);
  });

program.parse();
