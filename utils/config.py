from pathlib import Path
import os
import yaml


class Config:
    """Centralised configuration loader/writer."""

    DEFAULTS = {
        "script_dir": str(Path(__file__).resolve().parent.parent / "sandboxed_scripts"),
        "log_dir": str(Path(__file__).resolve().parent.parent / "logs"),
        "max_exec_time_sec": 5,
        "backend_base_url": "http://localhost:8000",
    }

    _cache = None

    @classmethod
    def load(cls, path: str | None = None):
        if cls._cache is not None:
            return cls._cache

        cfg = cls.DEFAULTS.copy()
        if path and os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                try:
                    file_cfg = yaml.safe_load(f) or {}
                    cfg.update(file_cfg)
                except yaml.YAMLError:
                    pass
        cls._cache = cfg
        return cfg