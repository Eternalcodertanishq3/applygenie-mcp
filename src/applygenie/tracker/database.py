"""SQLite database setup and management for application tracking.

Handles database creation, schema migrations, and connection management.
"""

import logging
import sqlite3
from contextlib import contextmanager
from pathlib import Path

from applygenie.config import DATABASE_PATH

logger = logging.getLogger(__name__)

SCHEMA_VERSION = 1

SCHEMA_SQL = """
-- Applications log
CREATE TABLE IF NOT EXISTS applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company TEXT NOT NULL,
    role TEXT NOT NULL,
    portal TEXT,
    url TEXT,
    status TEXT DEFAULT 'applied',
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resume_used TEXT,
    cover_letter_used TEXT,
    custom_answers TEXT,
    job_description TEXT,
    notes TEXT,
    salary_range TEXT,
    location TEXT,
    remote_type TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Interview sessions
CREATE TABLE IF NOT EXISTS interview_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    application_id INTEGER REFERENCES applications(id),
    session_type TEXT NOT NULL,
    difficulty TEXT DEFAULT 'medium',
    questions TEXT,
    answers TEXT,
    scores TEXT,
    feedback TEXT,
    duration_minutes REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Custom answers bank (reusable across applications)
CREATE TABLE IF NOT EXISTS answer_bank (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_pattern TEXT NOT NULL,
    answer_text TEXT NOT NULL,
    company TEXT,
    times_used INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Schema versioning
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for fast queries
CREATE INDEX IF NOT EXISTS idx_applications_company ON applications(company);
CREATE INDEX IF NOT EXISTS idx_applications_status ON applications(status);
CREATE INDEX IF NOT EXISTS idx_applications_applied_at ON applications(applied_at);
CREATE INDEX IF NOT EXISTS idx_interview_sessions_app_id ON interview_sessions(application_id);
CREATE INDEX IF NOT EXISTS idx_answer_bank_pattern ON answer_bank(question_pattern);
"""


@contextmanager
def get_connection():
    """Get a database connection with automatic commit/rollback."""
    conn = sqlite3.connect(str(DATABASE_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def initialize_database() -> None:
    """Create the database and tables if they don't exist."""
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    with get_connection() as conn:
        conn.executescript(SCHEMA_SQL)

        # Check and record schema version
        cursor = conn.execute(
            "SELECT MAX(version) FROM schema_version"
        )
        row = cursor.fetchone()
        current_version = row[0] if row[0] is not None else 0

        if current_version < SCHEMA_VERSION:
            conn.execute(
                "INSERT INTO schema_version (version) VALUES (?)",
                (SCHEMA_VERSION,),
            )
            logger.info(f"Database initialized at schema version {SCHEMA_VERSION}")
        else:
            logger.debug(f"Database already at schema version {current_version}")


def reset_database() -> None:
    """Drop and recreate all tables. USE WITH CAUTION."""
    if DATABASE_PATH.exists():
        DATABASE_PATH.unlink()
    initialize_database()
    logger.warning("Database has been reset.")
