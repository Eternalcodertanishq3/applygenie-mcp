"""Tests for Mock Interview Engine and Scoring Rubrics."""

import pytest
from applygenie.interview.engine import session_engine
from applygenie.interview.feedback import (
    format_coding_rubric, format_behavioral_rubric, format_system_design_rubric
)


def test_coding_interview_flow():
    session = session_engine.start_session("coding", company="Google", difficulty="easy")
    assert session["status"] == "started"
    assert "Two Sum" in session["title"]

    # Request hint
    hint_res = session_engine.get_hint()
    assert hint_res["hint_level"] == 1
    assert "Rung 1" in hint_res["hint"]


def test_behavioral_interview_flow():
    session = session_engine.start_session("behavioral", company="Amazon")
    assert session["status"] == "started"
    assert "question" in session

    # Analyze answer
    sample_answer = (
        "When I was at my previous company, our payment microservice experienced high latency during Black Friday. "
        "I was tasked with resolving the bottleneck within two weeks. "
        "I decided to profile the SQL queries and implemented a Redis caching layer with a write-through strategy. "
        "As a result, we reduced p99 latency from 450ms to 65ms, resulting in 0 failed checkouts."
    )
    analysis = session_engine.analyze_behavioral_answer(sample_answer)
    assert analysis["word_count"] > 30
    assert analysis["ownership_ratio"]["ratio"] > 1.0
    assert analysis["star_components_detected"]["action"] is True


def test_rubrics():
    code_eval = format_coding_rubric(5, 5, 4, 4, "Clean hash map implementation.")
    assert code_eval["overall_score"] == "4.5/5.0"
    assert code_eval["verdict"] == "STRONG HIRE"

    sys_eval = format_system_design_rubric(5, 5, 4, 5, 5, "Excellent partitioning strategy.")
    assert sys_eval["verdict"] == "STAFF / PRINCIPAL"
