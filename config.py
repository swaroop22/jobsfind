"""
Centralized configuration and environment settings for JobsFind.
Adheres to 12-factor application and enterprise configuration standards.
"""

import os
import logging
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

# Gracefully silence platform-specific LibreSSL warning on macOS Python 3.9
warnings.filterwarnings("ignore", message=".*urllib3 v2 only supports OpenSSL.*")


BASE_DIR = Path(__file__).resolve().parent


@dataclass(frozen=True)
class Settings:
    """Application settings loaded from environment with enterprise defaults."""

    base_dir: Path = BASE_DIR
    profile_path: Path = Path(
        os.getenv("JOBSFIND_PROFILE_PATH", str(BASE_DIR / "resume_profile.json"))
    )
    db_path: Path = Path(
        os.getenv("JOBSFIND_DB_PATH", str(BASE_DIR / "job_applications.db"))
    )
    log_level: str = os.getenv("JOBSFIND_LOG_LEVEL", "INFO").upper()
    http_timeout: int = int(os.getenv("JOBSFIND_HTTP_TIMEOUT", "5"))
    max_retries: int = int(os.getenv("JOBSFIND_MAX_RETRIES", "3"))
    jobicy_api_url: str = os.getenv(
        "JOBSFIND_JOBICY_API_URL",
        "https://jobicy.com/api/v2/remote-jobs",
    )


settings = Settings()


def setup_logging(level: Optional[str] = None) -> logging.Logger:
    """Configure structured logging across the application."""
    log_level_name = level or settings.log_level
    numeric_level = getattr(logging, log_level_name, logging.INFO)

    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logger = logging.getLogger("jobsfind")
    logger.setLevel(numeric_level)
    return logger
