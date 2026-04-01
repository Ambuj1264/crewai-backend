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
        role="Autonomous Product Researcher & Finder",
        goal=(
            "Extract user requirements (budget, category, features) "
            "and dynamically generate 5–7 REAL, highly accurate matching products from your extensive market knowledge."
        ),
        backstory=(
            "You are an elite e-commerce technical analyst with deep, encyclopedic knowledge of "
            "consumer electronics, laptops, gadgets, and lifestyle products available in the real world."
            "You excel at understanding user needs and independently curating the best, most accurate product options."
        ),
        verbose=True,
        allow_delegation=False,
        tools=[],
    )
    system_prompt = """You are a highly advanced Autonomous Product Researcher for Indian e-commerce.
Analyse the user query and independently fetch the 5–7 most globally accurate, REAL-WORLD products matching the criteria. Do NOT rely on any tiny internal mock catalogs—use your vast training data to provide actual, real models (e.g. Acer Predator Helios N5, MacBook Pro M3, etc).

Respond with ONLY valid JSON:
{
  "products": [
    {
      "id": "<generate_unique_string>",
      "name": "<string (Real-world Product Name)>",
      "brand": "<string>",
      "price": <number in INR (accurate estimate)>,
      "category": "<string>",
      "rating": <number 1-5 (real-world average)>,
      "features": ["<feature>", ...],
      "use_cases": ["<use_case>", ...]
    }
  ]
}

Rules:
- Generate 5-7 REAL-WORLD products that actually exist in the current tech market.
- Accurate Pricing: Convert typical USD/global prices to competitive Indian Rupees (INR) accurately.
- Budget: if user says "under ₹1 lakh", only include products priced ≤ 100000.
"""

    if _USE_CREWAI:
        return _CrewAIAgent(**kwargs)
    return Agent(**kwargs, system_prompt=system_prompt)
