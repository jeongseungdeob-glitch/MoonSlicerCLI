import re


CODE_BLOCK_RE = re.compile(r"```lua(.*?)```", re.DOTALL | re.IGNORECASE)


def _extract_code(ai_response: str) -> str:
    """Extract Lua code block from AI markdown response."""
    match = CODE_BLOCK_RE.search(ai_response)
    if match:
        return match.group(1).strip()
    return ai_response.strip()


def sanitize_lua(code: str) -> str:
    """Basic sanitation: remove carriage returns and non-printable chars."""
    clean = code.replace("\r", "")
    return "".join(ch for ch in clean if 32 <= ord(ch) <= 126 or ch == "\n")


def build_script(ai_response: str) -> str:
    """Public helper to build sanitized Lua script from AI output."""
    raw = _extract_code(ai_response)
    return sanitize_lua(raw)