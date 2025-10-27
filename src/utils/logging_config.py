"""Logging helper utilities for pipeline-wide configuration."""

from __future__ import annotations

import logging
import logging.config
import os
from pathlib import Path
from typing import Any, Dict

from .config import load_config


DEFAULT_LOGGER_NAME = "ier"


def setup_logging(config: Dict[str, Any] | None = None) -> logging.Logger:
    """Configure logging according to the pipeline configuration.

    Parameters
    ----------
    config:
        Pre-loaded configuration dictionary. When omitted, the global pipeline
        configuration (with logging overrides) is loaded automatically.

    Returns
    -------
    logging.Logger
        Configured root logger for the pipeline.
    """

    if config is None:
        config = load_config()

    logging_cfg = config.get("logging", {})
    log_level = logging_cfg.get("level", "INFO")
    log_file = logging_cfg.get("file", "logs/pipeline.log")
    log_format = logging_cfg.get("format", "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s")
    date_format = logging_cfg.get("date_format", "%Y-%m-%d %H:%M:%S")
    max_bytes = int(logging_cfg.get("max_bytes", 10 * 1024 * 1024))
    backup_count = int(logging_cfg.get("backup_count", 3))
    console_enabled = bool(logging_cfg.get("console", True))

    log_path = Path(log_file)
    if log_path.parent and not log_path.parent.exists():
        os.makedirs(log_path.parent, exist_ok=True)

    handlers: Dict[str, Dict[str, Any]] = {
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": log_level,
            "formatter": "standard",
            "filename": str(log_path),
            "maxBytes": max_bytes,
            "backupCount": backup_count,
            "encoding": "utf-8",
        }
    }

    if console_enabled:
        handlers["console"] = {
            "class": "logging.StreamHandler",
            "level": log_level,
            "formatter": "standard",
        }

    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": log_format,
                "datefmt": date_format,
            }
        },
        "handlers": handlers,
        "root": {
            "level": log_level,
            "handlers": list(handlers.keys()),
        },
    }

    logging.config.dictConfig(logging_config)
    return logging.getLogger(DEFAULT_LOGGER_NAME)


__all__ = ["setup_logging", "DEFAULT_LOGGER_NAME"]
