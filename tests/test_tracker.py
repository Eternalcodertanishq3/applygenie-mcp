"""Tests for Application Tracker and Analytics."""

import pytest
from applygenie.tracker.database import initialize_database
from applygenie.tracker.models import (
    log_application, update_application_status, get_application, list_applications, search_applications
)
from applygenie.tracker.analytics import get_application_stats


def test_tracker_lifecycle(tmp_path, monkeypatch):
    test_db = tmp_path / "test_applygenie.db"
    monkeypatch.setattr("applygenie.tracker.database.DATABASE_PATH", test_db)

    initialize_database()

    app_id = log_application(
        company="Cyncly",
        role="AI/ML Engineer",
        portal="Oracle",
        url="https://cyncly.oraclecloud.com/job/123",
        notes="Applied with tailored CV resume.",
        salary_range="6-8 LPA",
        location="Bangalore",
    )

    assert app_id == 1

    app = get_application(app_id)
    assert app is not None
    assert app["company"] == "Cyncly"
    assert app["status"] == "applied"

    # Status update
    res = update_application_status(app_id, "interview", "Received recruiter reachout!")
    assert "updated to 'interview'" in res

    updated_app = get_application(app_id)
    assert updated_app["status"] == "interview"
    assert "recruiter reachout" in updated_app["notes"]

    # Search
    search_res = search_applications("Cyncly")
    assert len(search_res) == 1
    assert search_res[0]["role"] == "AI/ML Engineer"

    # Analytics
    stats = get_application_stats()
    assert stats["total_applications"] == 1
    assert stats["interview_rate"] == "100.0%"
