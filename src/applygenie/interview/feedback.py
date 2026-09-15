"""Interview scoring rubrics and feedback generation.

Implements structured 1-5 evaluations across Coding, Behavioral, and System Design.
"""

from typing import Any


def format_coding_rubric(
    correctness: int,
    complexity: int,
    code_quality: int,
    communication: int,
    feedback_notes: str,
) -> dict[str, Any]:
    """Generate standardized coding evaluation report card."""
    scores = {
        "algorithmic_correctness": min(max(1, correctness), 5),
        "time_space_complexity": min(max(1, complexity), 5),
        "code_quality_and_style": min(max(1, code_quality), 5),
        "technical_communication": min(max(1, communication), 5),
    }
    overall_score = round(sum(scores.values()) / len(scores), 1)

    return {
        "interview_type": "coding",
        "scores": scores,
        "overall_score": f"{overall_score}/5.0",
        "verdict": "STRONG HIRE" if overall_score >= 4.5 else ("HIRE" if overall_score >= 3.8 else ("LEAN HIRE" if overall_score >= 3.0 else "NO HIRE")),
        "coaching_feedback": feedback_notes,
    }


def format_behavioral_rubric(
    star_structure: int,
    ownership: int,
    measurable_impact: int,
    cultural_alignment: int,
    delivery: int,
    feedback_notes: str,
) -> dict[str, Any]:
    """Generate standardized behavioral evaluation report card."""
    scores = {
        "star_structure": min(max(1, star_structure), 5),
        "personal_ownership": min(max(1, ownership), 5),
        "measurable_impact": min(max(1, measurable_impact), 5),
        "company_cultural_alignment": min(max(1, cultural_alignment), 5),
        "executive_presence_and_delivery": min(max(1, delivery), 5),
    }
    overall_score = round(sum(scores.values()) / len(scores), 1)

    return {
        "interview_type": "behavioral",
        "scores": scores,
        "overall_score": f"{overall_score}/5.0",
        "verdict": "STRONG HIRE" if overall_score >= 4.5 else ("HIRE" if overall_score >= 3.8 else ("LEAN HIRE" if overall_score >= 3.0 else "NO HIRE")),
        "coaching_feedback": feedback_notes,
    }


def format_system_design_rubric(
    requirements_clarity: int,
    component_architecture: int,
    data_modeling: int,
    tradeoffs: int,
    fault_tolerance: int,
    feedback_notes: str,
) -> dict[str, Any]:
    """Generate standardized system design evaluation report card."""
    scores = {
        "requirements_and_scope": min(max(1, requirements_clarity), 5),
        "component_architecture": min(max(1, component_architecture), 5),
        "data_modeling_and_storage": min(max(1, data_modeling), 5),
        "tradeoff_justification": min(max(1, tradeoffs), 5),
        "fault_tolerance_and_resilience": min(max(1, fault_tolerance), 5),
    }
    overall_score = round(sum(scores.values()) / len(scores), 1)

    return {
        "interview_type": "system_design",
        "scores": scores,
        "overall_score": f"{overall_score}/5.0",
        "verdict": "STAFF / PRINCIPAL" if overall_score >= 4.7 else ("SENIOR" if overall_score >= 4.0 else ("MID-LEVEL" if overall_score >= 3.0 else "NEEDS PREPARATION")),
        "coaching_feedback": feedback_notes,
    }
