import os
from datetime import datetime
from utils.config import Config
from utils.file_manager import load_script, save_script, ensure_dir_exists
from executor.sandbox import Sandbox
from executor.logger import get_logger
from executor.anti_cheat_bypass import apply_bypass


class Executor:
    """High-level interface for executing Lua scripts in a secure sandbox."""

    def __init__(self):
        self.cfg = Config.load()
        self.logger = get_logger("executor.core")
        self.sandbox = Sandbox()

    def _audit_log(self, script_path: str, success: bool, error: str | None = None):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "script": script_path,
            "success": success,
            "error": error,
        }
        self.logger.info("AUDIT %s", log_entry)

    def run_script(self, script_path: str):
        """Load script from path, apply bypass, and execute inside sandbox."""
        code = load_script(script_path)

        # In future, mutate lua runtime via bypass
        apply_bypass(self.sandbox.lua)

        try:
            result = self.sandbox.execute(code)
            self._audit_log(script_path, True)
            return result
        except Exception as exc:
            self._audit_log(script_path, False, str(exc))
            raise

    def run_code(self, code: str, filename: str | None = None):
        """Save Lua `code`, then execute it. filename optional."""
        if not filename:
            filename = f"generated_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.lua"
        script_path = save_script(code, filename, self.cfg["script_dir"])
        return self.run_script(script_path)