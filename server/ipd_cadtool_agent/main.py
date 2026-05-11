#!/usr/bin/env python3
"""ipd-cadtool-agent 入口 - 启动本地代理服务"""

from __future__ import annotations

import argparse
import logging
import sys

import uvicorn

from ipd_cadtool_agent.config import get_config
from ipd_cadtool_agent.registrar import registrar
from ipd_cadtool_agent.task_puller import puller


def main():
    parser = argparse.ArgumentParser(description="IPD Cadtool Agent 本地代理服务")
    parser.add_argument("--host", default="", help="监听地址 (默认 0.0.0.0)")
    parser.add_argument("--port", type=int, default=0, help="监听端口 (默认 9527)")
    parser.add_argument("--server", default="", help="远程服务端地址")
    parser.add_argument("--token", default="", help="认证 Token")
    parser.add_argument("--no-pull", action="store_true", help="禁用任务拉取")
    parser.add_argument("--no-heartbeat", action="store_true", help="禁用心跳")

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    config = get_config()
    host = args.host or config.proxy_host
    port = args.port or config.proxy_port

    if args.port:
        config.set("proxy_port", str(args.port))
    if args.host:
        config.set("proxy_host", args.host)
    if args.server:
        config.set("server_url", args.server)
    if args.token:
        config.set("auth_token", args.token)

    # 注册 + 心跳 + 拉取
    if config.server_url:
        try:
            resp = registrar.register()
            logging.info("代理已注册: %s", resp.agent_id)
        except Exception as exc:
            logging.warning("注册失败: %s", exc)

        if not args.no_heartbeat:
            registrar.start_heartbeat()
            logging.info("心跳已启动")

        if not args.no_pull:
            puller.set_status_callback(registrar.set_status)
            puller.start()
            logging.info("任务拉取已启动")

    from ipd_cadtool_agent.server import app
    logging.info("代理服务启动: %s:%s", host, port)
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    main()
