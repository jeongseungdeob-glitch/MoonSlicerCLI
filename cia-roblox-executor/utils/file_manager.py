import os
from typing import Optional, List
from .config import get_config, ensure_directories


def get_project_paths() -> dict:
	cfg = get_config()
	return {
		"logs": cfg["log_dir"],
		"scripts": cfg["scripts_dir"],
	}


def save_script(filename: str, content: str) -> str:
	ensure_directories()
	paths = get_project_paths()
	if not filename.endswith(".lua"):
		filename = filename + ".lua"
	path = os.path.join(paths["scripts"], filename)
	with open(path, "w", encoding="utf-8") as f:
		f.write(content)
	return path


def read_script(path: str) -> str:
	with open(path, "r", encoding="utf-8") as f:
		return f.read()


def list_scripts() -> List[str]:
	paths = get_project_paths()
	if not os.path.isdir(paths["scripts"]):
		return []
	return [os.path.join(paths["scripts"], f) for f in os.listdir(paths["scripts"]) if f.endswith(".lua")]


def validate_filename_safe(filename: str) -> bool:
	return not any(x in filename for x in ["..", "/", "\\"])