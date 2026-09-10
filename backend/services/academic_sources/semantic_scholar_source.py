"""
ResearchPilot AI - Semantic Scholar Academic Source
"""
from typing import List, Optional
import httpx

from backend.config import SEMANTIC_SCHOLAR_API_KEY
from backend.services.academic_sources.base import AcademicSource, StandardPaper

SS_SEARCH_URL = "https://api.semanticscholar.org/graph/v1/paper/search"
SS_FIELDS = "title,abstract,authors,year,externalIds,citationCount,fieldsOfStudy,url,openAccessPdf,venue,publicationVenue"


class SemanticScholarSource(AcademicSource):
    name = "semantic_scholar"

    def _get_headers(self):
        headers = {"Accept": "application/json"}
        if SEMANTIC_SCHOLAR_API_KEY:
            headers["x-api-key"] = SEMANTIC_SCHOLAR_API_KEY
        return headers

    async def search(
        self,
        query: str,
        max_results: int = 20,
        year_from: Optional[int] = None,
        year_to: Optional[int] = None,
    ) -> List[StandardPaper]:
        params = {
            "query": query,
            "limit": min(max_results, 100),
            "fields": SS_FIELDS,
        }
        if year_from or year_to:
            yr_from = year_from or 2000
            yr_to = year_to or 2099
            params["year"] = f"{yr_from}-{yr_to}"

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(SS_SEARCH_URL, params=params, headers=self._get_headers())
                resp.raise_for_status()
                data = resp.json()
        except Exception as e:
            print(f"[SemanticScholarSource] Error: {e}")
            return []

        papers = []
        for item in data.get("data", []):
            authors = [a.get("name", "") for a in item.get("authors", [])]
            ext_ids = item.get("externalIds", {}) or {}
            doi = ext_ids.get("DOI")
            arxiv_id = ext_ids.get("ArXiv")
            url = item.get("url") or (f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else None)

            open_access = item.get("openAccessPdf")
            pdf_url = open_access.get("url") if open_access else None

            fields = item.get("fieldsOfStudy") or []
            field_name = fields[0] if fields else None

            venue_info = item.get("publicationVenue") or {}
            venue = venue_info.get("name") or item.get("venue")

            papers.append(
                StandardPaper(
                    title=item.get("title", "Untitled"),
                    abstract=item.get("abstract"),
                    authors=authors,
                    year=item.get("year"),
                    doi=doi,
                    url=url,
                    source="semantic_scholar",
                    source_id=item.get("paperId"),
                    citation_count=item.get("citationCount", 0),
                    keywords=[],
                    research_field=field_name,
                    pdf_url=pdf_url,
                    journal=venue,
                    venue=venue,
                )
            )
        return papers
