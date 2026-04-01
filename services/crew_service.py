"""
Shopping Crew Service — 4-agent sequential pipeline.

On Python <=3.12 (crewai available):
  Uses real crewai.Crew with Process.sequential — true multi-agent orchestration.

On Python 3.13+ (crewai/pydantic_v1 incompatible):
  Emulates the exact same sequential workflow via the OpenAI SDK.
  Each agent is called in order; context is passed forward explicitly.
"""

import json
import logging
import os
import re
import sys

logger = logging.getLogger(__name__)

# ── Detect crewai availability ────────────────────────────────────────────────
_USE_CREWAI = False
try:
    if sys.version_info < (3, 13):
        from crewai import Crew, Process
        _USE_CREWAI = True
        logger.info("crewai detected — using native Crew orchestration")
except Exception:
    pass

if not _USE_CREWAI:
    logger.info("crewai unavailable on Python 3.13+ — using OpenAI native pipeline")


# ── OpenAI helpers (used in fallback path) ───────────────────────────────────
_client = None


def _get_openai_client():
    global _client
    if _client is None:
        from openai import OpenAI
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY is not set. "
                "Copy backend/.env.example → backend/.env and add your key."
            )
        _client = OpenAI(api_key=api_key)
    return _client


def _call_agent(system_prompt: str, user_message: str) -> str:
    """Single agent call via OpenAI with JSON output enforced."""
    model = os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")
    client = _get_openai_client()
    logger.info(f"  → OpenAI call model={model}")
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_message},
        ],
        temperature=0.3,
        response_format={"type": "json_object"},
    )
    return response.choices[0].message.content


def _safe_json(text: str):
    """Robustly parse JSON from an LLM response string."""
    if not isinstance(text, str):
        return {}
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    m = re.search(r"```(?:json)?\s*([\s\S]+?)```", text)
    if m:
        try:
            return json.loads(m.group(1).strip())
        except json.JSONDecodeError:
            pass
    return {"raw": text}


# ── CrewAI path ───────────────────────────────────────────────────────────────
def _run_with_crewai(query: str, candidates: list, products_json: str) -> dict:
    """Use real crewai.Crew with Process.sequential (Python <=3.12 only)."""
    from agents.product_finder import get_product_finder_agent
    from agents.comparison_agent import get_comparison_agent
    from agents.review_analyzer import get_review_analyzer_agent
    from agents.recommendation_agent import get_recommendation_agent
    from tasks.shopping_tasks import (
        create_product_finder_task,
        create_comparison_task,
        create_review_analysis_task,
        create_recommendation_task,
    )

    a1 = get_product_finder_agent()
    a2 = get_comparison_agent()
    a3 = get_review_analyzer_agent()
    a4 = get_recommendation_agent()

    t1 = create_product_finder_task(query, products_json)
    t2 = create_comparison_task(query, context=[t1])
    t3 = create_review_analysis_task(query, context=[t1])
    t4 = create_recommendation_task(query, context=[t1, t2, t3])

    crew = Crew(
        agents=[a1, a2, a3, a4],
        tasks=[t1, t2, t3, t4],
        process=Process.sequential,
        verbose=True,
    )
    result = crew.kickoff()

    outputs = getattr(result, "tasks_output", [])
    products    = _safe_json(outputs[0].raw) if len(outputs) > 0 else {}
    comparison  = _safe_json(outputs[1].raw) if len(outputs) > 1 else {}
    reviews_raw = _safe_json(outputs[2].raw) if len(outputs) > 2 else {}
    reco        = _safe_json(outputs[3].raw) if len(outputs) > 3 else {}

    return {
        "products":       products if isinstance(products, list) else candidates,
        "comparison":     comparison if isinstance(comparison, dict) else {},
        "reviews":        reviews_raw if isinstance(reviews_raw, list) else [],
        "recommendation": reco if isinstance(reco, dict) else {},
    }


