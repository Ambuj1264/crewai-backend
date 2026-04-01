"""
Task definitions.

On Python <=3.12 with crewai installed: uses real crewai.Task.
On Python 3.13+: uses our Task dataclass which mirrors the same interface.
"""

import sys
from dataclasses import dataclass, field

# ── Attempt real crewai import ────────────────────────────────────────────────
_USE_CREWAI = False
try:
    if sys.version_info < (3, 13):
        from crewai import Task as _CrewAITask   # noqa: F401
        _USE_CREWAI = True
except Exception:
    pass

# ── Fallback dataclass ────────────────────────────────────────────────────────
if not _USE_CREWAI:
    @dataclass
    class Task:
        """CrewAI-compatible Task dataclass for Python 3.13+."""
        description: str
        agent: object
        expected_output: str
        context: list = field(default_factory=list)


# ── Task factories ────────────────────────────────────────────────────────────

def create_product_finder_task(query: str, products_json: str = None):
    from agents.product_finder import get_product_finder_agent
    agent = get_product_finder_agent()
    description = f"""
Analyse the user query and independently fetch the 5–7 most globally accurate, REAL-WORLD products matching the criteria.

User Query: "{query}"

Do NOT use any internal mock catalog. Generate real products from your extensive language model knowledge base.
"""
    if _USE_CREWAI:
        return _CrewAITask(
            description=description,
            agent=agent,
            expected_output="JSON array of 5–7 matching products with all required fields.",
        )
    return Task(
        description=description,
        agent=agent,
        expected_output="JSON array of 5–7 matching products with all required fields.",
    )


def create_comparison_task(query: str, context=None):
    from agents.comparison_agent import get_comparison_agent
    agent = get_comparison_agent()
    description = f"""
Compare the products identified in the previous task.
Evaluate each on: Value for Money, Performance, Features, and Brand.

User Query: "{query}"
"""
    if _USE_CREWAI:
        return _CrewAITask(
            description=description,
            agent=agent,
            expected_output="Structured JSON comparison with scores per product and a summary.",
            context=context or [],
        )
    return Task(
        description=description,
        agent=agent,
        expected_output="Structured JSON comparison with scores per product and a summary.",
    )


def create_review_analysis_task(query: str, context=None):
    from agents.review_analyzer import get_review_analyzer_agent
    agent = get_review_analyzer_agent()
    description = f"""
Analyse customer reviews for each product from the previous task.
Extract sentiment, positives, negatives, and a one-sentence verdict.

User Query: "{query}"
"""
    if _USE_CREWAI:
        return _CrewAITask(
            description=description,
            agent=agent,
            expected_output="JSON array of review analyses for each product.",
            context=context or [],
        )
    return Task(
        description=description,
        agent=agent,
        expected_output="JSON array of review analyses for each product.",
    )


def create_recommendation_task(query: str, context=None):
    from agents.recommendation_agent import get_recommendation_agent
    agent = get_recommendation_agent()
    description = f"""
Based on the products, comparison scores, and review analyses from previous tasks,
recommend the single best product for this specific user.

User Query: "{query}"
"""
    if _USE_CREWAI:
        return _CrewAITask(
            description=description,
            agent=agent,
            expected_output="JSON recommendation object with reasoning, pros/cons, and alternatives.",
            context=context or [],
        )
    return Task(
        description=description,
        agent=agent,
        expected_output="JSON recommendation object with reasoning, pros/cons, and alternatives.",
    )
