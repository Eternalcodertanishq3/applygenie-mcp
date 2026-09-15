import os
from pathlib import Path
from applygenie import __version__

APP_NAME = "ApplyGenie"
APP_VERSION = __version__
DATA_DIR = Path.home() / ".applygenie"
PROFILE_PATH = DATA_DIR / "profile.json"
DATABASE_PATH = DATA_DIR / "applygenie.db"
RESUMES_DIR = DATA_DIR / "resumes"
LOGS_DIR = DATA_DIR / "logs"

MAX_ACTIONS_PER_MINUTE = 30
MIN_ACTION_DELAY = 0.5
SCREENSHOT_QUALITY = 70
SCREENSHOT_MAX_WIDTH = 1920
BLOCKED_KEY_COMBOS = {"alt+f4", "ctrl+alt+delete"}
FAILSAFE_ENABLED = True

def ensure_data_dirs():
    """Ensure all required data directories exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    RESUMES_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

ensure_data_dirs()
