"""
ResearchPilot AI - Tests
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock


# ── Test: Academic Source Deduplication ──────────────────────────────────────

def test_deduplicate_by_doi():
    from backend.services.academic_sources.aggregator import deduplicate
    from backend.services.academic_sources.base import StandardPaper

    papers = [
        StandardPaper(title="Paper A", doi="10.1234/abc", source="arxiv"),
        StandardPaper(title="Paper A Duplicate", doi="10.1234/abc", source="crossref"),
        StandardPaper(title="Paper B", doi="10.1234/xyz", source="semantic_scholar"),
    ]
    result = deduplicate(papers)
    assert len(result) == 2
    assert result[0].doi == "10.1234/abc"
    assert result[1].doi == "10.1234/xyz"


def test_deduplicate_by_title():
    from backend.services.academic_sources.aggregator import deduplicate
    from backend.services.academic_sources.base import StandardPaper

    papers = [
        StandardPaper(title="Attention Is All You Need", source="arxiv"),
        StandardPaper(title="Attention Is All You Need", source="semantic_scholar"),
        StandardPaper(title="BERT: Pre-training of Transformers", source="semantic_scholar"),
    ]
    result = deduplicate(papers)
    assert len(result) == 2


def test_rank_papers():
    from backend.services.academic_sources.aggregator import rank_papers
    from backend.services.academic_sources.base import StandardPaper

    papers = [
        StandardPaper(title="Random unrelated topic", citation_count=100, year=2020, source="arxiv"),
        StandardPaper(title="Deep learning neural networks transformer", citation_count=5000, year=2022, source="arxiv"),
        StandardPaper(title="Transformer architecture attention mechanism", citation_count=10000, year=2018, abstract="transformer deep learning attention"),
    ]
    ranked = rank_papers(papers, "transformer deep learning")
    assert ranked[0].citation_count >= ranked[1].citation_count or ranked[0].title != papers[0].title


# ── Test: Text Chunking ───────────────────────────────────────────────────────

def test_chunk_text_basic():
    from backend.services.document_processor.extractor import chunk_text

    text = " ".join([f"word{i}" for i in range(1000)])
    chunks = chunk_text(text, chunk_size=100, overlap=20)
    assert len(chunks) > 1
    for chunk in chunks:
        words = chunk.split()
        assert len(words) <= 100


def test_chunk_text_empty():
    from backend.services.document_processor.extractor import chunk_text
    assert chunk_text("") == []
    assert chunk_text("   ") == []


def test_chunk_text_short():
    from backend.services.document_processor.extractor import chunk_text
    result = chunk_text("Short text", chunk_size=512)
    assert len(result) == 1
    assert result[0] == "Short text"


# ── Test: PDF Metadata Detection ─────────────────────────────────────────────

def test_detect_paper_metadata_with_abstract():
    from backend.services.document_processor.extractor import detect_paper_metadata

    text = """A Study on Deep Learning Methods

    John Smith, Jane Doe

    Abstract: This paper presents a novel deep learning approach
    for image classification tasks. We propose a new architecture
    that outperforms baseline methods.

    Introduction
    Deep learning has shown remarkable results...
    """
    meta = detect_paper_metadata(text)
    assert meta["title"] is not None
    assert meta["abstract"] is not None
    assert "deep learning" in meta["abstract"].lower()


def test_detect_paper_metadata_empty():
    from backend.services.document_processor.extractor import detect_paper_metadata
    meta = detect_paper_metadata("")
    assert meta["title"] is None
    assert meta["abstract"] is None


# ── Test: File Validation ─────────────────────────────────────────────────────

def test_validate_upload_valid():
    from backend.services.document_processor.extractor import validate_upload
    ok, msg = validate_upload("paper.pdf", 1024 * 1024)
    assert ok
    assert msg == ""


def test_validate_upload_invalid_extension():
    from backend.services.document_processor.extractor import validate_upload
    ok, msg = validate_upload("malware.exe", 1024)
    assert not ok
    assert "Unsupported" in msg


def test_validate_upload_too_large():
    from backend.services.document_processor.extractor import validate_upload
    ok, msg = validate_upload("paper.pdf", 100 * 1024 * 1024)
    assert not ok
    assert "too large" in msg.lower()


# ── Test: Embedding Service ───────────────────────────────────────────────────

def test_embed_texts_returns_correct_count():
    from backend.services.embeddings.embedder import embed_texts
    texts = ["Hello world", "Deep learning", "Transformer architecture"]
    embeddings = embed_texts(texts)
    assert len(embeddings) == 3
    assert all(isinstance(e, list) for e in embeddings)
    assert all(len(e) > 0 for e in embeddings)


def test_embed_empty():
    from backend.services.embeddings.embedder import embed_texts
    result = embed_texts([])
    assert result == []


# ── Test: IBM watsonx Client Demo Mode ────────────────────────────────────────

@pytest.mark.asyncio
async def test_watsonx_demo_mode_research_plan():
    from backend.services.ibm.watsonx_client import WatsonxClient
    client = WatsonxClient()
    # Force demo mode
    client._initialized = True
    client._client = None

    response = await client.generate("Create a research plan for: AI in healthcare")
    assert response is not None
    assert len(response) > 10


@pytest.mark.asyncio
async def test_research_planner_agent_output():
    from backend.services.research_agents.agents import research_planner_agent
    result = await research_planner_agent("Applications of AI in disease detection")
    assert "research_topic" in result or "key_concepts" in result
    assert isinstance(result, dict)


@pytest.mark.asyncio
async def test_trend_agent_with_papers():
    from backend.services.research_agents.agents import trend_prediction_agent
    papers = [
        {"title": "Deep Learning Survey", "year": 2022, "keywords": ["deep learning", "neural networks"]},
        {"title": "Transformer Models", "year": 2023, "keywords": ["transformer", "attention"]},
        {"title": "BERT Language Model", "year": 2020, "keywords": ["BERT", "NLP"]},
    ]
    result = await trend_prediction_agent(papers)
    assert "yearly_distribution" in result
    assert "disclaimer" in result


# ── Test: Demo Data ───────────────────────────────────────────────────────────

def test_demo_papers_structure():
    from data.demo.demo_data import DEMO_PAPERS
    assert len(DEMO_PAPERS) > 0
    for paper in DEMO_PAPERS:
        assert "title" in paper
        assert "abstract" in paper
        assert "authors" in paper
        assert "year" in paper
        assert paper["is_demo"] is True


# ── Test: API Health ─────────────────────────────────────────────────────────

def test_api_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def client():
    from fastapi.testclient import TestClient
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    from backend.main import app
    return TestClient(app)
