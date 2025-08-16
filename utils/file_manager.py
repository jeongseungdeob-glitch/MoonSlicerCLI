import os
from pathlib import Path


def ensure_dir_exists(path: str):
    """Create directory path if it does not already exist."""
    Path(path).mkdir(parents=True, exist_ok=True)


def save_script(code: str, filename: str, base_dir: str):
    """Save Lua code to filename inside base_dir. Returns full file path."""
    ensure_dir_exists(base_dir)
    full_path = os.path.join(base_dir, filename)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(code)
    return full_path


def load_script(path: str) -> str:
    """Load and return script contents from path."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()