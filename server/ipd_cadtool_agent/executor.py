from __future__ import annotations

import subprocess
import tempfile
import time
from pathlib import Path

from ipd_emcad_agent.models import TaskRequest, TaskResult


class ScriptExecutor:
    """Python 脚本执行器，使用 subprocess 安全执行"""

    def execute(self, task: TaskRequest, agent_id: str = "") -> TaskResult:
        result = TaskResult(task_id=task.task_id, agent_id=agent_id)
        started = time.monotonic()

        try:
            if task.script_type == "content":
                script_path = self._write_temp_script(task.script)
            else:
                script_path = task.script

            env = {}
            if task.env:
                env.update(task.env)

            cwd = task.work_dir or None
            cmd = ["python3", script_path] + task.args

            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=task.timeout,
                cwd=cwd,
                env=env or None,
            )

            result.exit_code = proc.returncode
            result.stdout = proc.stdout
            result.stderr = proc.stderr

            if task.script_type == "content":
                Path(script_path).unlink(missing_ok=True)

        except subprocess.TimeoutExpired:
            result.exit_code = -1
            result.error = f"脚本执行超时 ({task.timeout}s)"
        except FileNotFoundError:
            result.exit_code = -1
            result.error = f"脚本文件不存在: {task.script}"
        except Exception as exc:
            result.exit_code = -1
            result.error = f"执行异常: {exc}"

        result.duration = round(time.monotonic() - started, 3)
        return result

    def _write_temp_script(self, content: str) -> str:
        fd, path = tempfile.mkstemp(suffix=".py", prefix="ipd_emcad_script_")
        with open(fd, "w") as f:
            f.write(content)
        return path


executor = ScriptExecutor()
