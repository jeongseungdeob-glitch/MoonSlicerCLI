import logging
import os
from datetime import datetime
from utils.config import LOGS_DIR, ensure_directories


def get_logger(name: str = "executor") -> logging.Logger:
	ensure_directories()
	logger = logging.getLogger(name)
	if logger.handlers:
		return logger
	logger.setLevel(logging.INFO)
	log_path = os.path.join(LOGS_DIR, f"{name}.log")
	fh = logging.FileHandler(log_path, encoding="utf-8")
	sh = logging.StreamHandler()
	fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
	fh.setFormatter(fmt)
	sh.setFormatter(fmt)
	logger.addHandler(fh)
	logger.addHandler(sh)
	logger.info("Logger initialized at %s", datetime.now().isoformat())
	return logger