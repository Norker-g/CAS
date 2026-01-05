from __future__ import annotations

import logging
import os
import sys

DEFAULT_FORMAT = "%(asctime)s %(levelname)s %(name)s:%(lineno)d: %(message)s"
DEFAULT_DATEFMT = "%H:%M:%S"

def setup_logging(
    *,
    enabled: bool | None = None,
    level: int | None = None,
    fmt: str = DEFAULT_FORMAT,
) -> None:
    """
    Console-only logging (stdout).
    - Call once from your CAS entry point (main/CLI/REPL).
    - Use enabled=False to silence logs.
    - Use level=logging.DEBUG to see debug logs.
    - Optional env var: CAS_LOG=debug / info / warning / error / 0
    """
    env = os.getenv("CAS_LOG", "").strip().lower()

    if enabled is None:
        enabled = env not in {"0", "off", "false", "no"}

    if not enabled:
        logging.getLogger().setLevel(logging.CRITICAL + 1)
        return

    if level is None:
        level_map = {
            "debug": logging.DEBUG,
            "info": logging.INFO,
            "warning": logging.WARNING,
            "warn": logging.WARNING,
            "error": logging.ERROR,
            "critical": logging.CRITICAL,
            "1": logging.DEBUG,      # convenience
            "true": logging.DEBUG,
            "on": logging.DEBUG,
        }
        level = level_map.get(env, logging.INFO)

    root = logging.getLogger()
    root.setLevel(level)

    # Avoid duplicate handlers if setup_logging is called more than once.
    if root.handlers:
        return

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(fmt=fmt, datefmt=DEFAULT_DATEFMT))
    root.addHandler(handler)

