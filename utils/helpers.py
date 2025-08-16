import re

_CODE_BLOCK_RE = re.compile(r"```(?:lua)?\s*([\s\S]*?)```", re.IGNORECASE)


def extract_lua_code(text: str) -> str:
    match = _CODE_BLOCK_RE.search(text or "")
    if match:
        return match.group(1).strip()
    return (text or "").strip()