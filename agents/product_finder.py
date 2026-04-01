"""
agents/product_finder.py

Exports get_product_finder_agent() → a CrewAI-compatible Agent.

On Python <=3.12 with crewai installed: returns a real crewai.Agent.
On Python 3.13+ (crewai/pydantic_v1 incompatible): returns our Agent dataclass
  which mirrors the same interface used by crew_service.py.
"""

import sys
from dataclasses import dataclass

# ── Attempt real crewai import ────────────────────────────────────────────────
_USE_CREWAI = False
try:
    if sys.version_info < (3, 13):
        from crewai import Agent as _CrewAIAgent  # noqa: F401
        _USE_CREWAI = True
except Exception:
    pass

# ── Fallback dataclass (same interface) ──────────────────────────────────────
if not _USE_CREWAI:
    @dataclass
    class Agent:
        """CrewAI-compatible Agent dataclass for Python 3.13+."""
        role: str
        goal: str
        backstory: str
        system_prompt: str = ""
        verbose: bool = True
        allow_delegation: bool = False
        tools: list = None

        def __post_init__(self):
            if self.tools is None:
                self.tools = []

# ── Factory ───────────────────────────────────────────────────────────────────
def get_product_finder_agent():
    kwargs = dict(
        role="Product Finder Specialist",
        goal=(
            "Extract user requirements (budget, category, features) "
            "and find 5–7 matching products from the product catalog."
        ),
        backstory=(
            "You are an expert e-commerce product analyst with deep knowledge of "
            "consumer electronics, gadgets, and lifestyle products. You excel at "
            "understanding user needs and matching them to the right products."
        ),
        verbose=True,
        allow_delegation=False,
        tools=[],
    )
    system_prompt = """You are a Product Finder Specialist for an Indian e-commerce platform.
Analyse the user query and the available product catalog, then select the 5–7 most relevant products.

Respond with ONLY valid JSON:
{
  "products": [
    {
      "id": "<string>",
      "name": "<string>",
      "brand": "<string>",
      "price": <number in INR>,
      "category": "<string>",
      "rating": <number 1-5>,
      "features": ["<feature>", ...],
      "use_cases": ["<use_case>", ...]
    }
  ]
}

Rules:
- Only select products matching the user's stated budget, category, and use-case.
- Do NOT fabricate products. Use only the products provided in the catalog.
- Budget: if user says "under ₹1 lakh", only include products priced ≤ 100000.
"""

    if _USE_CREWAI:
        return _CrewAIAgent(**kwargs)
    return Agent(**kwargs, system_prompt=system_prompt)
