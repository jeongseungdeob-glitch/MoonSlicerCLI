import argparse
import json
import os
from executor.core import ExecutorCore
from utils.file_manager import read_script
from utils.config import get_config


def cli():
	parser = argparse.ArgumentParser(description="Internal Lua Sandbox Executor")
	parser.add_argument("--generate", type=str, help="Goal for AI to generate a Lua script")
	parser.add_argument("--execute", type=str, help="Path to Lua script to execute")
	args = parser.parse_args()

	core = ExecutorCore()

	if args.generate:
		info = core.generate_and_save(args.generate)
		print(json.dumps(info, indent=2))

	if args.execute:
		code = read_script(args.execute) if os.path.exists(args.execute) else args.execute
		res = core.execute(code)
		print(json.dumps(res, indent=2))


if __name__ == "__main__":
	cli()