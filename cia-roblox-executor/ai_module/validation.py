from typing import Tuple, List
from ..utils.config import get_config


def validate_script(content: str) -> Tuple[bool, List[str]]:
	cfg = get_config()
	errors: List[str] = []
	if len(content.encode()) > cfg["max_script_bytes"]:
		errors.append("Script exceeds maximum allowed size")
	for token in cfg["banned_tokens"]:
		if token in content:
			errors.append(f"Banned token detected: {token}")
	for pattern in cfg["infinite_loop_patterns"]:
		if pattern in content:
			errors.append(f"Potential infinite loop pattern: {pattern}")
	return (len(errors) == 0, errors)