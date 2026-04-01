"""Comparison Agent — real crewai.Agent on Python <=3.12, dataclass fallback otherwise."""

import sys

_USE_CREWAI = False
try:
    if sys.version_info < (3, 13):
        from crewai import Agent
        _USE_CREWAI = True
except Exception:
    pass

if not _USE_CREWAI:
    from agents.product_finder import Agent  # noqa: F811 — our compatible dataclass


def get_comparison_agent():
    kwargs = dict(
        role="Product Comparison Expert",
        goal=(
            "Compare products based on price, performance, features, and brand reputation "
            "to produce a structured, objective comparison."
        ),
        backstory=(
            "You are a seasoned technology reviewer and product analyst who has spent "
            "years comparing consumer electronics for top publications. Known for fair, "
            "data-driven comparisons that cut through marketing noise."
        ),
        verbose=True,
        allow_delegation=False,
        tools=[],
    )
    system_prompt = """You are a Product Comparison Expert specialising in consumer electronics.
Score each product across key criteria and produce a structured comparison.

Respond with ONLY valid JSON:
{
  "criteria": ["Value for Money", "Performance", "Features", "Brand"],
  "scores": {
    "<product name>": {
      "Value for Money": <1-10>,
      "Performance": <1-10>,
      "Features": <1-10>,
      "Brand": <1-10>,
      "overall": <average to 1 decimal>
    }
  },
  "summary": "<2-3 sentence objective comparison>"
}

Be specific and data-driven. Scores should reflect real differences between products.
"""
    if _USE_CREWAI:
        return Agent(**kwargs)
    return Agent(**kwargs, system_prompt=system_prompt)
