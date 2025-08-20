import re
from typing import Tuple


def extract_lua_code(ai_output: str) -> str:
	code_blocks = re.findall(r"```lua\n([\s\S]*?)```", ai_output, flags=re.IGNORECASE)
	if code_blocks:
		return code_blocks[0].strip()
	fenced = re.findall(r"```\n([\s\S]*?)```", ai_output)
	if fenced:
		return fenced[0].strip()
	return ai_output.strip()


def build_script(ai_output: str) -> Tuple[str, str]:
	code = extract_lua_code(ai_output)
	if not code:
		code = "-- empty script generated\n"
	return ("generated_script", code)