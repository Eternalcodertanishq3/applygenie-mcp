"""Curated question bank for coding, behavioral, and system design interviews.

Categorized by topic, company focus, difficulty, and interview type.
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class CodingQuestion:
    id: str
    title: str
    difficulty: str  # "easy", "medium", "hard"
    category: str    # "arrays", "two-pointers", "sliding-window", "trees", "graphs", "dp"
    company_tags: list[str]
    description: str
    examples: list[dict[str, str]]
    hints: list[str]  # 4-rung Socratic hint ladder
    optimal_complexity: dict[str, str]  # time, space


@dataclass
class BehavioralQuestion:
    id: str
    question: str
    competency: str     # "leadership", "ownership", "conflict", "ambiguity", "bias_for_action"
    company_framework: str  # "Amazon LP", "Google Googliness", "Meta Move Fast", "General"
    star_guide: dict[str, str]
    evaluation_criteria: list[str]


@dataclass
class SystemDesignQuestion:
    id: str
    title: str
    difficulty: str
    scale_requirements: str
    key_components: list[str]
    stress_scenarios: list[str]
    tradeoffs_to_probe: list[str]


CODING_QUESTIONS: list[CodingQuestion] = [
    CodingQuestion(
        id="two-sum",
        title="Two Sum",
        difficulty="easy",
        category="arrays",
        company_tags=["Google", "Amazon", "Meta", "Apple", "Microsoft"],
        description=(
            "Given an array of integers `nums` and an integer `target`, return indices of the two "
            "numbers such that they add up to `target`. You may assume that each input would have "
            "exactly one solution, and you may not use the same element twice."
        ),
        examples=[
            {"input": "nums = [2,7,11,15], target = 9", "output": "[0,1]"},
            {"input": "nums = [3,2,4], target = 6", "output": "[1,2]"},
        ],
        hints=[
            "Rung 1 (Clarification): Can you find a way to look up the difference `target - num` faster than scanning the whole array?",
            "Rung 2 (Data Structure): What data structure provides average O(1) time complexity for key lookups?",
            "Rung 3 (Pseudocode): Maintain a hash map of `value -> index`. For each number `x`, check if `target - x` is already in the map.",
            "Rung 4 (Code Walkthrough): Iterate `for i, num in enumerate(nums)`. If `target - num in map`, return `[map[target - num], i]`. Else `map[num] = i`.",
        ],
        optimal_complexity={"time": "O(N)", "space": "O(N)"},
    ),
    CodingQuestion(
        id="lru-cache",
        title="LRU Cache",
        difficulty="medium",
        category="design",
        company_tags=["Amazon", "Google", "Microsoft", "Bloomberg"],
        description=(
            "Design a data structure that follows the constraints of a Least Recently Used (LRU) cache. "
            "Implement the `LRUCache` class with `get(key)` and `put(key, value)` both running in O(1) average time."
        ),
        examples=[
            {"input": "LRUCache(2); put(1,1); put(2,2); get(1); put(3,3); get(2);", "output": "[null, null, null, 1, null, -1]"},
        ],
        hints=[
            "Rung 1: We need fast lookups (O(1)) and fast ordering updates (O(1) insertion/deletion at both ends).",
            "Rung 2: A hash map gives O(1) lookup. What structure gives O(1) removal and insertion when given a node pointer?",
            "Rung 3: Combine a Doubly Linked List with dummy head/tail nodes and a Hash Map storing `key -> ListNode`.",
            "Rung 4: On `get(k)`, move node to front of list. On `put(k, v)`, if key exists update and move; if capacity exceeded, evict node before tail.",
        ],
        optimal_complexity={"time": "O(1) for get and put", "space": "O(capacity)"},
    ),
    CodingQuestion(
        id="trapping-rain-water",
        title="Trapping Rain Water",
        difficulty="hard",
        category="two-pointers",
        company_tags=["Amazon", "Google", "Meta", "Goldman Sachs"],
        description=(
            "Given `n` non-negative integers representing an elevation map where the width of each bar is 1, "
            "compute how much water it can trap after raining."
        ),
        examples=[
            {"input": "height = [0,1,0,2,1,0,1,3,2,1,2,1]", "output": "6"},
        ],
        hints=[
            "Rung 1: At any bar `i`, what determines the water level directly above it? (Think min of max left and max right).",
            "Rung 2: Can we avoid precomputing prefix/suffix arrays with an O(1) space two-pointer approach?",
            "Rung 3: Place pointers `left=0` and `right=len-1`. Track `max_left` and `max_right`. Move the pointer corresponding to the smaller max height.",
            "Rung 4: If `max_left < max_right`, water trapped is `max_left - height[left]`. Advance `left`. Otherwise compute for `right` and decrement `right`.",
        ],
        optimal_complexity={"time": "O(N)", "space": "O(1)"},
    ),
]


BEHAVIORAL_QUESTIONS: list[BehavioralQuestion] = [
    BehavioralQuestion(
        id="conflict-resolution",
        question="Tell me about a time you had a strong technical disagreement with a team member or manager. How did you resolve it?",
        competency="conflict",
        company_framework="Amazon LP (Have Backbone; Disagree and Commit)",
        star_guide={
            "Situation": "Describe the project, the technical dilemma, and the differing viewpoints objectively.",
            "Task": "Clarify the shared project goal and what was at stake for the user or system.",
            "Action": "Focus on data-driven benchmarking, POCs, or architecture spikes rather than personal opinion. Show collaborative discussion.",
            "Result": "State the final decision, whether you agreed or committed, and the measurable impact on the product.",
        },
        evaluation_criteria=[
            "Focus on objective data over personal ego",
            "Active listening and respect for alternatives",
            "Clear demonstration of personal ownership",
            "Disagreement leading to product improvement",
        ],
    ),
    BehavioralQuestion(
        id="ownership-failure",
        question="Describe a situation where a project or feature you were responsible for failed or caused an outage. What happened and what did you learn?",
        competency="ownership",
        company_framework="Amazon LP (Ownership / Earn Trust)",
        star_guide={
            "Situation": "The system context, release, and the failure trigger (e.g. unhandled edge case, load spike).",
            "Task": "Immediate triage responsibility and stakeholder communication.",
            "Action": "Root cause analysis (5 Whys), rollback, hotfix deployment, and post-mortem creation.",
            "Result": "New alerting rules, test cases added, zero recurrence, and psychological safety fostered.",
        },
        evaluation_criteria=[
            "Zero blame-shifting",
            "Fast mitigation before prolonged debate",
            "Concrete preventative systemic fixes",
            "Humility and growth mindset",
        ],
    ),
    BehavioralQuestion(
        id="navigating-ambiguity",
        question="Give an example of a time you were assigned a high-priority task with completely vague or contradictory requirements. How did you proceed?",
        competency="ambiguity",
        company_framework="Google Googliness (Navigating Ambiguity)",
        star_guide={
            "Situation": "Context of incomplete product specs or emerging customer pain points.",
            "Task": "Your responsibility to define the scope and deliver a viable path forward.",
            "Action": "Stakeholder interviews, user journey mapping, progressive prototyping, and phased roadmapping.",
            "Result": "Delivered MVP on time, converted ambiguity into documented engineering specs.",
        },
        evaluation_criteria=[
            "Proactive discovery and user-centric framing",
            "Creation of clarity for the broader team",
            "Bias for action under uncertainty",
        ],
    ),
]


SYSTEM_DESIGN_QUESTIONS: list[SystemDesignQuestion] = [
    SystemDesignQuestion(
        id="url-shortener",
        title="Design a High-Throughput URL Shortener (TinyURL)",
        difficulty="easy",
        scale_requirements="100M URLs created/month, 10B reads/month (100:1 read-to-write ratio), 99.99% availability, <10ms read latency.",
        key_components=[
            "API Gateway / Rate Limiter",
            "Shortening Token Generator (Base62 vs KGS - Key Generation Service)",
            "Distributed Cache (Redis Cluster with LRU)",
            "Storage Layer (NoSQL / DynamoDB or PostgreSQL partitioned by hash)",
        ],
        stress_scenarios=[
            "A viral tweet generates 100,000 reads/sec on a single shortened link (Hotspot key problem).",
            "Database primary node crashes during a heavy batch write window.",
        ],
        tradeoffs_to_probe=[
            "Base62 hash of MD5/MurmurHash vs dedicated Pre-generated Key Service",
            "Consistency vs Availability (CAP Theorem) for URL redirection",
            "Handling link expiration and garbage collection at scale",
        ],
    ),
    SystemDesignQuestion(
        id="distributed-rate-limiter",
        title="Design an API Gateway Distributed Rate Limiter",
        difficulty="medium",
        scale_requirements="500,000 requests/sec across 10 global regions, sub-millisecond decision latency overhead.",
        key_components=[
            "Envoy / NGINX Reverse Proxy",
            "Sliding Window Counter / Token Bucket algorithm",
            "Redis Cluster with Lua scripts for atomic increments",
            "Local in-memory fallback cache to prevent Redis saturation",
        ],
        stress_scenarios=[
            "Redis cluster partition occurs between US-East and EU-West.",
            "Distributed Denial of Service (DDoS) attack hits unauthenticated endpoints.",
        ],
        tradeoffs_to_probe=[
            "Token Bucket vs Leaky Bucket vs Sliding Window Log vs Sliding Window Counter",
            "Centralized Redis vs Local synchronized in-memory rate limiting",
            "Hard throttling (HTTP 429) vs graceful degradation",
        ],
    ),
]


def get_questions_by_type(interview_type: str) -> list[Any]:
    """Return available questions for coding, behavioral, or system design."""
    match interview_type.lower():
        case "coding":
            return CODING_QUESTIONS
        case "behavioral":
            return BEHAVIORAL_QUESTIONS
        case "system_design" | "system-design":
            return SYSTEM_DESIGN_QUESTIONS
        case _:
            return CODING_QUESTIONS
