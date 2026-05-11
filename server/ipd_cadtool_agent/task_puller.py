from __future__ import annotations

import threading
import time
import logging

import requests

from ipd_cadtool_agent.config import get_config
from ipd_cadtool_agent.models import TaskPullResponse
from ipd_cadtool_agent.executor import executor

logger = logging.getLogger(__name__)


class TaskPuller:
    """定时从服务端拉取任务并执行"""

    def __init__(self) -> None:
        self._config = get_config()
        self._running = False
        self._thread: threading.Thread | None = None
        self._callback = None

    def set_status_callback(self, callback) -> None:
        self._callback = callback

    def start(self) -> None:
        if self._running:
            return
        if not self._config.server_url:
            return
        self._running = True
        self._thread = threading.Thread(target=self._pull_loop, daemon=True)
        self._thread.start()
        logger.info("任务拉取已启动")

    def stop(self) -> None:
        self._running = False
        logger.info("任务拉取已停止")

    def _pull_loop(self) -> None:
        token = self._config.auth_token
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        while self._running:
            try:
                url = f"{self._config.server_url.rstrip('/')}/tasks/{self._config.agent_id}"
                resp = requests.get(url, headers=headers, timeout=10)
                resp.raise_for_status()
                data = TaskPullResponse(**resp.json())

                if data.tasks:
                    if self._callback:
                        self._callback("busy")
                    for task in data.tasks:
                        logger.info("执行拉取任务: %s", task.task_id)
                        result = executor.execute(task, self._config.agent_id)

                        report_url = f"{self._config.server_url.rstrip('/')}/results"
                        requests.post(report_url, json=result.model_dump(), headers=headers, timeout=10)
                    if self._callback:
                        self._callback("idle")
            except Exception as exc:
                logger.warning("拉取任务失败: %s", exc)
            time.sleep(self._config.pull_interval)


puller = TaskPuller()
