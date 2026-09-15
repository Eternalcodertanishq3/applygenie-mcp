"""Application tracking models and CRUD operations.

Provides functions to log, query, update, and search job applications.
"""

import json
import logging
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Any

from applygenie.tracker.database import get_connection, initialize_database

logger = logging.getLogger(__name__)


@dataclass
class ApplicationRecord:
    """Represents a tracked job application."""

    id: int | None = None
    company: str = ""
    role: str = ""
    portal: str | None = None
    url: str | None = None
    status: str = "applied"
    applied_at: str | None = None
    resume_used: str | None = None
    cover_letter_used: str | None = None
    custom_answers: dict[str, str] | None = None
    job_description: str | None = None
    notes: str | None = None
    salary_range: str | None = None
    location: str | None = None
    remote_type: str | None = None
    updated_at: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary, serializing nested objects."""
        d = asdict(self)
        if d.get("custom_answers") and isinstance(d["custom_answers"], dict):
            d["custom_answers"] = json.dumps(d["custom_answers"])
        return d


# Valid status transitions
VALID_STATUSES = {
    "applied",
    "screening",
    "interview",
    "technical",
    "offer",
    "rejected",
    "withdrawn",
    "accepted",
}


def log_application(
    company: str,
    role: str,
    portal: str | None = None,
    url: str | None = None,
    resume_used: str | None = None,
    cover_letter_used: str | None = None,
    custom_answers: dict[str, str] | None = None,
    job_description: str | None = None,
    notes: str | None = None,
    salary_range: str | None = None,
    location: str | None = None,
    remote_type: str | None = None,
) -> int:
    """Log a new job application. Returns the application ID."""
    initialize_database()

    custom_answers_json = json.dumps(custom_answers) if custom_answers else None

    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO applications
                (company, role, portal, url, resume_used, cover_letter_used,
                 custom_answers, job_description, notes, salary_range, location, remote_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                company, role, portal, url, resume_used, cover_letter_used,
                custom_answers_json, job_description, notes, salary_range,
                location, remote_type,
            ),
        )
        app_id = cursor.lastrowid
        logger.info(f"Logged application #{app_id}: {role} at {company}")
        return app_id


def update_application_status(app_id: int, status: str, notes: str | None = None) -> str:
    """Update the status of an application."""
    if status not in VALID_STATUSES:
        return f"Invalid status '{status}'. Valid statuses: {', '.join(sorted(VALID_STATUSES))}"

    initialize_database()
    with get_connection() as conn:
        updates = ["status = ?", "updated_at = CURRENT_TIMESTAMP"]
        params: list[Any] = [status]

        if notes:
            updates.append("notes = COALESCE(notes || '\n' || ?, ?)")
            params.extend([notes, notes])

        params.append(app_id)
        conn.execute(
            f"UPDATE applications SET {', '.join(updates)} WHERE id = ?",
            params,
        )
        return f"Application #{app_id} status updated to '{status}'"


def get_application(app_id: int) -> dict[str, Any] | None:
    """Get a single application by ID."""
    initialize_database()
    with get_connection() as conn:
        cursor = conn.execute("SELECT * FROM applications WHERE id = ?", (app_id,))
        row = cursor.fetchone()
        if row:
            result = dict(row)
            if result.get("custom_answers"):
                try:
                    result["custom_answers"] = json.loads(result["custom_answers"])
                except json.JSONDecodeError:
                    pass
            return result
        return None


def list_applications(
    status: str | None = None,
    company: str | None = None,
    portal: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[dict[str, Any]]:
    """List applications with optional filters."""
    initialize_database()
    conditions = []
    params: list[Any] = []

    if status:
        conditions.append("status = ?")
        params.append(status)
    if company:
        conditions.append("company LIKE ?")
        params.append(f"%{company}%")
    if portal:
        conditions.append("portal LIKE ?")
        params.append(f"%{portal}%")

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    params.extend([limit, offset])

    with get_connection() as conn:
        cursor = conn.execute(
            f"""
            SELECT * FROM applications
            {where_clause}
            ORDER BY applied_at DESC
            LIMIT ? OFFSET ?
            """,
            params,
        )
        return [dict(row) for row in cursor.fetchall()]


def search_applications(query: str) -> list[dict[str, Any]]:
    """Search applications by company, role, or notes."""
    initialize_database()
    pattern = f"%{query}%"
    with get_connection() as conn:
        cursor = conn.execute(
            """
            SELECT * FROM applications
            WHERE company LIKE ? OR role LIKE ? OR notes LIKE ? OR portal LIKE ?
            ORDER BY applied_at DESC
            LIMIT 50
            """,
            (pattern, pattern, pattern, pattern),
        )
        return [dict(row) for row in cursor.fetchall()]


def delete_application(app_id: int) -> str:
    """Delete an application record."""
    initialize_database()
    with get_connection() as conn:
        conn.execute("DELETE FROM applications WHERE id = ?", (app_id,))
        return f"Application #{app_id} deleted."
