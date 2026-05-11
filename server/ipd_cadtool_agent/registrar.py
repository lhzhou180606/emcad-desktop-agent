from __future__ import annotations

import threading
import time
import logging

import requests

from ipd_cadtool_agent.config import get_config
from ipd_cadtool_agent.models import AgentInfo, HeartbeatRequest, RegisterRequest, RegisterResponse

logger = logging.getLogger(__name__)


class Registrar:
    """向服务端注册代理并维护心跳"""

    def __init__(self) -> None:
        self._config = get_config()
        self._token = self._config.auth_token
        self._running = False
        self._thread: threading.Thread | None = None
        self._status = "idle"

    @property
    def status(self) -> str:
        return self._status

    def register(self, server_url: str = "") -> RegisterResponse:
        if server_url:
            self._config.set("server_url", server_url)

        url = f"{self._config.server_url.rstrip('/')}/register"
        agent = AgentInfo(
            hostname=self._config.get_hostname(),
            ip=self._config.get_local_ip(),
            port=self._config.proxy_port,
        )
        req = RegisterRequest(agent=agent)

        headers = {"Content-Type": "application/json"}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"

        resp = requests.post(url, json=req.model_dump(), headers=headers, timeout=10)
        resp.raise_for_status()
        data = RegisterResponse(**resp.json())

        self._config.set("agent_id", data.agent_id)
        self._config.set("heartbeat_interval", str(data.heartbeat_interval))
        logger.info("注册成功: agent_id=%s", data.agent_id)
        return data

    def set_status(self, status: str) -> None:
        self._status = status

    def start_heartbeat(self) -> None:
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self._thread.start()

    def stop_heartbeat(self) -> None:
        self._running = False

    def _heartbeat_loop(self) -> None:
        while self._running:
            try:
                url = f"{self._config.server_url.rstrip('/')}/heartbeat"
                req = HeartbeatRequest(
                    agent_id=self._config.agent_id,
                    status=self._status,
                )
                headers = {"Content-Type": "application/json"}
                if self._token:
                    headers["Authorization"] = f"Bearer {self._token}"
                requests.post(url, json=req.model_dump(), headers=headers, timeout=10)
            except Exception:
                pass
            time.sleep(self._config.heartbeat_interval)


registrar = Registrar()
