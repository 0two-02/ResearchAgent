"""
ResearchPilot AI - Pydantic Schemas
"""
from __future__ import annotations
from datetime import datetime
from typing import Any, List, Optional
from pydantic import BaseModel, ConfigDict, Field


# ─── Paper Schemas ────────────────────────────────────────────────────────────

class AuthorSchema(BaseModel):
    id: Optional[int] = None
    name: str
    affiliation: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class PaperBase(BaseModel):
    title: str
    abstract: Optional[str] = None
    year: Optional[int] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    source: Optional[str] = None
    source_id: Optional[str] = None
    citation_count: Optional[int] = 0
    keywords: Optional[List[str]] = None
    research_field: Optional[str] = None
    pdf_url: Optional[str] = None
    journal: Optional[str] = None
    venue: Optional[str] = None
    is_demo: bool = False


class PaperCreate(PaperBase):
    authors: Optional[List[str]] = []
    topics: Optional[List[str]] = []


class PaperOut(PaperBase):
    id: int
    authors: List[AuthorSchema] = []
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class PaperAnalysisOut(BaseModel):
    id: int
    paper_id: int
    problem_statement: Optional[str] = None
    objective: Optional[str] = None
    methodology: Optional[str] = None
    dataset: Optional[str] = None
    results: Optional[str] = None
    limitations: Optional[str] = None
    key_findings: Optional[str] = None
    future_work: Optional[str] = None
    summary: Optional[str] = None
    raw_json: Optional[Any] = None

    model_config = ConfigDict(from_attributes=True)


# ─── Research Request / Response Schemas ──────────────────────────────────────

class ResearchSearchRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=500)
    sources: Optional[List[str]] = ["arxiv", "semantic_scholar", "openalex"]
    max_results: int = Field(default=20, ge=1, le=100)
    year_from: Optional[int] = None
    year_to: Optional[int] = None
    demo_mode: bool = False


class ResearchSearchResponse(BaseModel):
    query_id: int
    query: str
    research_plan: Optional[Any] = None
    papers: List[PaperOut]
    total_found: int
    summary: Optional[str] = None
    sources_searched: List[str] = []
    demo_mode: bool = False


class PaperAnalyzeRequest(BaseModel):
    paper_ids: List[int]


class LiteratureReviewRequest(BaseModel):
    query_id: Optional[int] = None
    paper_ids: List[int]
    topic: Optional[str] = None


class LiteratureReviewOut(BaseModel):
    id: int
    title: Optional[str] = None
    introduction: Optional[str] = None
    existing_research: Optional[str] = None
    major_approaches: Optional[str] = None
    comparison_of_methods: Optional[str] = None
    important_findings: Optional[str] = None
    limitations: Optional[str] = None
    research_gaps: Optional[str] = None
    emerging_trends: Optional[str] = None
    future_directions: Optional[str] = None
    references: Optional[Any] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ResearchGapRequest(BaseModel):
    paper_ids: List[int]
    query_id: Optional[int] = None


class ResearchGapOut(BaseModel):
    research_gaps: List[str]
    evidence: List[str]
    importance: List[str]
    possible_research_questions: List[str]
    supporting_papers: Optional[Any] = None


class TrendRequest(BaseModel):
    paper_ids: List[int]
    query_id: Optional[int] = None


class TrendResponse(BaseModel):
    growing_topics: List[str]
    declining_topics: List[str]
    emerging_keywords: List[str]
    active_research_areas: List[str]
    yearly_distribution: Optional[Any] = None
    keyword_frequency: Optional[Any] = None
    disclaimer: str = "AI-assisted trend forecasting based on available research data."


class RecommendationRequest(BaseModel):
    paper_ids: List[int]
    query_id: Optional[int] = None
    research_topic: Optional[str] = None


class RecommendationOut(BaseModel):
    research_idea: str
    why_it_matters: str
    existing_evidence: str
    research_gap: str
    suggested_methodology: str
    possible_dataset: str
    expected_contribution: str
    difficulty_level: str


class RecommendationsResponse(BaseModel):
    recommendations: List[RecommendationOut]
    topic: Optional[str] = None


class CompareRequest(BaseModel):
    paper_ids: List[int]


class CompareResponse(BaseModel):
    papers: List[PaperOut]
    comparison_table: List[Any]
    ai_summary: Optional[str] = None


# ─── Chat Schemas ─────────────────────────────────────────────────────────────

class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    paper_ids: Optional[List[int]] = []
    query_id: Optional[int] = None
    history: Optional[List[ChatMessage]] = []


class ChatResponse(BaseModel):
    response: str
    sources: Optional[List[Any]] = []
    evidence: Optional[str] = None


# ─── Document Schemas ─────────────────────────────────────────────────────────

class DocumentOut(BaseModel):
    id: int
    filename: str
    file_type: str
    file_size: int
    detected_title: Optional[str] = None
    detected_authors: Optional[Any] = None
    detected_abstract: Optional[str] = None
    chunk_count: int = 0
    is_indexed: bool = False
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class DocumentAnalyzeResponse(BaseModel):
    document: DocumentOut
    insights: Optional[str] = None
    extracted_info: Optional[Any] = None


# ─── Dashboard Schema ─────────────────────────────────────────────────────────

class DashboardStats(BaseModel):
    total_papers: int
    total_topics: int
    total_queries: int
    total_gaps: int
    most_active_area: Optional[str] = None
    emerging_topic: Optional[str] = None
    most_cited_paper: Optional[str] = None
    yearly_distribution: Optional[Any] = None
    top_keywords: Optional[Any] = None
    topic_clusters: Optional[Any] = None
    citation_network: Optional[Any] = None
