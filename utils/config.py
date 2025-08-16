import os
from dataclasses import dataclass

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOGS_DIR = os.path.join(ROOT_DIR, "logs")
SANDBOXED_SCRIPTS_DIR = os.path.join(ROOT_DIR, "sandboxed_scripts")


def ensure_directories():
    os.makedirs(LOGS_DIR, exist_ok=True)
    os.makedirs(SANDBOXED_SCRIPTS_DIR, exist_ok=True)


@dataclass
class AIConfig:
    chat_api_url: str = os.environ.get("MOON_CHAT_API", "http://localhost:8000/api/chat")
    fast_mode: bool = True


@dataclass
class SandboxConfig:
    instruction_limit: int = 200000
    time_limit_seconds: float = 3.0


@dataclass
class ValidationConfig:
    max_lines: int = 2000