from typing import Optional
from .sandbox import LuaSandbox
from .logger import get_logger
from utils.file_manager import read_script


class ExecutorCore:
	def __init__(self):
		self.logger = get_logger("executor_core")
		self.sandbox = LuaSandbox()

	def execute_script_file(self, path: str) -> dict:
		self.logger.info("Executing script: %s", path)
		code = read_script(path)
		result = self.sandbox.run(code)
		self.logger.info("Execution result: %s", result)
		return result

	def execute_code(self, code: str) -> dict:
		self.logger.info("Executing provided Lua code (%d chars)", len(code))
		result = self.sandbox.run(code)
		self.logger.info("Execution result: %s", result)
		return result