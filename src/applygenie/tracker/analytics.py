"""Application analytics and metrics calculation.

Provides insights into job application velocity, conversion rates, and portal performance.
"""

import logging
from typing import Any

from applygenie.tracker.database import get_connection, initialize_database

logger = logging.getLogger(__name__)


def get_application_stats() -> dict[str, Any]:
    """Calculate aggregate statistics across all logged job applications."""
    initialize_database()

    with get_connection() as conn:
        # Total counts
        total_count = conn.execute("SELECT COUNT(*) FROM applications").fetchone()[0]

        if total_count == 0:
            return {
                "total_applications": 0,
                "status_breakdown": {},
                "portal_breakdown": {},
                "interview_rate": "0.0%",
                "offer_rate": "0.0%",
                "top_companies": [],
            }

        # Status breakdown
        status_cursor = conn.execute(
            """
            SELECT status, COUNT(*) as count
            FROM applications
            GROUP BY status
            ORDER BY count DESC
            """
        )
        status_breakdown = {row["status"]: row["count"] for row in status_cursor.fetchall()}

        # Portal breakdown
        portal_cursor = conn.execute(
            """
            SELECT COALESCE(portal, 'Unknown') as portal_name, COUNT(*) as count
            FROM applications
            GROUP BY portal_name
            ORDER BY count DESC
            """
        )
        portal_breakdown = {row["portal_name"]: row["count"] for row in portal_cursor.fetchall()}

        # Success metrics
        interview_count = sum(
            status_breakdown.get(st, 0)
            for st in ("interview", "technical", "screening", "offer", "accepted")
        )
        offer_count = status_breakdown.get("offer", 0) + status_breakdown.get("accepted", 0)

        interview_rate = f"{(interview_count / total_count * 100):.1f}%"
        offer_rate = f"{(offer_count / total_count * 100):.1f}%"

        # Top companies
        comp_cursor = conn.execute(
            """
            SELECT company, COUNT(*) as count
            FROM applications
            GROUP BY company
            ORDER BY count DESC
            LIMIT 5
            """
        )
        top_companies = [dict(row) for row in comp_cursor.fetchall()]

        return {
            "total_applications": total_count,
            "status_breakdown": status_breakdown,
            "portal_breakdown": portal_breakdown,
            "interview_rate": interview_rate,
            "offer_rate": offer_rate,
            "top_companies": top_companies,
        }


def get_weekly_application_velocity() -> list[dict[str, Any]]:
    """Get the count of applications submitted grouped by week."""
    initialize_database()

    with get_connection() as conn:
        cursor = conn.execute(
            """
            SELECT strftime('%Y-%W', applied_at) as week, COUNT(*) as count
            FROM applications
            GROUP BY week
            ORDER BY week DESC
            LIMIT 12
            """
        )
        return [dict(row) for row in cursor.fetchall()]
