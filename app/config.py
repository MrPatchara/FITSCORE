import os
from pathlib import Path

# Base Directories
APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent

# User Data Directories
USER_DATA_DIR = Path(os.path.expanduser("~")) / "Documents" / "FITSCORE"
PHOTOS_DIR = USER_DATA_DIR / "photos"
REPORTS_DIR = USER_DATA_DIR / "reports"

# Ensure directories exist
USER_DATA_DIR.mkdir(parents=True, exist_ok=True)
PHOTOS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Database Configuration
DATABASE_URL = f"sqlite:///{USER_DATA_DIR}/fittest.db"

# Application Settings
APP_NAME = "FITSCORE"
VERSION = "1.0.0"
DEFAULT_PHOTO_FILENAME = "default_avatar.png"