# ── OpenAI-native fallback path ───────────────────────────────────────────────
def _run_with_openai(query: str, candidates: list, products_json: str) -> dict:
    """
    Emulate crewai's sequential process using the OpenAI SDK directly.
    Each agent's system_prompt drives a GPT call; context is forwarded explicitly.
    """
    from agents.product_finder import get_product_finder_agent
    from agents.comparison_agent import get_comparison_agent
    from agents.review_analyzer import get_review_analyzer_agent
    from agents.recommendation_agent import get_recommendation_agent

    # Agent 1 — Product Finder
    logger.info("[Agent 1] Product Finder running…")
    a1 = get_product_finder_agent()
    raw1 = _call_agent(
        a1.system_prompt,
        f'User Query: "{query}"\n\nAvailable Products (JSON):\n{products_json}',
    )
    p = _safe_json(raw1)
    products = p.get("products", []) if isinstance(p, dict) and p.get("products") else candidates

    # Agent 2 — Comparison
    logger.info("[Agent 2] Comparison Agent running…")
    a2 = get_comparison_agent()
    products_summary = "\n".join(
        f"- {p_.get('name')} ({p_.get('brand')}): ₹{p_.get('price', 0):,} | "
        f"Rating: {p_.get('rating')} | Features: {', '.join((p_.get('features') or [])[:4])}"
        for p_ in products
    )
    raw2 = _call_agent(
        a2.system_prompt,
        f'User Query: "{query}"\n\nProducts to compare:\n{products_summary}',
    )
    comparison = _safe_json(raw2)
    if not isinstance(comparison, dict):
        comparison = {}

    # Agent 3 — Review Analyzer
    logger.info("[Agent 3] Review Analyzer running…")
    a3 = get_review_analyzer_agent()
    reviews_block = "\n\n".join(
        f"Product: {p_.get('name')} (ID: {p_.get('id', 'N/A')})\nReviews:\n"
        + "\n".join(f"  - {r}" for r in (p_.get("reviews") or []))
        for p_ in products
    )
    raw3 = _call_agent(
        a3.system_prompt,
        f'User Query: "{query}"\n\nProduct Reviews:\n{reviews_block}',
    )
    r3 = _safe_json(raw3)
    reviews = r3.get("reviews", []) if isinstance(r3, dict) else []

    # Agent 4 — Recommendation Advisor
    logger.info("[Agent 4] Recommendation Advisor running…")
    a4 = get_recommendation_agent()
    raw4 = _call_agent(
        a4.system_prompt,
        f'User Query: "{query}"\n\n'
        f'Products:\n' + "\n".join(f"- {p_.get('name')} ({p_.get('brand')}): ₹{p_.get('price',0):,}" for p_ in products) + "\n\n"
        f'Comparison Scores:\n{json.dumps(comparison.get("scores", {}), indent=2)}\n\n'
        f'Review Analysis:\n' + "\n".join(
            f"- {r_.get('product_name')}: {r_.get('sentiment')} — {r_.get('verdict', '')}"
            for r_ in reviews
        ),
    )
    recommendation = _safe_json(raw4)
    if not isinstance(recommendation, dict) or "recommended_product" not in recommendation:
        recommendation = {}

    return {
        "products":       products,
        "comparison":     comparison,
        "reviews":        reviews,
        "recommendation": recommendation,
    }


# ── Public orchestrator ───────────────────────────────────────────────────────
def run_shopping_crew(query: str) -> dict:
    """
    Execute the full 4-agent sequential pipeline.

    Automatically uses crewai.Crew (Python <=3.12) or OpenAI-native (Python 3.13+).
    """
    from services.mock_data import search_products

    logger.info(f"[Crew] Starting pipeline — query: {query!r}")
    logger.info(f"[Crew] Mode: {'crewai native' if _USE_CREWAI else 'OpenAI native (Python 3.13+)'}")

    candidates = search_products(query, max_results=7)
    products_json = json.dumps(candidates, indent=2, ensure_ascii=False)

    if _USE_CREWAI:
        result = _run_with_crewai(query, candidates, products_json)
    else:
        result = _run_with_openai(query, candidates, products_json)

    logger.info("[Crew] Pipeline complete.")
    return result
