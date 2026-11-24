"""Logging utilities."""

import logging
import sys
from pathlib import Path


def setup_logging(level: str = "INFO", log_file: str = None) -> None:
    """
    Setup logging configuration.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR).
        log_file: Optional log file path.
    """
    log_level = getattr(logging, level.upper(), logging.INFO)

    handlers = [logging.StreamHandler(sys.stdout)]
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_path))

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=handlers,
    )

    # Reduce noise from some libraries
    logging.getLogger("PIL").setLevel(logging.WARNING)
    logging.getLogger("onnxruntime").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)