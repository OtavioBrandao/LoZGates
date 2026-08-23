"""Configuracao centralizada de logging diagnostico do LozGates."""

import json
import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

from config import LOG_DIR


class JsonLogFormatter(logging.Formatter):
    """Serializa um registro por linha para facilitar busca e processamento."""

    def format(self, record):
        payload = {
            "timestamp": datetime.fromtimestamp(record.created).astimezone().isoformat(
                timespec="milliseconds"
            ),
            "level": record.levelname,
            "logger": record.name,
            "module": record.module,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def _positive_int(variable_name, default):
    try:
        return max(1, int(os.getenv(variable_name, default)))
    except (TypeError, ValueError):
        return default


def _resolve_level(level_name):
    candidate = (level_name or os.getenv("LOZGATES_LOG_LEVEL", "INFO")).upper()
    return getattr(logging, candidate, logging.INFO)


def configure_logging(log_dir=None, level=None, force=False):
    """Configura console, log geral e log exclusivo de erros de forma idempotente."""
    root_logger = logging.getLogger()
    managed_handlers = [
        handler
        for handler in root_logger.handlers
        if getattr(handler, "_lozgates_handler", False)
    ]
    if managed_handlers and not force:
        return Path(log_dir or LOG_DIR)

    for handler in managed_handlers:
        root_logger.removeHandler(handler)
        handler.close()

    resolved_dir = Path(log_dir or LOG_DIR).expanduser().resolve()
    resolved_dir.mkdir(parents=True, exist_ok=True)
    selected_level = _resolve_level(level)
    max_bytes = _positive_int("LOZGATES_LOG_MAX_BYTES", 2_000_000)
    backup_count = _positive_int("LOZGATES_LOG_BACKUP_COUNT", 5)

    json_formatter = JsonLogFormatter()
    console_formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    general_handler = RotatingFileHandler(
        resolved_dir / "lozgates.log",
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    general_handler.setLevel(selected_level)
    general_handler.setFormatter(json_formatter)

    error_handler = RotatingFileHandler(
        resolved_dir / "errors.log",
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(json_formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(selected_level)
    console_handler.setFormatter(console_formatter)

    for handler in (general_handler, error_handler, console_handler):
        handler._lozgates_handler = True
        root_logger.addHandler(handler)

    root_logger.setLevel(logging.DEBUG)
    logging.getLogger(__name__).info(
        "Logging inicializado em %s (nivel %s)",
        resolved_dir,
        logging.getLevelName(selected_level),
    )
    return resolved_dir
