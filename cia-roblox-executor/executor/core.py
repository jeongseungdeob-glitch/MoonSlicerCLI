from typing import Dict, Any
from .sandbox import create_sandbox, run_script
from .logger import get_logger
from ..ai_module.ai_interface import AIInterface
from ..ai_module.script_builder import build_script
from ..ai_module.validation import validate_script
from ..utils.file_manager import save_script
from ..utils.config import get_config


class ExecutorCore:
	def __init__(self):
		self.logger = get_logger("executor.core")
		self.lua = create_sandbox()
		self.cfg = get_config()
		self.ai = AIInterface()

	def generate_and_save(self, goal: str) -> Dict[str, Any]:
		self.logger.info(f"Generating script for goal: {goal}")
		ai_output = self.ai.generate_lua(goal)
		name, code = build_script(ai_output)
		ok, errors = validate_script(code)
		if not ok:
			self.logger.error(f"Validation failed: {errors}")
			raise ValueError("Generated script failed validation: " + "; ".join(errors))
		path = save_script(name, code)
		self.logger.info(f"Script saved: {path}")
		return {"path": path, "name": name, "code": code}

	def execute(self, code: str) -> Dict[str, Any]:
		self.logger.info("Executing script in sandbox")
		ok, errors = validate_script(code)
		if not ok:
			self.logger.error(f"Execution validation failed: {errors}")
			raise ValueError("Script failed validation before execution: " + "; ".join(errors))
		out = run_script(self.lua, code, timeout_seconds=self.cfg["lua_timeout_seconds"])
		self.logger.info("Execution finished")
		return out