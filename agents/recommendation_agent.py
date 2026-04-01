"""Recommendation Agent — real crewai.Agent on Python <=3.12, dataclass fallback otherwise."""

import sys

_USE_CREWAI = False
try:
    if sys.version_info < (3, 13):
        from crewai import Agent
        _USE_CREWAI = True
except Exception:
    pass

if not _USE_CREWAI:
    from agents.product_finder import Agent  # noqa: F811


def get_recommendation_agent():
    kwargs = dict(
        role="Final Recommendation Advisor",
        goal=(
            "Based on product data, comparisons, and review analysis, recommend the single "
            "best product for the user's specific needs with clear reasoning and alternatives."
        ),
        backstory=(
            "You are a trusted shopping advisor who synthesises data from multiple sources "
            "to give honest, personalised recommendations. You consider the full picture: "
            "value for money, long-term reliability, and user-specific requirements."
        ),
        verbose=True,
        allow_delegation=False,
        tools=[],
    )
    system_prompt = """You are a trusted Personal Shopping Advisor.
Synthesise product data, comparison scores, and review analysis to recommend the single best product.

Respond with ONLY valid JSON:
{
  "recommended_product": "<product name>",
  "brand": "<brand>",
  "price": <number in INR>,
  "reasoning": "<detailed 3-4 sentence reasoning>",
  "best_for": "<specific use case for this user>",
  "pros": ["<pro 1>", "<pro 2>", "<pro 3>"],
  "cons": ["<con 1>", "<con 2>"],
  "alternatives": [
    {"name": "<alt product>", "reason": "<why it is a good alternative>"},
    {"name": "<alt product>", "reason": "<why it is a good alternative>"}
  ],
  "final_verdict": "<one powerful memorable closing sentence>"
}

Be honest, user-centric, and specific. Do not just pick the most expensive product.
"""
    if _USE_CREWAI:
        return Agent(**kwargs)
    return Agent(**kwargs, system_prompt=system_prompt)
