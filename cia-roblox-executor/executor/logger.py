import os
import logging
from logging.handlers import RotatingFileHandler
from typing import Optional
from ..utils.config import get_config, ensure_directories


def get_logger(name: Optional[str] = None) -> logging.Logger:
	ensure_directories()
	cfg = get_config()
	log_dir = cfg["log_dir"]
	os.makedirs(log_dir, exist_ok=True)
	logger = logging.getLogger(name or "cia_executor")
	if logger.handlers:
		return logger
	logger.setLevel(logging.INFO)

	log_path = os.path.join(log_dir, "executor.log")
	file_handler = RotatingFileHandler(log_path, maxBytes=1_000_000, backupCount=3)
	file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
	logger.addHandler(file_handler)

	console_handler = logging.StreamHandler()
	console_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
	logger.addHandler(console_handler)
	return logger