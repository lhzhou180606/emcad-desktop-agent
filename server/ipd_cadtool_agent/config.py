from __future__ import annotations

import json
import os
import socket
from pathlib import Path
from typing import Optional


class Config:
    """全局配置管理，支持配置文件 + 环境变量覆盖"""

    def __init__(self) -> None:
        self._config_dir = Path.home() / ".ipd-cadtool-cli"
        self._config_file = self._config_dir / "config.json"
        self._data: dict = {}
        self._load()

    @property
    def config_dir(self) -> Path:
        return self._config_dir

    @property
    def proxy_host(self) -> str:
        return self._get("proxy_host", "0.0.0.0")

    @property
    def proxy_port(self) -> int:
        return int(self._get("proxy_port", "9527"))

    @property
    def server_url(self) -> str:
        return self._get("server_url", "")

    @property
    def auth_token(self) -> str:
        return self._get("auth_token", "")

    @property
    def agent_id(self) -> str:
        return self._get("agent_id", "")

    @property
    def heartbeat_interval(self) -> int:
        return int(self._get("heartbeat_interval", "30"))

    @property
    def pull_interval(self) -> int:
        return int(self._get("pull_interval", "10"))

    def set(self, key: str, value: str) -> None:
        self._data[key] = value
        self._save()

    def get_hostname(self) -> str:
        return socket.gethostname()

    def get_local_ip(self) -> str:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    def _get(self, key: str, default: str) -> str:
        env_key = f"CADTOOL_{key.upper()}"
        env_val = os.environ.get(env_key)
        if env_val is not None:
            return env_val
        return self._data.get(key, default)

    def _load(self) -> None:
        if self._config_file.exists():
            try:
                self._data = json.loads(self._config_file.read_text())
            except Exception:
                self._data = {}

    def _save(self) -> None:
        self._config_dir.mkdir(parents=True, exist_ok=True)
        self._config_file.write_text(json.dumps(self._data, indent=2))


_config: Optional[Config] = None


def get_config() -> Config:
    global _config
    if _config is None:
        _config = Config()
    return _config
