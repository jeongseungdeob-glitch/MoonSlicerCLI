from typing import Any, Dict
import multiprocessing as mp
import json
from utils.config import SandboxConfig
from .logger import get_logger
from .sandbox_worker import run_lua_code


class LuaSandbox:
	def __init__(self, config: SandboxConfig | None = None):
		self.config = config or SandboxConfig()
		self.logger = get_logger("sandbox")

	def _target(self, code: str, q: mp.Queue) -> None:
		res = run_lua_code(code)
		try:
			q.put(res)
		except Exception:
			pass

	def run(self, code: str) -> Dict[str, Any]:
		q: mp.Queue = mp.Queue()
		proc = mp.Process(target=self._target, args=(code, q))
		proc.start()
		proc.join(timeout=float(self.config.time_limit_seconds))
		if proc.is_alive():
			self.logger.error("Lua execution timed out; terminating process")
			proc.terminate()
			proc.join(1)
			return {"ok": False, "error": "Time limit exceeded"}
		try:
			res = q.get_nowait()
			# Log worker logs if any
			for line in res.get("logs", []) or []:
				self.logger.info(line)
			# Remove logs from response for cleanliness
			res.pop("logs", None)
			return res
		except Exception as e:
			self.logger.error("Lua worker failed: %s", e)
			return {"ok": False, "error": str(e)}