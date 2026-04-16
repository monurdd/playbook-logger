from ansible.plugins.callback import CallbackBase
from datetime import datetime
import json
import uuid
import os

class CallbackModule(CallbackBase):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = "notification"
    CALLBACK_NAME = "playbook_logger"

    def __init__(self):
        super().__init__()
        self.session_id = str(uuid.uuid4())
        self.task_start_times = {} 
        self.log_file = f"./logs/{self.session_id}.jsonl"

    def _write_log(self, payload):
        os.makedirs("./logs", exist_ok=True)
        try:
            with open(self.log_file, "a") as f:
                f.write(json.dumps(payload) + "\n")
        except Exception as e:
            self._display.display(f"LOG WRITE ERROR: {str(e)}")

    def v2_playbook_on_task_start(self, task, is_conditional):
        self.current_task_name = task.get_name().strip()
        self.task_start_times[self.current_task_name] = datetime.utcnow()

    def _get_duration_ms(self, task_name):
        start_time = self.task_start_times.get(task_name)
        if not start_time:
            return None

        duration = datetime.utcnow() - start_time
        return int(duration.total_seconds() * 1000)

    def _get_module_name(self, result):
        task = getattr(result, "_task", None)
        if not task:
            return None
        return getattr(task, "action", None)

    def v2_runner_on_ok(self, result):
        try:
            data = result._result
            task = getattr(result, "_task", None)
            task_name = None
            if task:
                try:
                    task_name = task.get_name().strip()
                except Exception:
                    task_name = getattr(result, "task_name", "unknown")
            else:
                task_name = getattr(result, "task_name", "unknown")

            payload = {
                "@timestamp": datetime.utcnow().isoformat(),
                "session_id": self.session_id,
                "task": task_name,
                "host": result._host.get_name(),
                "status": "ok",
                "changed": data.get("changed", False),
                "duration_ms": self._get_duration_ms(task_name),
                "msg": data.get("msg"),
                "module": self._get_module_name(result),
                "item_count": len(data.get("results") or []),
            }
            self._write_log(payload)

        except Exception as e:
            self._display.display(f"CALLBACK ERROR: {str(e)}")

    def v2_runner_on_failed(self, result, ignore_errors=False):
        data = result._result
        task = getattr(result, "_task", None)
        if task:
            try:
                task_name = task.get_name().strip()
            except Exception:
                task_name = getattr(result, "task_name", "unknown")
        else:
            task_name = getattr(result, "task_name", "unknown")

        payload = {
            "@timestamp": datetime.utcnow().isoformat(),
            "session_id": self.session_id,
            "task": task_name,
            "host": result._host.get_name(),
            "status": "failed",
            "changed": data.get("changed", False),
            "duration_ms": self._get_duration_ms(task_name),
            "msg": data.get("msg"),
            "module": self._get_module_name(result),
            "item_count": len(data.get("results", [])),
        }

        self._write_log(payload)