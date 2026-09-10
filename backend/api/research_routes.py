"""
ResearchPilot AI - Research API Routes
"""
import json
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.database.session import get_db
from backend.database.models import (
    Paper, Author, Topic, ResearchQuery, ResearchResult,
    PaperAnalysis, ResearchGap, ResearchRecommendation, LiteratureReview
)
from backend.schemas.schemas import (
    ResearchSearchRequest, ResearchSearchResponse, PaperOut, PaperAnalyzeRequest,
    LiteratureReviewRequest, LiteratureReviewOut, ResearchGapRequest, ResearchGapOut,
    TrendRequest, TrendResponse, RecommendationRequest, RecommendationsResponse,
    CompareRequest, CompareResponse, ChatRequest, ChatResponse, DashboardStats
)
from backend.services.academic_sources.aggregator import search_all_sources
from backend.services.research_agents.agents import (
    research_planner_agent, paper_analysis_agent, literature_review_agent,
    research_gap_agent, trend_prediction_agent, citation_analysis_agent,
    research_recommendation_agent, chat_agent, comparison_agent
)
from backend.config import DEMO_MODE
from data.demo.demo_data import DEMO_PAPERS, DEMO_RESEARCH_PLAN, DEMO_GAPS, DEMO_SUMMARY

router = APIRouter()


def _get_or_create_author(db: Session, name: str) -> Author:
    author = db.query(Author).filter(Author.name == name).first()
    if not author:
        author = Author(name=name)
        db.add(author)
        db.flush()
    return author


def _get_or_create_topic(db: Session, name: str) -> Topic:
    topic = db.query(Topic).filter(Topic.name == name).first()
    if not topic:
        topic = Topic(name=name)
        db.add(topic)
        db.flush()
    return topic


def _save_paper(db: Session, paper_data: Dict) -> Paper:
    """Save a paper to the database, avoiding duplicates."""
    existing = None
    if paper_data.get("doi"):
        existing = db.query(Paper).filter(Paper.doi == paper_data["doi"]).first()
    if not existing and paper_data.get("source_id"):
        existing = db.query(Paper).filter(
            Paper.source == paper_data.get("source"),
            Paper.source_id == paper_data["source_id"]
        ).first()
    if existing:
        return existing

    paper = Paper(
        title=paper_data.get("title", "Unknown"),
        abstract=paper_data.get("abstract"),
        year=paper_data.get("year"),
        doi=paper_data.get("doi"),
        url=paper_data.get("url"),
        source=paper_data.get("source"),
        source_id=paper_data.get("source_id"),
        citation_count=paper_data.get("citation_count", 0),
        keywords=paper_data.get("keywords", []),
        research_field=paper_data.get("research_field"),
        pdf_url=paper_data.get("pdf_url"),
        journal=paper_data.get("journal"),
        venue=paper_data.get("venue"),
        is_demo=paper_data.get("is_demo", False),
    )
    # Add to session first so association table inserts work correctly
    db.add(paper)
    db.flush()

    for author_name in (paper_data.get("authors") or [])[:10]:
        if isinstance(author_name, str):
            author = _get_or_create_author(db, author_name)
            if author not in paper.authors:
                paper.authors.append(author)
        elif isinstance(author_name, dict):
            name = author_name.get("name", "")
            if name:
                author = _get_or_create_author(db, name)
                if author not in paper.authors:
                    paper.authors.append(author)

    if paper_data.get("research_field"):
        topic = _get_or_create_topic(db, paper_data["research_field"])
        if topic not in paper.topics:
            paper.topics.append(topic)

    db.flush()
    return paper


def _paper_to_dict(paper: Paper) -> Dict:
    return {
        "id": paper.id,
        "title": paper.title,
        "abstract": paper.abstract,
        "year": paper.year,
        "doi": paper.doi,
        "url": paper.url,
        "source": paper.source,
        "source_id": paper.source_id,
        "citation_count": paper.citation_count,
        "keywords": paper.keywords or [],
        "research_field": paper.research_field,
        "pdf_url": paper.pdf_url,
        "journal": paper.journal,
        "is_demo": paper.is_demo,
        "authors": [{"name": a.name, "affiliation": a.affiliation} for a in paper.authors],
    }


# ─── Research Search ──────────────────────────────────────────────────────────

