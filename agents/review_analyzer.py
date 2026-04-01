"""Review Analyzer Agent — real crewai.Agent on Python <=3.12, dataclass fallback otherwise."""

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


def get_review_analyzer_agent():
    kwargs = dict(
        role="Customer Review Analyst",
        goal=(
            "Analyse customer reviews for each product and extract positives, negatives, "
            "and overall sentiment to help users make informed decisions."
        ),
        backstory=(
            "You are an expert in natural language processing and customer sentiment analysis. "
            "You have analysed millions of product reviews and quickly identify recurring "
            "themes, genuine pain points, and standout features users rave about."
        ),
        verbose=True,
        allow_delegation=False,
        tools=[],
    )
    system_prompt = """You are a Customer Review Analyst specialising in sentiment analysis.
For each product, analyse the reviews and extract structured insights.

Respond with ONLY valid JSON:
{
  "reviews": [
    {
      "product_id": "<id>",
      "product_name": "<name>",
      "sentiment": "positive" | "negative" | "mixed" | "neutral",
      "sentiment_score": <0.0 to 1.0>,
      "positives": ["<key positive>", ...],
      "negatives": ["<key negative>", ...],
      "verdict": "<one concise verdict sentence>"
    }
  ]
}

Base your analysis only on the review text provided. Be honest about negatives.
"""
    if _USE_CREWAI:
        return Agent(**kwargs)
    return Agent(**kwargs, system_prompt=system_prompt)
