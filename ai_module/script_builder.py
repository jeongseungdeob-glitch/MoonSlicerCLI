from utils.helpers import extract_lua_code


def build_lua_script_from_text(text: str) -> str:
	code = extract_lua_code(text)
	if not code.strip():
		code = "print('No code generated')"
	return code