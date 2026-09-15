"""Coding interview simulator and Socratic guidance engine.

Manages interactive coding challenges, progressive hint ladders, and complexity checks.
"""

from typing import Any
from applygenie.interview.question_bank import CODING_QUESTIONS, CodingQuestion


class CodingSimulator:
    """Manages an active coding interview question session."""

    def __init__(self, question: CodingQuestion) -> None:
        self.question = question
        self.hint_level = 0
        self.max_hints = len(question.hints)

    def get_prompt(self) -> str:
        """Format the initial problem prompt for the candidate."""
        examples_str = "\n".join(
            f"Example {i+1}:\n  Input: {ex['input']}\n  Output: {ex['output']}"
            for i, ex in enumerate(self.question.examples)
        )
        return (
            f"=== Technical Coding Challenge: {self.question.title} ({self.question.difficulty.upper()}) ===\n"
            f"Companies: {', '.join(self.question.company_tags)}\n\n"
            f"{self.question.description}\n\n"
            f"{examples_str}\n\n"
            f"Instructions:\n"
            f"1. Explain your thought process and proposed Big-O time/space complexity before writing code.\n"
            f"2. You can request progressive hints at any point if you get stuck."
        )

    def get_next_hint(self) -> dict[str, Any]:
        """Advance the hint ladder and provide the next rung."""
        if self.hint_level >= self.max_hints:
            return {
                "hint_level": self.hint_level,
                "hint": "You have exhausted all available hints. Optimal complexity is "
                        f"{self.question.optimal_complexity['time']} time and "
                        f"{self.question.optimal_complexity['space']} space.",
                "has_more": False,
            }

        hint_text = self.question.hints[self.hint_level]
        self.hint_level += 1
        return {
            "hint_level": self.hint_level,
            "hint": hint_text,
            "has_more": self.hint_level < self.max_hints,
        }

    def evaluate_solution(self, solution_code: str, complexity_explanation: str) -> dict[str, Any]:
        """Evaluate candidate code and return heuristic breakdown."""
        code_length = len(solution_code.strip())
        has_docstring = '"""' in solution_code or "'''" in solution_code
        has_type_hints = "->" in solution_code or ":" in solution_code

        # Check optimal complexity mention
        time_mentioned = any(
            comp in complexity_explanation.lower()
            for comp in ["o(n)", "o(1)", "o(log n)", "o(n log n)", "linear", "constant"]
        )

        return {
            "status": "ready_for_ai_review",
            "heuristics": {
                "code_length": code_length,
                "has_docstrings": has_docstring,
                "has_type_hints": has_type_hints,
                "complexity_analyzed": time_mentioned,
                "hints_used": self.hint_level,
            },
            "optimal_target": self.question.optimal_complexity,
            "next_step": "Submit to LLM-as-a-judge for full code correctness & clarity score.",
        }
