from typing import Any, Dict
from lupa import LuaRuntime


def create_sandbox() -> LuaRuntime:
	# Disallow attribute access and sandbox libraries
	rt = LuaRuntime(unpack_returned_tuples=True, register_eval=False)
	# Remove dangerous globals
	for name in [
		"os", "io", "debug", "package", "require", "load", "loadstring", "dofile", "loadfile",
		"setfenv", "getfenv", "collectgarbage", "coroutine"
	]:
		try:
			rt.globals()[name] = None
		except Exception:
			pass
	return rt


def run_script(lua: LuaRuntime, code: str, timeout_seconds: int = 5) -> Dict[str, Any]:
	try:
		fn = lua.eval(f"function()\n{code}\nend")
		result = fn()
		return {"ok": True, "result": result}
	except Exception as e:
		return {"ok": False, "error": str(e)}