"""
ResearchPilot AI - Academic Source: Base Class
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class StandardPaper:
    """Unified paper format returned by all academic sources."""
    title: str
    abstract: Optional[str] = None
    authors: List[str] = field(default_factory=list)
    year: Optional[int] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    source: str = "unknown"
    source_id: Optional[str] = None
    citation_count: int = 0
    keywords: List[str] = field(default_factory=list)
    research_field: Optional[str] = None
    pdf_url: Optional[str] = None
    journal: Optional[str] = None
    venue: Optional[str] = None


class AcademicSource(ABC):
    """Abstract base class for all academic sources."""

    name: str = "base"

    @abstractmethod
    async def search(self, query: str, max_results: int = 20, year_from: Optional[int] = None, year_to: Optional[int] = None) -> List[StandardPaper]:
        """Search for papers matching the query."""
        pass

    def is_available(self) -> bool:
        """Check if this source is currently available."""
        return True