@router.post("/research/search", response_model=ResearchSearchResponse)
async def research_search(request: ResearchSearchRequest, db: Session = Depends(get_db)):
    """
    Full agentic research search:
    1. Research Planner Agent creates a research plan
    2. Academic sources are searched in parallel
    3. Results are deduplicated and ranked
    4. Papers saved to database
    """
    use_demo = request.demo_mode or DEMO_MODE

    # Agent 1: Research Planner
    if use_demo:
        research_plan = DEMO_RESEARCH_PLAN
    else:
        research_plan = await research_planner_agent(request.query)

    # Save query
    query_obj = ResearchQuery(
        query_text=request.query,
        research_plan=research_plan,
        status="searching",
    )
    db.add(query_obj)
    db.commit()
    db.refresh(query_obj)

    # Agent 2: Research Discovery
    if use_demo:
        raw_papers = DEMO_PAPERS
        sources_searched = ["demo"]
        total = len(raw_papers)
    else:
        result = await search_all_sources(
            query=request.query,
            sources=request.sources,
            max_results_per_source=max(request.max_results // len(request.sources), 5),
            year_from=request.year_from,
            year_to=request.year_to,
        )
        raw_papers_objs = result["papers"][: request.max_results]
        sources_searched = result["sources_searched"]
        total = result["total_found"]
        raw_papers = [vars(p) for p in raw_papers_objs]

    # Save papers and create results
    saved_papers = []
    for paper_data in raw_papers:
        paper = _save_paper(db, paper_data)
        saved_papers.append(paper)
        rr = ResearchResult(
            query_id=query_obj.id,
            paper_id=paper.id,
            relevance_score=paper_data.get("relevance_score", 0.0),
            rank=len(saved_papers),
        )
        db.add(rr)

    query_obj.status = "completed"
    db.commit()

    # Generate summary using AI
    papers_for_ai = [_paper_to_dict(p) for p in saved_papers[:10]]
    if use_demo:
        summary = DEMO_SUMMARY
    else:
        from backend.services.ibm.watsonx_client import watsonx
        from backend.services.academic_sources.aggregator import _paper_context
        from backend.services.academic_sources.base import StandardPaper
        paper_ctx = _paper_context(papers_for_ai)
        summary_prompt = f"Summarize these research papers in 3-4 sentences for the query: '{request.query}'\n\nPapers:\n{paper_ctx}\n\nSummary:"
        summary = await watsonx.generate(summary_prompt)

    paper_outs = [PaperOut.model_validate(p) for p in saved_papers]

    return ResearchSearchResponse(
        query_id=query_obj.id,
        query=request.query,
        research_plan=research_plan,
        papers=paper_outs,
        total_found=total,
        summary=summary,
        sources_searched=sources_searched,
        demo_mode=use_demo,
    )


# ─── Paper Analysis ───────────────────────────────────────────────────────────

@router.post("/research/analyze")
async def analyze_papers(request: PaperAnalyzeRequest, db: Session = Depends(get_db)):
    """Agent 3: Analyze selected papers."""
    results = []
    for paper_id in request.paper_ids:
        paper = db.query(Paper).filter(Paper.id == paper_id).first()
        if not paper:
            continue

        # Check for existing analysis
        existing = db.query(PaperAnalysis).filter(PaperAnalysis.paper_id == paper_id).first()
        if existing:
            results.append({"paper_id": paper_id, "analysis": {
                "problem_statement": existing.problem_statement,
                "objective": existing.objective,
                "methodology": existing.methodology,
                "dataset": existing.dataset,
                "results": existing.results,
                "limitations": existing.limitations,
                "key_findings": existing.key_findings,
                "future_work": existing.future_work,
                "summary": existing.summary,
            }})
            continue

        analysis_data = await paper_analysis_agent(_paper_to_dict(paper))
        analysis = PaperAnalysis(
            paper_id=paper_id,
            problem_statement=analysis_data.get("problem_statement"),
            objective=analysis_data.get("objective"),
            methodology=analysis_data.get("methodology"),
            dataset=analysis_data.get("dataset"),
            results=analysis_data.get("results"),
            limitations=analysis_data.get("limitations"),
            key_findings=analysis_data.get("key_findings"),
            future_work=analysis_data.get("future_work"),
            summary=analysis_data.get("summary"),
            raw_json=analysis_data,
        )
        db.add(analysis)
        db.commit()
        results.append({"paper_id": paper_id, "analysis": analysis_data})

    return {"analyses": results}


# ─── Literature Review ────────────────────────────────────────────────────────

@router.post("/research/literature-review")
async def generate_literature_review(request: LiteratureReviewRequest, db: Session = Depends(get_db)):
    """Agent 4: Generate structured literature review."""
    papers = []
    for pid in request.paper_ids:
        p = db.query(Paper).filter(Paper.id == pid).first()
        if p:
            papers.append(_paper_to_dict(p))

    if not papers:
        raise HTTPException(status_code=400, detail="No valid papers found.")

    topic = request.topic or "Research Analysis"
    review_text = await literature_review_agent(papers, topic)

    # Parse sections from markdown
    sections = _parse_review_sections(review_text)

    review = LiteratureReview(
        query_id=request.query_id,
        title=f"Literature Review: {topic}",
        introduction=sections.get("introduction"),
        existing_research=sections.get("existing_research"),
        major_approaches=sections.get("major_approaches"),
        comparison_of_methods=sections.get("comparison"),
        important_findings=sections.get("findings"),
        limitations=sections.get("limitations"),
        research_gaps=sections.get("gaps"),
        emerging_trends=sections.get("trends"),
        future_directions=sections.get("future"),
        references=[{"paper_id": pid, "title": p.get("title")} for pid, p in zip(request.paper_ids, papers)],
    )
    db.add(review)
    db.commit()
    db.refresh(review)

    return {
        "id": review.id,
        "title": review.title,
        "full_text": review_text,
        "sections": sections,
        "references": review.references,
    }


def _parse_review_sections(text: str) -> Dict[str, str]:
    """Extract sections from markdown literature review."""
    import re
    sections = {}
    patterns = {
        "introduction": r"(?:##?\s*introduction)(.*?)(?=##|\Z)",
        "existing_research": r"(?:##?\s*existing research)(.*?)(?=##|\Z)",
        "major_approaches": r"(?:##?\s*major approaches)(.*?)(?=##|\Z)",
        "comparison": r"(?:##?\s*comparison)(.*?)(?=##|\Z)",
        "findings": r"(?:##?\s*(?:important )?findings)(.*?)(?=##|\Z)",
        "limitations": r"(?:##?\s*limitations)(.*?)(?=##|\Z)",
        "gaps": r"(?:##?\s*research gaps)(.*?)(?=##|\Z)",
        "trends": r"(?:##?\s*emerging trends)(.*?)(?=##|\Z)",
        "future": r"(?:##?\s*future)(.*?)(?=##|\Z)",
    }
    for key, pattern in patterns.items():
        m = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if m:
            sections[key] = m.group(1).strip()[:3000]
    return sections


# ─── Research Gaps ────────────────────────────────────────────────────────────

@router.post("/research/gaps")
async def identify_gaps(request: ResearchGapRequest, db: Session = Depends(get_db)):
    """Agent 5: Identify research gaps."""
    papers = []
    for pid in request.paper_ids:
        p = db.query(Paper).filter(Paper.id == pid).first()
        if p:
            papers.append(_paper_to_dict(p))

    if not papers:
        if DEMO_MODE:
            return DEMO_GAPS
        raise HTTPException(status_code=400, detail="No valid papers found.")

    gaps_data = await research_gap_agent(papers)

    # Save to database
    for i, gap_text in enumerate(gaps_data.get("research_gaps", [])):
        evidence_list = gaps_data.get("evidence", [])
        importance_list = gaps_data.get("importance", [])
        questions_list = gaps_data.get("possible_research_questions", [])
        gap = ResearchGap(
            query_id=request.query_id,
            gap_description=gap_text,
            evidence=evidence_list[i] if i < len(evidence_list) else None,
            importance=importance_list[i] if i < len(importance_list) else "medium",
            possible_research_questions=questions_list[i:i+1] if i < len(questions_list) else [],
        )
        db.add(gap)
    db.commit()

    return gaps_data


# ─── Trends ───────────────────────────────────────────────────────────────────

@router.post("/research/trends")
async def analyze_trends(request: TrendRequest, db: Session = Depends(get_db)):
    """Agent 6: Analyze research trends."""
    papers = []
    for pid in request.paper_ids:
        p = db.query(Paper).filter(Paper.id == pid).first()
        if p:
            papers.append(_paper_to_dict(p))

    if not papers:
        raise HTTPException(status_code=400, detail="No valid papers found.")

    return await trend_prediction_agent(papers)


# ─── Recommendations ──────────────────────────────────────────────────────────

@router.post("/research/recommendations")
async def get_recommendations(request: RecommendationRequest, db: Session = Depends(get_db)):
    """Agent 8: Generate research recommendations."""
    papers = []
    for pid in request.paper_ids:
        p = db.query(Paper).filter(Paper.id == pid).first()
        if p:
            papers.append(_paper_to_dict(p))

    if not papers:
        raise HTTPException(status_code=400, detail="No valid papers found.")

    recs = await research_recommendation_agent(papers, request.research_topic or "")

    for rec in recs:
        db_rec = ResearchRecommendation(
            query_id=request.query_id,
            research_idea=rec.get("research_idea", ""),
            why_it_matters=rec.get("why_it_matters"),
            existing_evidence=rec.get("existing_evidence"),
            research_gap=rec.get("research_gap"),
            suggested_methodology=rec.get("suggested_methodology"),
            possible_dataset=rec.get("possible_dataset"),
            expected_contribution=rec.get("expected_contribution"),
            difficulty_level=rec.get("difficulty_level", "medium"),
        )
        db.add(db_rec)
    db.commit()

    return {"recommendations": recs, "topic": request.research_topic}


# ─── Paper Comparison ─────────────────────────────────────────────────────────

@router.post("/research/compare")
async def compare_papers(request: CompareRequest, db: Session = Depends(get_db)):
    """Compare multiple papers with AI-generated summary."""
    papers = []
    analyses = []
    for pid in request.paper_ids:
        p = db.query(Paper).filter(Paper.id == pid).first()
        if p:
            papers.append(_paper_to_dict(p))
            analysis = db.query(PaperAnalysis).filter(PaperAnalysis.paper_id == pid).first()
            analyses.append(analysis.raw_json if analysis else {})

    if len(papers) < 2:
        raise HTTPException(status_code=400, detail="At least 2 papers required for comparison.")

    comparison_table = []
    fields = ["methodology", "dataset", "results", "limitations", "key_findings", "future_work"]
    for field in fields:
        row = {"feature": field.replace("_", " ").title()}
        for i, (p, a) in enumerate(zip(papers, analyses)):
            row[f"paper_{i+1}"] = (a or {}).get(field) or p.get("abstract", "")[:100]
        comparison_table.append(row)

    ai_summary = await comparison_agent(papers, analyses)

    return {
        "papers": [PaperOut.model_validate(p) for p in papers],
        "comparison_table": comparison_table,
        "ai_summary": ai_summary,
    }


# ─── Papers List ──────────────────────────────────────────────────────────────

@router.get("/papers")
def list_papers(
    skip: int = 0,
    limit: int = 50,
    source: Optional[str] = None,
    year_from: Optional[int] = None,
    year_to: Optional[int] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Paper)
    if source:
        query = query.filter(Paper.source == source)
    if year_from:
        query = query.filter(Paper.year >= year_from)
    if year_to:
        query = query.filter(Paper.year <= year_to)

    total = query.count()
    papers = query.order_by(Paper.citation_count.desc()).offset(skip).limit(limit).all()
    return {"papers": [PaperOut.model_validate(p) for p in papers], "total": total}


@router.get("/papers/{paper_id}")
def get_paper(paper_id: int, db: Session = Depends(get_db)):
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found.")
    analysis = db.query(PaperAnalysis).filter(PaperAnalysis.paper_id == paper_id).first()
    paper_dict = _paper_to_dict(paper)
    paper_dict["analysis"] = analysis.raw_json if analysis else None
    return paper_dict


# ─── Dashboard ────────────────────────────────────────────────────────────────

@router.get("/dashboard")
def get_dashboard(db: Session = Depends(get_db)):
    total_papers = db.query(Paper).count()
    total_topics = db.query(Topic).count()
    total_queries = db.query(ResearchQuery).count()
    total_gaps = db.query(ResearchGap).count()

    # Most cited paper
    most_cited = db.query(Paper).order_by(Paper.citation_count.desc()).first()

    # Year distribution
    from sqlalchemy import func
    year_dist = db.query(Paper.year, func.count(Paper.id)).filter(Paper.year.isnot(None)).group_by(Paper.year).all()
    yearly_distribution = {str(y): c for y, c in year_dist if y}

    # Top keywords
    all_keywords: Dict[str, int] = {}
    for paper in db.query(Paper).filter(Paper.keywords.isnot(None)).limit(200).all():
        for kw in (paper.keywords or []):
            all_keywords[kw] = all_keywords.get(kw, 0) + 1
    top_keywords = sorted(all_keywords.items(), key=lambda x: x[1], reverse=True)[:15]

    # Topic clusters
    topics = db.query(Topic).all()
    topic_clusters = [{"name": t.name, "paper_count": len(t.papers)} for t in topics[:20]]

    return {
        "total_papers": total_papers,
        "total_topics": total_topics,
        "total_queries": total_queries,
        "total_gaps": total_gaps,
        "most_cited_paper": most_cited.title if most_cited else None,
        "most_active_area": topic_clusters[0]["name"] if topic_clusters else None,
        "emerging_topic": "Foundation Models" if total_papers > 0 else None,
        "yearly_distribution": yearly_distribution,
        "top_keywords": dict(top_keywords),
        "topic_clusters": topic_clusters,
    }
