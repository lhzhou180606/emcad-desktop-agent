from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel


class TaskRequest(BaseModel):
    task_id: str
    script: str
    script_type: str = "path"  # "path" | "content"
    args: List[str] = []
    env: dict = {}
    timeout: int = 60
    work_dir: str = ""


class TaskResult(BaseModel):
    task_id: str
    agent_id: str = ""
    exit_code: int = -1
    stdout: str = ""
    stderr: str = ""
    duration: float = 0.0
    error: str = ""


class AgentInfo(BaseModel):
    hostname: str
    ip: str
    port: int


class RegisterRequest(BaseModel):
    agent: AgentInfo


class RegisterResponse(BaseModel):
    agent_id: str
    heartbeat_interval: int


class HeartbeatRequest(BaseModel):
    agent_id: str
    status: str


class TaskPullResponse(BaseModel):
    tasks: List[TaskRequest]
