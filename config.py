"""
Configuration for Resume Upload Automation.
Loads credentials from .env and defines all settings.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# ── Load .env ──────────────────────────────────────────────
load_dotenv()

# ── Paths ──────────────────────────────────────────────────
PROJECT_DIR = Path(__file__).parent.resolve()
BASE_RESUME = PROJECT_DIR / "Abhay__cv.pdf"
LOGS_DIR = PROJECT_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# ── Naukri ─────────────────────────────────────────────────
NAUKRI_EMAIL = os.getenv("NAUKRI_EMAIL", "")
NAUKRI_PASSWORD = os.getenv("NAUKRI_PASSWORD", "")
NAUKRI_LOGIN_URL = "https://www.naukri.com/nlogin/login"
NAUKRI_PROFILE_URL = "https://www.naukri.com/mnjuser/profile"

# ── Indeed ─────────────────────────────────────────────────
INDEED_EMAIL = os.getenv("INDEED_EMAIL", "")
INDEED_PASSWORD = os.getenv("INDEED_PASSWORD", "")
INDEED_LOGIN_URL = "https://secure.indeed.com/auth"
INDEED_RESUME_URL = "https://my.indeed.com/resume"

# ── Anti-Detection Delays (seconds) ───────────────────────
MIN_DELAY = 2          # minimum random delay between actions
MAX_DELAY = 5          # maximum random delay between actions
PAGE_LOAD_WAIT = 8     # wait for pages to fully load
KEYSTROKE_MIN = 0.05   # min delay between keystrokes
KEYSTROKE_MAX = 0.15   # max delay between keystrokes

# ── Chrome Options ─────────────────────────────────────────
CHROME_ARGUMENTS = [
    "--start-maximized"
]

# When running on GitHub Actions, we need headless mode so it doesn't crash on the Linux server without a display
if os.getenv("GITHUB_ACTIONS"):
    CHROME_ARGUMENTS.extend([
        "--headless=new",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-gpu",
        "--window-size=1920,1080"
    ])

CHROME_EXCLUDE_SWITCHES = ["enable-automation"]
CHROME_PREFS = {
    "credentials_enable_service": False,
    "profile.password_manager_enabled": False,
}

# ── Resume Naming ──────────────────────────────────────────
RESUME_NAME_PATTERN = "Abhay_Resume_{date}.pdf"   # {date} → 10_Mar_2026
