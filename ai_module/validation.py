import re
from utils.config import ValidationConfig

_PROHIBITED = [
	"os.", "io.", "require", "dofile", "loadfile", "package.", "debug.getinfo",
]

_LOOP_RE = re.compile(r"\bwhile\s+true\s*do\b", re.IGNORECASE)


def validate_lua(code: str, cfg: ValidationConfig | None = None) -> tuple[bool, list[str]]:
	errors: list[str] = []
	cfg = cfg or ValidationConfig()
	if code.count("\n") > cfg.max_lines:
		errors.append("Script too long")
	for token in _PROHIBITED:
		if token in code:
			errors.append(f"Prohibited token: {token}")
	if _LOOP_RE.search(code):
		errors.append("Infinite loop pattern detected: while true do")
	return (len(errors) == 0, errors)