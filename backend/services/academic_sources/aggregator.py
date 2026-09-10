"""
ResearchPilot AI - Academic Source Aggregator
Searches multiple sources in parallel, deduplicates, and ranks results.
"""
import asyncio
from typing import List, Optional, Dict, Any

from backend.services.academic_sources.base import StandardPaper, AcademicSource
from backend.services.academic_sources.arxiv_source import ArxivSource
from backend.services.academic_sources.semantic_scholar_source import SemanticScholarSource
from backend.services.academic_sources.crossref_source import CrossrefSource
from backend.services.academic_sources.openalex_source import OpenAlexSource


SOURCE_REGISTRY: Dict[str, AcademicSource] = {
    "arxiv": ArxivSource(),
    "semantic_scholar": SemanticScholarSource(),
    "crossref": CrossrefSource(),
    "openalex": OpenAlexSource(),
}


def _normalize_title(title: str) -> str:
    """Lowercase and strip punctuation for deduplication."""
    import re
    return re.sub(r"[^a-z0-9 ]", "", title.lower()).strip()


def deduplicate(papers: List[StandardPaper]) -> List[StandardPaper]:
    """Remove near-duplicate papers by title or DOI."""
    seen_dois = set()
    seen_titles = set()
    unique = []
    for paper in papers:
        if paper.doi and paper.doi in seen_dois:
            continue
        norm_title = _normalize_title(paper.title)
        if norm_title in seen_titles:
            continue
        if paper.doi:
            seen_dois.add(paper.doi)
        seen_titles.add(norm_title)
        unique.append(paper)
    return unique


def rank_papers(papers: List[StandardPaper], query: str) -> List[StandardPaper]:
    """
    Simple relevance ranking:
    - Citation count contributes heavily
    - Query term presence in title boosts score
    - Recency (year) provides a mild boost
    """
    import re

    query_words = set(re.sub(r"[^a-z0-9 ]", "", query.lower()).split())
    current_year = 2024

    def score(p: StandardPaper) -> float:
        title_words = set(re.sub(r"[^a-z0-9 ]", "", (p.title or "").lower()).split())
        abstract_words = set(re.sub(r"[^a-z0-9 ]", "", (p.abstract or "").lower()).split())
        overlap_title = len(query_words & title_words) / max(len(query_words), 1)
        overlap_abstract = len(query_words & abstract_words) / max(len(query_words), 1)
        citation_score = min((p.citation_count or 0) / 1000.0, 1.0)
        year_score = min(((p.year or 2000) - 2000) / (current_year - 2000 + 1), 1.0) if p.year else 0.0
        return overlap_title * 3 + overlap_abstract * 1.5 + citation_score * 2 + year_score * 0.5

    return sorted(papers, key=score, reverse=True)


async def search_all_sources(
    query: str,
    sources: Optional[List[str]] = None,
    max_results_per_source: int = 20,
    year_from: Optional[int] = None,
    year_to: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Search all selected academic sources concurrently,
    deduplicate, and return ranked results.
    """
    if sources is None:
        sources = ["arxiv", "semantic_scholar", "openalex"]

    active_sources = [SOURCE_REGISTRY[s] for s in sources if s in SOURCE_REGISTRY]

    tasks = [
        src.search(query, max_results=max_results_per_source, year_from=year_from, year_to=year_to)
        for src in active_sources
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    all_papers: List[StandardPaper] = []
    sources_searched = []
    for src, result in zip(active_sources, results):
        if isinstance(result, Exception):
            print(f"[Aggregator] Source {src.name} failed: {result}")
        else:
            all_papers.extend(result)
            sources_searched.append(src.name)

    unique_papers = deduplicate(all_papers)
    ranked_papers = rank_papers(unique_papers, query)

    return {
        "papers": ranked_papers,
        "total_found": len(ranked_papers),
        "sources_searched": sources_searched,
    }
