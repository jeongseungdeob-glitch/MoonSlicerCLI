import logging
import os
from pathlib import Path

from utils.config import Config
from utils.file_manager import ensure_dir_exists

_cfg = Config.load()
LOG_DIR = _cfg["log_dir"]
ensure_dir_exists(LOG_DIR)
LOG_PATH = os.path.join(LOG_DIR, "executor.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH),
        logging.StreamHandler(),
    ],
)


def get_logger(name: str = "executor") -> logging.Logger:
    """Return a configured logger instance."""
    return logging.getLogger(name)