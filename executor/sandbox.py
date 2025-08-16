from lupa import LuaRuntime

from utils.config import Config
from executor.logger import get_logger

logger = get_logger("sandbox")


class Sandbox:
    """Isolated Lua runtime for secure script execution."""

    def __init__(self):
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self._setup_environment()

    def _setup_environment(self):
        """Strip dangerous globals and prepare limited stdlib."""
        # Potentially unsafe globals/APIs to remove
        unsafe = [
            "os",
            "io",
            "require",
            "load",
            "dofile",
            "package",
            "collectgarbage",
        ]
        for name in unsafe:
            try:
                self.lua.execute(f"{name} = nil")
            except Exception:
                # Some globals may not exist; ignore
                pass

    def execute(self, code: str):
        """Execute Lua code in sandbox and return the result."""
        try:
            func = self.lua.eval(f"function() {code} end")
            result = func()
            return result
        except Exception as exc:
            logger.error("Sandbox execution error: %s", exc)
            raise