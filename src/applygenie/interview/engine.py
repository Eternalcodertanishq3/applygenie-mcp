"""Interview session engine orchestrator.

Creates, routes, and tracks mock interview practice sessions.
"""

from typing import Any
from applygenie.interview.question_bank import (
    CODING_QUESTIONS,
    BEHAVIORAL_QUESTIONS,
    SYSTEM_DESIGN_QUESTIONS,
    get_questions_by_type,
)
from applygenie.interview.coding import CodingSimulator
from applygenie.interview.behavioral import BehavioralCoach
from applygenie.interview.system_design import SystemDesignInterviewer


class InterviewSessionEngine:
    """Manages active candidate interview sessions."""

    def __init__(self) -> None:
        self.active_session: dict[str, Any] | None = None

    def start_session(
        self,
        session_type: str,
        company: str = "General",
        difficulty: str = "medium",
    ) -> dict[str, Any]:
        """Start a new interview session and initialize the challenge."""
        stype = session_type.lower()
        if stype == "coding":
            # Match company or difficulty
            matches = [q for q in CODING_QUESTIONS if q.difficulty == difficulty or company.lower() in [c.lower() for c in q.company_tags]]
            chosen = matches[0] if matches else CODING_QUESTIONS[0]
            simulator = CodingSimulator(chosen)
            self.active_session = {
                "type": "coding",
                "instance": simulator,
                "company": company,
                "prompt": simulator.get_prompt(),
            }
            return {
                "status": "started",
                "session_type": "coding",
                "title": chosen.title,
                "prompt": self.active_session["prompt"],
            }

        elif stype == "behavioral":
            chosen = BEHAVIORAL_QUESTIONS[0]
            coach = BehavioralCoach(chosen)
            self.active_session = {
                "type": "behavioral",
                "instance": coach,
                "company": company,
                "prompt": coach.get_prompt(),
            }
            return {
                "status": "started",
                "session_type": "behavioral",
                "question": chosen.question,
                "prompt": self.active_session["prompt"],
            }

        elif stype in ("system_design", "system-design"):
            chosen = SYSTEM_DESIGN_QUESTIONS[0]
            interviewer = SystemDesignInterviewer(chosen)
            self.active_session = {
                "type": "system_design",
                "instance": interviewer,
                "company": company,
                "prompt": interviewer.get_initial_brief(),
            }
            return {
                "status": "started",
                "session_type": "system_design",
                "title": chosen.title,
                "prompt": self.active_session["prompt"],
            }
        else:
            return {"error": f"Unknown interview session type: {session_type}. Choose 'coding', 'behavioral', or 'system_design'."}

    def get_hint(self) -> dict[str, Any]:
        """Request progressive hint for active coding session."""
        if not self.active_session or self.active_session.get("type") != "coding":
            return {"error": "No active coding session to provide hints for."}
        simulator: CodingSimulator = self.active_session["instance"]
        return simulator.get_next_hint()

    def advance_system_design(self, candidate_input: str) -> dict[str, Any]:
        """Advance system design interview to next phase."""
        if not self.active_session or self.active_session.get("type") != "system_design":
            return {"error": "No active system design session to advance."}
        interviewer: SystemDesignInterviewer = self.active_session["instance"]
        return interviewer.advance_phase(candidate_input)

    def analyze_behavioral_answer(self, answer_text: str) -> dict[str, Any]:
        """Analyze STAR structure of candidate behavioral response."""
        if not self.active_session or self.active_session.get("type") != "behavioral":
            return {"error": "No active behavioral session to analyze."}
        coach: BehavioralCoach = self.active_session["instance"]
        return coach.analyze_star_response(answer_text)


session_engine = InterviewSessionEngine()
