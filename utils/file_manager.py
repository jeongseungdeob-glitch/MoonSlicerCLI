import os
import time
from typing import List
from .config import SANDBOXED_SCRIPTS_DIR, ensure_directories


def _timestamp_str() -> str:
    return time.strftime("%Y%m%d-%H%M%S")


def make_script_path(name: str | None = None) -> str:
    ensure_directories()
    if not name:
        name = f"script_{_timestamp_str()}.lua"
    elif not name.endswith(".lua"):
        name = name + ".lua"
    return os.path.join(SANDBOXED_SCRIPTS_DIR, name)


essential_encoding = "utf-8"


def save_script(content: str, name: str | None = None) -> str:
    path = make_script_path(name)
    with open(path, "w", encoding=essential_encoding) as f:
        f.write(content)
    return path


def read_script(path: str) -> str:
    with open(path, "r", encoding=essential_encoding) as f:
        return f.read()


def list_scripts() -> List[str]:
    ensure_directories()
    files = [os.path.join(SANDBOXED_SCRIPTS_DIR, f) for f in os.listdir(SANDBOXED_SCRIPTS_DIR) if f.endswith(".lua")]
    files.sort()
    return files