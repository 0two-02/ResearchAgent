"""
ResearchPilot AI - OpenAlex Academic Source
"""
from typing import List, Optional
import httpx

from backend.services.academic_sources.base import AcademicSource, StandardPaper

OPENALEX_URL = "https://api.openalex.org/works"


class OpenAlexSource(AcademicSource):
    name = "openalex"

    async def search(
        self,
        query: str,
        max_results: int = 20,
        year_from: Optional[int] = None,
        year_to: Optional[int] = None,
    ) -> List[StandardPaper]:
        params = {
            "search": query,
            "per-page": min(max_results, 200),
            "sort": "relevance_score:desc",
            "select": "id,title,abstract_inverted_index,authorships,publication_year,doi,open_access,primary_location,cited_by_count,concepts,keywords",
            "mailto": "research@researchpilot.ai",
        }
        if year_from or year_to:
            yr_from = year_from or 2000
            yr_to = year_to or 2099
            params["filter"] = f"publication_year:{yr_from}-{yr_to}"

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(OPENALEX_URL, params=params)
                resp.raise_for_status()
                data = resp.json()
        except Exception as e:
            print(f"[OpenAlexSource] Error: {e}")
            return []

        papers = []
        for item in data.get("results", []):
            title = item.get("title") or "Untitled"

            # Reconstruct abstract from inverted index
            abstract = None
            inv_index = item.get("abstract_inverted_index")
            if inv_index:
                try:
                    word_positions = []
                    for word, positions in inv_index.items():
                        for pos in positions:
                            word_positions.append((pos, word))
                    word_positions.sort(key=lambda x: x[0])
                    abstract = " ".join(w for _, w in word_positions)
                except Exception:
                    pass

            authors = []
            for authorship in item.get("authorships", []):
                author_info = authorship.get("author", {})
                name = author_info.get("display_name")
                if name:
                    authors.append(name)

            year = item.get("publication_year")
            doi = item.get("doi", "")
            if doi and doi.startswith("https://doi.org/"):
                doi = doi[len("https://doi.org/"):]
            elif doi and doi.startswith("http://doi.org/"):
                doi = doi[len("http://doi.org/"):]

            url = None
            oa_info = item.get("open_access", {})
            if oa_info:
                url = oa_info.get("oa_url")
            if not url and doi:
                url = f"https://doi.org/{doi}"

            primary_loc = item.get("primary_location", {}) or {}
            source_info = primary_loc.get("source", {}) or {}
            journal = source_info.get("display_name")

            cited_by = item.get("cited_by_count", 0)

            concepts = item.get("concepts", []) or []
            keywords = [c.get("display_name", "") for c in concepts[:10] if c.get("score", 0) > 0.3]

            field = concepts[0].get("display_name") if concepts else None

            papers.append(
                StandardPaper(
                    title=title,
                    abstract=abstract,
                    authors=authors[:10],
                    year=year,
                    doi=doi or None,
                    url=url,
                    source="openalex",
                    source_id=item.get("id"),
                    citation_count=cited_by,
                    keywords=keywords,
                    research_field=field,
                    journal=journal,
                )
            )
        return papers
