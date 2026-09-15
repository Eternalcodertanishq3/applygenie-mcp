"""Behavioral interview coach and STAR method evaluation module.

Guides candidates through Situation, Task, Action, and Result structured responses.
"""

from typing import Any
from applygenie.interview.question_bank import BEHAVIORAL_QUESTIONS, BehavioralQuestion


class BehavioralCoach:
    """Evaluates and guides behavioral interview responses."""

    def __init__(self, question: BehavioralQuestion) -> None:
        self.question = question

    def get_prompt(self) -> str:
        """Return the behavioral question and guidance."""
        guide_lines = "\n".join(f"- {stage}: {desc}" for stage, desc in self.question.star_guide.items())
        return (
            f"=== Behavioral Interview Question ===\n"
            f"Framework: {self.question.company_framework} (Competency: {self.question.competency.upper()})\n\n"
            f"\"{self.question.question}\"\n\n"
            f"Recommended STAR Structure:\n{guide_lines}\n\n"
            f"Tip: Allocate ~50% of your answer to the concrete actions YOU personally took."
        )

    def analyze_star_response(self, response_text: str) -> dict[str, Any]:
        """Perform heuristic structural checks on a STAR response."""
        words = response_text.split()
        word_count = len(words)

        lower = response_text.lower()

        # Heuristic detection of STAR sections
        indicators = {
            "situation": any(w in lower for w in ["situation", "when i was", "at my previous", "in my role", "project"]),
            "task": any(w in lower for w in ["task", "goal", "needed to", "responsible for", "objective", "challenge"]),
            "action": any(w in lower for w in ["i decided", "i implemented", "i built", "i initiated", "i proposed", "i wrote", "i led"]),
            "result": any(w in lower for w in ["result", "impact", "reduced", "increased", "achieved", "improved", "%", "outcomes"]),
        }

        # Ownership ratio: "I" vs "We"
        i_count = sum(1 for w in words if w.lower() in ("i", "i'm", "i've", "my", "me"))
        we_count = sum(1 for w in words if w.lower() in ("we", "we're", "we've", "our", "us"))
        ownership_ratio = round(i_count / max(1, we_count), 2)

        # Conciseness recommendation
        if word_count < 100:
            pacing_feedback = "Answer may be too brief. Expand on your personal actions and measurable impact."
        elif word_count > 600:
            pacing_feedback = "Answer is running long (>4 minutes speaking time). Tighten the situation and get to actions quicker."
        else:
            pacing_feedback = "Good length (approx. 2-3 minutes speaking pace)."

        return {
            "word_count": word_count,
            "star_components_detected": indicators,
            "ownership_ratio": {
                "i_count": i_count,
                "we_count": we_count,
                "ratio": ownership_ratio,
                "assessment": "Healthy individual ownership" if ownership_ratio >= 1.5 else "Consider emphasizing your individual role over the team",
            },
            "pacing_feedback": pacing_feedback,
            "evaluation_criteria": self.question.evaluation_criteria,
        }
