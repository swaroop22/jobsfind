"""
SQLite Application Tracker for managing job applications, interview stages, and statuses.
"""

import sqlite3
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime
import pandas as pd
from models import ApplicationRecord


DB_PATH = Path(__file__).parent / "job_applications.db"


class ApplicationTracker:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
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
            conn.commit()

    def add_application(
        self,
        job_title: str,
        company: str,
        location: str,
        status: str = "Saved",
        match_score: float = 0.0,
        notes: str = "",
        job_url: str = "",
        applied_date: Optional[str] = None
    ) -> int:
        if not applied_date:
            applied_date = datetime.now().strftime("%Y-%m-%d")

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO applications (job_title, company, location, status, applied_date, match_score, notes, job_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (job_title, company, location, status, applied_date, match_score, notes, job_url)
            )
            conn.commit()
            return cursor.lastrowid

    def update_status(self, app_id: int, new_status: str, notes: Optional[str] = None):
        with self._get_connection() as conn:
            if notes is not None:
                conn.execute(
                    "UPDATE applications SET status = ?, notes = ? WHERE id = ?",
                    (new_status, notes, app_id)
                )
            else:
                conn.execute(
                    "UPDATE applications SET status = ? WHERE id = ?",
                    (new_status, app_id)
                )
            conn.commit()

    def delete_application(self, app_id: int):
        with self._get_connection() as conn:
            conn.execute("DELETE FROM applications WHERE id = ?", (app_id,))
            conn.commit()

    def get_all(self) -> List[ApplicationRecord]:
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
                    match_score=row["match_score"],
                    notes=row["notes"] or "",
                    job_url=row["job_url"] or ""
                )
                for row in rows
            ]

    def to_dataframe(self) -> pd.DataFrame:
        records = self.get_all()
        if not records:
            return pd.DataFrame(
                columns=["ID", "Job Title", "Company", "Location", "Status", "Date", "Match Score %", "Notes", "Job URL"]
            )
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
        with self._get_connection() as conn:
            total = conn.execute("SELECT COUNT(*) FROM applications").fetchone()[0]
            saved = conn.execute("SELECT COUNT(*) FROM applications WHERE status = 'Saved'").fetchone()[0]
            applied = conn.execute("SELECT COUNT(*) FROM applications WHERE status = 'Applied'").fetchone()[0]
            interviewing = conn.execute("SELECT COUNT(*) FROM applications WHERE status = 'Interviewing'").fetchone()[0]
            offers = conn.execute("SELECT COUNT(*) FROM applications WHERE status = 'Offer'").fetchone()[0]
            avg_score = conn.execute("SELECT AVG(match_score) FROM applications").fetchone()[0] or 0.0

            return {
                "total": total,
                "saved": saved,
                "applied": applied,
                "interviewing": interviewing,
                "offers": offers,
                "avg_match_score": round(avg_score, 1)
            }
