import logging
import sys
from logging.handlers import RotatingFileHandler
from applygenie.config import LOGS_DIR

def setup_logging(level: str = "INFO") -> None:
    """Configure structured logging for the application."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
    )
    
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setFormatter(formatter)
    
    log_file = LOGS_DIR / "applygenie.log"
    file_handler = RotatingFileHandler(
        log_file, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    
    root_logger = logging.getLogger("applygenie")
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    # Avoid adding handlers multiple times
    if not root_logger.handlers:
        root_logger.addHandler(console_handler)
        root_logger.addHandler(file_handler)
