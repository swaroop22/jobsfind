"""
SQLite Application Tracker for managing job applications, interview stages, and statuses.
Provides robust connection lifecycle management, transaction rollback safety, and structured logging.
"""

import sqlite3
import logging
from contextlib import contextmanager
from typing import List, Dict, Any, Optional, Iterator
from pathlib import Path
from datetime import datetime
import pandas as pd

from config import settings
from exceptions import DatabaseError
from models import ApplicationRecord, ApplicationStatus

logger = logging.getLogger(__name__)


class ApplicationTracker:
    """Enterprise SQLite persistence layer for candidate job applications."""

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize the application tracker.

        Args:
            db_path: Optional custom path to SQLite database. Defaults to configured DB_PATH.
        """
        self.db_path = Path(db_path) if db_path else settings.db_path
        self._init_db()

    @contextmanager
    def _get_connection(self) -> Iterator[sqlite3.Connection]:
        """
        Safe context manager ensuring transaction commit/rollback and connection closure.

        Yields:
            sqlite3.Connection instance with Row factory.

        Raises:
            DatabaseError: If connection or execution fails.
        """
        conn = None
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            yield conn
            conn.commit()
        except sqlite3.Error as exc:
            if conn:
                try:
                    conn.rollback()
                except Exception as rollback_err:
                    logger.warning("Failed to rollback transaction: %s", rollback_err)
            logger.error("Database operation failed on %s: %s", self.db_path, exc, exc_info=True)
            raise DatabaseError(f"Database operation failed: {exc}") from exc
        finally:
            if conn:
                conn.close()

    def _init_db(self) -> None:
        """Create applications table and index if they do not exist."""
        try:
            with self._get_connection() as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS applications (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        job_title TEXT NOT NULL,
                        company TEXT NOT NULL,
                        location TEXT NOT NULL,
                        status TEXT NOT NULL DEFAULT 'Saved',
                        applied_date TEXT NOT NULL,
                        match_score REAL DEFAULT 0.0,
                        notes TEXT DEFAULT '',
                        job_url TEXT DEFAULT '',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_applications_status ON applications(status)"
                )
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_applications_company ON applications(company)"
                )
            logger.debug("Database initialized at %s", self.db_path)
        except Exception as exc:
            logger.error("Failed to initialize database: %s", exc, exc_info=True)
            raise DatabaseError(f"Failed to initialize database: {exc}") from exc

    def add_application(
        self,
        job_title: str,
        company: str,
        location: str = "Ohio / Remote",
        status: str = ApplicationStatus.SAVED.value,
        match_score: float = 0.0,
        notes: str = "",
        job_url: str = "",
        applied_date: Optional[str] = None,
    ) -> int:
        """
        Record a new job application.

        Returns:
            The newly inserted record ID.
        """
        if not job_title or not company:
            raise ValueError("Job title and company name are required.")

        if not applied_date:
            applied_date = datetime.now().strftime("%Y-%m-%d")

        valid_statuses = ApplicationStatus.values()
        if status not in valid_statuses:
            logger.warning("Unrecognized status '%s'; defaulting to '%s'", status, ApplicationStatus.SAVED.value)
            status = ApplicationStatus.SAVED.value

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO applications (job_title, company, location, status, applied_date, match_score, notes, job_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (job_title.strip(), company.strip(), location.strip(), status, applied_date, float(match_score), notes.strip(), job_url.strip())
            )
            app_id = cursor.lastrowid
            logger.info("Application recorded with ID %d: '%s' at '%s'", app_id, job_title, company)
            return app_id

    def update_status(self, app_id: int, new_status: str, notes: Optional[str] = None) -> bool:
        """
        Update the status and optional notes for an application.

        Returns:
            True if a row was updated, False if record was not found.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if notes is not None:
                cursor.execute(
                    "UPDATE applications SET status = ?, notes = ? WHERE id = ?",
                    (new_status, notes.strip(), app_id)
                )
            else:
                cursor.execute(
                    "UPDATE applications SET status = ? WHERE id = ?",
                    (new_status, app_id)
                )
            updated = cursor.rowcount > 0
            if updated:
                logger.info("Application ID %d updated to status '%s'", app_id, new_status)
            else:
                logger.warning("Application ID %d not found for update", app_id)
            return updated

    def delete_application(self, app_id: int) -> bool:
        """
        Delete an application record by ID.

        Returns:
            True if deleted, False if record was not found.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM applications WHERE id = ?", (app_id,))
            deleted = cursor.rowcount > 0
            if deleted:
                logger.info("Application ID %d deleted", app_id)
            return deleted

    def get_all(self) -> List[ApplicationRecord]:
        """Retrieve all application records ordered by ID descending."""
        with self._get_connection() as conn:
            rows = conn.execute("SELECT * FROM applications ORDER BY id DESC").fetchall()
            return [
                ApplicationRecord(
                    id=row["id"],
                    job_title=row["job_title"],
                    company=row["company"],
                    location=row["location"],
                    status=row["status"],
                    applied_date=row["applied_date"],
                    match_score=float(row["match_score"] or 0.0),
                    notes=row["notes"] or "",
                    job_url=row["job_url"] or ""
                )
                for row in rows
            ]

    def to_dataframe(self) -> pd.DataFrame:
        """Export applications to a formatted pandas DataFrame."""
        records = self.get_all()
        columns = ["ID", "Job Title", "Company", "Location", "Status", "Date", "Match Score %", "Notes", "Job URL"]
        if not records:
            return pd.DataFrame(columns=columns)

        data = [
            {
                "ID": r.id,
                "Job Title": r.job_title,
                "Company": r.company,
                "Location": r.location,
                "Status": r.status,
                "Date": r.applied_date,
                "Match Score %": f"{r.match_score:.1f}%",
                "Notes": r.notes,
                "Job URL": r.job_url,
            }
            for r in records
        ]
        return pd.DataFrame(data)

    def get_statistics(self) -> Dict[str, Any]:
        """Aggregate key application metrics."""
        with self._get_connection() as conn:
            total = conn.execute("SELECT COUNT(*) FROM applications").fetchone()[0]
            saved = conn.execute("SELECT COUNT(*) FROM applications WHERE status = 'Saved'").fetchone()[0]
            applied = conn.execute("SELECT COUNT(*) FROM applications WHERE status = 'Applied'").fetchone()[0]
            interviewing = conn.execute("SELECT COUNT(*) FROM applications WHERE status = 'Interviewing'").fetchone()[0]
            offers = conn.execute("SELECT COUNT(*) FROM applications WHERE status = 'Offer'").fetchone()[0]
            avg_score_row = conn.execute("SELECT AVG(match_score) FROM applications").fetchone()
            avg_score = avg_score_row[0] if avg_score_row and avg_score_row[0] is not None else 0.0

            return {
                "total": total,
                "saved": saved,
                "applied": applied,
                "interviewing": interviewing,
                "offers": offers,
                "avg_match_score": round(float(avg_score), 1)
            }
