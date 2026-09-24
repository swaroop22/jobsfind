"""
Unit tests for config.py environment configuration and logging setup.
"""

import os
import logging
from config import Settings, setup_logging


class TestConfig:
    def test_default_settings(self):
        cfg = Settings()
        assert cfg.log_level in ["DEBUG", "INFO", "WARNING", "ERROR"]
        assert cfg.http_timeout > 0
        assert cfg.max_retries >= 1
        assert cfg.profile_path.name == "resume_profile.json"
        assert cfg.db_path.name == "job_applications.db"

    def test_setup_logging(self):
        logger = setup_logging(level="DEBUG")
        assert logger.level == logging.DEBUG
        assert logger.name == "jobsfind"
