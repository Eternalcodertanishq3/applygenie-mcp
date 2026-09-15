"""System design interview 4-phase state machine simulator.

Orchestrates structured architecture interviews across Scope, HLD, Deep Dive, and Stress Test.
"""

from typing import Any
from applygenie.interview.question_bank import SYSTEM_DESIGN_QUESTIONS, SystemDesignQuestion

PHASES = ["1. Scope & Requirements", "2. High-Level Design (HLD)", "3. Component Deep Dive", "4. Stress Scenarios & Bottlenecks"]


class SystemDesignInterviewer:
    """Manages an interactive multi-phase system design interview."""

    def __init__(self, question: SystemDesignQuestion) -> None:
        self.question = question
        self.current_phase_index = 0

    @property
    def current_phase(self) -> str:
        return PHASES[min(self.current_phase_index, len(PHASES) - 1)]

    def get_initial_brief(self) -> str:
        """Provide initial problem statement and Phase 1 prompt."""
        return (
            f"=== System Design Interview: {self.question.title} ===\n"
            f"Target Scale: {self.question.scale_requirements}\n\n"
            f"Current Phase: {self.current_phase}\n"
            f"Prompt: Before drawing diagrams or selecting databases, clarify functional requirements, "
            f"non-functional requirements (SLAs, latency, consistency), and calculate estimated QPS/Storage."
        )

    def advance_phase(self, candidate_input: str) -> dict[str, Any]:
        """Process candidate input for current phase and move to next checkpoint."""
        phase_completed = self.current_phase
        self.current_phase_index = min(self.current_phase_index + 1, len(PHASES) - 1)

        match self.current_phase_index:
            case 1:
                next_prompt = (
                    "Phase 2: High-Level Architecture\n"
                    "Define your core client, API Gateway, primary microservices, and high-level data stores. "
                    "List the main API endpoints (e.g. POST /v1/url, GET /:hash)."
                )
            case 2:
                next_prompt = (
                    f"Phase 3: Component Deep Dive\n"
                    f"Let's focus on key components: {', '.join(self.question.key_components[:2])}.\n"
                    f"What database schema and indexing strategy would you choose? Explain tradeoffs: "
                    f"{self.question.tradeoffs_to_probe[0]}"
                )
            case 3:
                next_prompt = (
                    f"Phase 4: Stress Testing & Failure Modes\n"
                    f"Scenario: {self.question.stress_scenarios[0]}\n"
                    "Where does the architecture buckle first, and what mitigation (caching, queue backpressure, sharding) do you deploy?"
                )
            case _:
                next_prompt = "Interview phases complete. Ready for holistic architectural debrief."

        return {
            "phase_completed": phase_completed,
            "next_phase": self.current_phase,
            "interviewer_prompt": next_prompt,
            "is_final_phase": self.current_phase_index >= len(PHASES) - 1,
        }
