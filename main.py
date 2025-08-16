import argparse
import asyncio
import json
from ai_module.ai_interface import AIScriptAssistant
from ai_module.script_builder import build_lua_script_from_text
from ai_module.validation import validate_lua
from executor.core import ExecutorCore
from utils.file_manager import save_script, list_scripts


async def generate(prompt: str) -> str:
	assistant = AIScriptAssistant()
	text = await assistant.generate_script_text(prompt)
	code = build_lua_script_from_text(text)
	ok, errs = validate_lua(code)
	if not ok:
		raise SystemExit("Validation failed: " + "; ".join(errs))
	path = save_script(code)
	print("Saved:", path)
	return path


def execute(path: str | None, code: str | None):
	exec_core = ExecutorCore()
	if code is not None:
		res = exec_core.execute_code(code)
	else:
		if not path:
			raise SystemExit("Provide --file or --code")
		res = exec_core.execute_script_file(path)
	print(json.dumps(res, indent=2))


def main():
	parser = argparse.ArgumentParser(description="MoonSlicer Sandbox Executor CLI")
	sub = parser.add_subparsers(dest="cmd")

	g = sub.add_parser("generate")
	g.add_argument("prompt", nargs="+")

	e = sub.add_parser("execute")
	e.add_argument("--file", dest="file", default=None)
	e.add_argument("--code", dest="code", default=None)

	l = sub.add_parser("list")

	args = parser.parse_args()
	if args.cmd == "generate":
		prompt = " ".join(args.prompt)
		asyncio.run(generate(prompt))
	elif args.cmd == "execute":
		execute(args.file, args.code)
	elif args.cmd == "list":
		for p in list_scripts():
			print(p)
	else:
		parser.print_help()


if __name__ == "__main__":
	main()