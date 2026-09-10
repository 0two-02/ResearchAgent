"""
ResearchPilot AI - CrossRef Academic Source
"""
from typing import List, Optional
import httpx

from backend.services.academic_sources.base import AcademicSource, StandardPaper

CROSSREF_URL = "https://api.crossref.org/works"


class CrossrefSource(AcademicSource):
    name = "crossref"

    async def search(
        self,
        query: str,
        max_results: int = 20,
        year_from: Optional[int] = None,
        year_to: Optional[int] = None,
    ) -> List[StandardPaper]:
        params = {
            "query": query,
            "rows": min(max_results, 100),
            "select": "title,abstract,author,published,DOI,URL,subject,is-referenced-by-count,container-title",
            "sort": "relevance",
        }
        if year_from:
            params["filter"] = f"from-pub-date:{year_from}"

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(
                    CROSSREF_URL,
                    params=params,
                    headers={"User-Agent": "ResearchPilot AI (research@researchpilot.ai)"},
                )
                resp.raise_for_status()
                data = resp.json()
        except Exception as e:
            print(f"[CrossrefSource] Error: {e}")
            return []

        papers = []
        items = data.get("message", {}).get("items", [])
        for item in items:
            title_list = item.get("title", [])
            title = title_list[0] if title_list else "Untitled"

            abstract = item.get("abstract", "")
            if abstract:
                # Remove JATS XML tags
                import re
                abstract = re.sub(r"<[^>]+>", "", abstract).strip()

            authors = []
            for author in item.get("author", []):
                given = author.get("given", "")
                family = author.get("family", "")
                full = f"{given} {family}".strip()
                if full:
                    authors.append(full)

            year = None
            published = item.get("published") or item.get("published-print") or item.get("published-online")
            if published:
                date_parts = published.get("date-parts", [[]])
                if date_parts and date_parts[0]:
                    year = date_parts[0][0]

            if year_from and year and year < year_from:
                continue
            if year_to and year and year > year_to:
                continue

            doi = item.get("DOI")
            url = item.get("URL") or (f"https://doi.org/{doi}" if doi else None)
            citation_count = item.get("is-referenced-by-count", 0)
            subjects = item.get("subject", [])
            journal_list = item.get("container-title", [])
            journal = journal_list[0] if journal_list else None

            papers.append(
                StandardPaper(
                    title=title,
                    abstract=abstract or None,
                    authors=authors,
                    year=year,
                    doi=doi,
                    url=url,
                    source="crossref",
                    source_id=doi,
                    citation_count=citation_count,
                    keywords=subjects[:10],
                    research_field=subjects[0] if subjects else None,
                    journal=journal,
                )
            )
        return papers
