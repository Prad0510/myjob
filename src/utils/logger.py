import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FILE = os.getenv("LOG_FILE", "logs/myjob.log")
ENABLE_FILE_LOGGING = os.getenv("ENABLE_FILE_LOGGING", "true").lower() in ("true", "1", "yes")

_initialized = False


def _setup_root_logging():
    global _initialized
    if _initialized:
        return

    root_logger = logging.getLogger("myjob")
    level = getattr(logging, LOG_LEVEL, logging.INFO)
    root_logger.setLevel(level)

    # Avoid duplicate handlers
    if not root_logger.handlers:
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] [%(name)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

        # Rotating File handler
        if ENABLE_FILE_LOGGING and LOG_FILE:
            try:
                log_path = Path(LOG_FILE)
                log_path.parent.mkdir(parents=True, exist_ok=True)

                file_handler = RotatingFileHandler(
                    log_path,
                    maxBytes=5 * 1024 * 1024,  # 5 MB
                    backupCount=5,
                    encoding="utf-8",
                )
                file_handler.setLevel(level)
                file_handler.setFormatter(formatter)
                root_logger.addHandler(file_handler)
            except Exception as e:
                console_handler.handle(
                    logging.LogRecord(
                        name="myjob.logger",
                        level=logging.WARNING,
                        pathname=__file__,
                        lineno=45,
                        msg=f"Failed to initialize file logger at {LOG_FILE}: {e}",
                        args=(),
                        exc_info=None,
                    )
                )

    _initialized = True


def get_logger(name: str | None = None) -> logging.Logger:
    """
    Get a structured logger instance under the 'myjob' namespace.
    """
    _setup_root_logging()
    if name:
        if name.startswith("myjob."):
            return logging.getLogger(name)
        return logging.getLogger(f"myjob.{name}")
    return logging.getLogger("myjob")

