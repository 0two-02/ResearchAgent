"""
ResearchPilot AI - Chat API Route
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database.session import get_db
from backend.database.models import Paper, PaperAnalysis
from backend.schemas.schemas import ChatRequest, ChatResponse
from backend.services.research_agents.agents import chat_agent
from backend.api.research_routes import _paper_to_dict

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def research_chat(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Conversational research assistant with RAG-powered responses.
    Grounded in retrieved paper evidence.
    """
    papers = []
    for pid in (request.paper_ids or []):
        p = db.query(Paper).filter(Paper.id == pid).first()
        if p:
            papers.append(_paper_to_dict(p))

    # If no specific papers, load recent papers
    if not papers:
        recent = db.query(Paper).order_by(Paper.citation_count.desc()).limit(10).all()
        papers = [_paper_to_dict(p) for p in recent]

    history = [{"role": m.role, "content": m.content} for m in (request.history or [])]

    result = await chat_agent(
        message=request.message,
        paper_ids=request.paper_ids or [],
        papers=papers,
        history=history,
    )

    return ChatResponse(
        response=result["response"],
        sources=result.get("sources", []),
        evidence=result.get("evidence"),
    )
