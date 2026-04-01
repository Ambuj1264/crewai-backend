"""
FastAPI main application for the AI-powered E-commerce Shopping Assistant.
"""

import logging
import os
import time
from contextlib import asynccontextmanager
from typing import Any

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Load environment variables from .env
load_dotenv()

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# App lifecycle
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Shopping Assistant API starting up…")
    yield
    logger.info("🛑 Shopping Assistant API shutting down…")


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(
    title="AI Shopping Assistant API",
    description="Multi-agent CrewAI powered e-commerce recommendation engine",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS – allow the Vite dev server (port 5173) and any localhost port
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------
class RecommendRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=5,
        max_length=500,
        example="Best laptop under ₹1 lakh for coding and gaming",
    )


class RecommendResponse(BaseModel):
    query: str
    products: list[Any]
    comparison: dict[str, Any]
    reviews: list[Any]
    recommendation: dict[str, Any]
    elapsed_seconds: float


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "message": "AI Shopping Assistant API is running 🛒"}


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy", "version": "1.0.0"}


@app.post("/recommend", response_model=RecommendResponse, tags=["Shopping"])
async def recommend(body: RecommendRequest):
    """
    Run the 4-agent CrewAI pipeline and return structured shopping recommendations.
    """
    logger.info(f"POST /recommend — query={body.query!r}")
    start = time.perf_counter()

    try:
        from services.crew_service import run_shopping_crew

        result = run_shopping_crew(body.query)
    except Exception as exc:
        logger.exception("CrewAI pipeline failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    elapsed = round(time.perf_counter() - start, 2)
    logger.info(f"Pipeline completed in {elapsed}s")

    return RecommendResponse(
        query=body.query,
        products=result.get("products", []),
        comparison=result.get("comparison", {}),
        reviews=result.get("reviews", []),
        recommendation=result.get("recommendation", {}),
        elapsed_seconds=elapsed,
    )


# ---------------------------------------------------------------------------
# Dev entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True,
        log_level="info",
    )
