from __future__ import annotations

import logging

from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel

from ipd_emcad_agent.config import get_config
from ipd_emcad_agent.models import TaskRequest
from ipd_emcad_agent.executor import executor
from ipd_emcad_agent.registrar import registrar
from ipd_emcad_agent.task_puller import puller

logger = logging.getLogger(__name__)

app = FastAPI(title="IPD Emcad Agent", version="0.1.0")
_config = get_config()


class ExecuteResponse(BaseModel):
    task_id: str
    exit_code: int
    stdout: str
    stderr: str
    duration: float
    error: str


class StatusResponse(BaseModel):
    agent_id: str
    status: str
    server_url: str
    pull_enabled: bool
    proxy_host: str
    proxy_port: int


class RegisterDirectRequest(BaseModel):
    server_url: str = ""
    auth_token: str = ""
    pull_interval: int = 0


class ConfigUpdateRequest(BaseModel):
    server_url: str = ""
    auth_token: str = ""
    pull_interval: int = 0


def _verify_token(authorization: str = Header("")) -> None:
    token = _config.auth_token
    if not token:
        return
    parts = authorization.split()
    if len(parts) != 2 or parts[1] != token:
        raise HTTPException(status_code=403, detail="认证失败")


@app.get("/health")
def health():
    return {"status": "ok", "agent_id": _config.agent_id}


@app.get("/status", response_model=StatusResponse)
def status():
    return StatusResponse(
        agent_id=_config.agent_id,
        status=registrar.status,
        server_url=_config.server_url,
        pull_enabled=puller._running,
        proxy_host=_config.proxy_host,
        proxy_port=_config.proxy_port,
    )


@app.post("/execute", response_model=ExecuteResponse)
def execute(task: TaskRequest, authorization: str = Header("")):
    _verify_token(authorization)
    result = executor.execute(task, _config.agent_id)
    return ExecuteResponse(
        task_id=result.task_id,
        exit_code=result.exit_code,
        stdout=result.stdout,
        stderr=result.stderr,
        duration=result.duration,
        error=result.error,
    )


@app.post("/register_direct")
def register_direct(req: RegisterDirectRequest):
    """CLI 直接调用的注册入口"""
    if not req.server_url:
        return {"error": "缺少 server_url"}

    _config.set("server_url", req.server_url)
    if req.auth_token:
        _config.set("auth_token", req.auth_token)
    if req.pull_interval:
        _config.set("pull_interval", str(req.pull_interval))

    try:
        resp = registrar.register(req.server_url)
        registrar.start_heartbeat()
        puller.set_status_callback(registrar.set_status)
        puller.start()
        return {"message": "ok", "agent_id": resp.agent_id}
    except Exception as exc:
        return {"error": str(exc)}


@app.post("/config")
def update_config(req: ConfigUpdateRequest):
    if req.server_url:
        _config.set("server_url", req.server_url)
    if req.auth_token:
        _config.set("auth_token", req.auth_token)
    if req.pull_interval:
        _config.set("pull_interval", str(req.pull_interval))
    return {"message": "ok"}
