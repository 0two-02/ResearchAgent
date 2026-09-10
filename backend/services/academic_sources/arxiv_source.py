"""
ResearchPilot AI - arXiv Academic Source
"""
import asyncio
import re
import xml.etree.ElementTree as ET
from typing import List, Optional
import httpx

from backend.services.academic_sources.base import AcademicSource, StandardPaper


ARXIV_API_URL = "http://export.arxiv.org/api/query"
ARXIV_NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "arxiv": "http://arxiv.org/schemas/atom",
    "dc": "http://purl.org/dc/elements/1.1/",
}


class ArxivSource(AcademicSource):
    name = "arxiv"

    async def search(
        self,
        query: str,
        max_results: int = 20,
        year_from: Optional[int] = None,
        year_to: Optional[int] = None,
    ) -> List[StandardPaper]:
        params = {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": max_results,
            "sortBy": "relevance",
            "sortOrder": "descending",
        }
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(ARXIV_API_URL, params=params)
                resp.raise_for_status()

            return self._parse_response(resp.text, year_from, year_to)
        except Exception as e:
            print(f"[ArxivSource] Error: {e}")
            return []

    def _parse_response(self, xml_text: str, year_from: Optional[int], year_to: Optional[int]) -> List[StandardPaper]:
        papers = []
        try:
            root = ET.fromstring(xml_text)
            for entry in root.findall("atom:entry", ARXIV_NS):
                title_el = entry.find("atom:title", ARXIV_NS)
                title = title_el.text.strip().replace("\n", " ") if title_el is not None and title_el.text else "Untitled"

                abstract_el = entry.find("atom:summary", ARXIV_NS)
                abstract = abstract_el.text.strip().replace("\n", " ") if abstract_el is not None and abstract_el.text else None

                authors = []
                for author_el in entry.findall("atom:author", ARXIV_NS):
                    name_el = author_el.find("atom:name", ARXIV_NS)
                    if name_el is not None and name_el.text:
                        authors.append(name_el.text.strip())

                published_el = entry.find("atom:published", ARXIV_NS)
                year = None
                if published_el is not None and published_el.text:
                    m = re.match(r"(\d{4})", published_el.text)
                    if m:
                        year = int(m.group(1))

                if year_from and year and year < year_from:
                    continue
                if year_to and year and year > year_to:
                    continue

                id_el = entry.find("atom:id", ARXIV_NS)
                arxiv_url = id_el.text.strip() if id_el is not None and id_el.text else None
                arxiv_id = arxiv_url.split("/abs/")[-1] if arxiv_url else None

                pdf_url = None
                for link_el in entry.findall("atom:link", ARXIV_NS):
                    if link_el.get("type") == "application/pdf":
                        pdf_url = link_el.get("href")

                category_el = entry.find("arxiv:primary_category", ARXIV_NS)
                field_name = category_el.get("term") if category_el is not None else None

                papers.append(
                    StandardPaper(
                        title=title,
                        abstract=abstract,
                        authors=authors,
                        year=year,
                        url=arxiv_url,
                        source="arxiv",
                        source_id=arxiv_id,
                        pdf_url=pdf_url,
                        research_field=field_name,
                    )
                )
        except Exception as e:
            print(f"[ArxivSource] Parse error: {e}")
        return papers
