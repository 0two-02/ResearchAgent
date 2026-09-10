"""
ResearchPilot AI - FastAPI Application Entry Point
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.config import CORS_ORIGINS, DEBUG, DEMO_MODE
from backend.database.session import create_tables
from backend.api.research_routes import router as research_router
from backend.api.document_routes import router as document_router
from backend.api.chat_routes import router as chat_router


# ─── Lifespan ─────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(application: FastAPI):
    """Application startup and shutdown logic."""
    # Startup
    create_tables()
    print("[ResearchPilot] Database tables created.")
    print(f"[ResearchPilot] DEMO_MODE: {DEMO_MODE}")

    if DEMO_MODE:
        from backend.database.session import SessionLocal
        from backend.api.research_routes import _save_paper
        from data.demo.demo_data import DEMO_PAPERS
        db = SessionLocal()
        try:
            from backend.database.models import Paper
            if db.query(Paper).count() == 0:
                for p in DEMO_PAPERS:
                    _save_paper(db, p)
                db.commit()
                print(f"[ResearchPilot] Seeded {len(DEMO_PAPERS)} demo papers.")
        finally:
            db.close()

    yield
    # Shutdown: nothing to clean up for SQLite/ChromaDB


# ─── App creation ─────────────────────────────────────────────────────────────

app = FastAPI(
    title="ResearchPilot AI",
    description="Intelligent Research Companion – From scattered research to actionable knowledge.",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ──────────────────────────────────────────────────────────────────

app.include_router(research_router, prefix="/api", tags=["Research"])
app.include_router(document_router, prefix="/api", tags=["Documents"])
app.include_router(chat_router, prefix="/api", tags=["Chat"])


# ─── Health & Info ────────────────────────────────────────────────────────────

@app.get("/api/health")
def health():
    return {
        "status": "healthy",
        "app": "ResearchPilot AI",
        "version": "1.0.0",
        "demo_mode": DEMO_MODE,
    }


@app.get("/api/info")
def info():
    from backend.config import IBM_AVAILABLE, GROQ_AVAILABLE
    from backend.services.ibm.watsonx_client import watsonx
    return {
        "app": "ResearchPilot AI",
        "tagline": "From scattered research to actionable knowledge.",
        "ibm_connected": IBM_AVAILABLE,
        "groq_connected": GROQ_AVAILABLE,
        "llm_provider": watsonx.active_provider,
        "demo_mode": DEMO_MODE,
        "academic_sources": ["arxiv", "semantic_scholar", "crossref", "openalex"],
        "agents": [
            "Research Planner Agent",
            "Research Discovery Agent",
            "Paper Analysis Agent",
            "Literature Review Agent",
            "Research Gap Agent",
            "Trend Prediction Agent",
            "Citation Analysis Agent",
            "Research Recommendation Agent",
        ],
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal error: {str(exc)}", "type": type(exc).__name__},
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=DEBUG)
