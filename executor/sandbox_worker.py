from typing import Any, Dict, List
from lupa import LuaRuntime


def run_lua_code(code: str) -> Dict[str, Any]:
	logs: List[str] = []

	def safe_print(*args: Any) -> None:
		try:
			logs.append("[LUA] " + " ".join(str(a) for a in args))
		except Exception:
			pass

	lua = LuaRuntime(unpack_returned_tuples=True)
	g = lua.globals()
	# Lock down unsafe libraries
	g.os = None
	g.io = None
	g.package = None
	g.dofile = None
	g.loadfile = None
	g.require = None
	g.debug = None
	g.print = safe_print

	try:
		func = lua.execute(f"return function()\n{code}\nend")
		result = func()
		# Convert result to string to avoid cross-process serialization issues
		return {"ok": True, "result": str(result), "logs": logs}
	except Exception as e:
		return {"ok": False, "error": str(e), "logs": logs}