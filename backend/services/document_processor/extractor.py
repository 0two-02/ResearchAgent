"""
ResearchPilot AI - Document Processor
Handles PDF, text, CSV, and image extraction.
"""
import io
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from a PDF file using pdfplumber."""
    try:
        import pdfplumber
        text_chunks = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_chunks.append(page_text.strip())
        return "\n\n".join(text_chunks)
    except ImportError:
        # Fallback: PyPDF2
        try:
            import PyPDF2
            text = ""
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"
            return text.strip()
        except Exception as e:
            print(f"[DocProcessor] PDF extraction error: {e}")
            return ""


def extract_text_from_txt(file_path: str) -> str:
    """Read plain text file."""
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception as e:
        print(f"[DocProcessor] Text extraction error: {e}")
        return ""


def extract_text_from_csv(file_path: str) -> str:
    """Convert CSV to a readable text form."""
    try:
        import csv
        rows = []
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.reader(f)
            for i, row in enumerate(reader):
                rows.append(", ".join(row))
                if i > 500:  # Limit large CSVs
                    rows.append("... (truncated)")
                    break
        return "\n".join(rows)
    except Exception as e:
        print(f"[DocProcessor] CSV extraction error: {e}")
        return ""


def detect_paper_metadata(text: str) -> Dict[str, Any]:
    """
    Heuristically detect title, authors, abstract from extracted text.
    """
    metadata: Dict[str, Any] = {"title": None, "authors": [], "abstract": None}

    if not text:
        return metadata

    lines = [l.strip() for l in text.split("\n") if l.strip()]

    # Title: first non-trivially short line in the first 20 lines
    for line in lines[:20]:
        if len(line) > 15 and not line.lower().startswith(("abstract", "introduction", "keywords")):
            metadata["title"] = line[:500]
            break

    # Abstract detection
    abstract_match = re.search(
        r"abstract[:\s]*\n?(.*?)(?=\n\s*\n|\nintroduction|\nkeywords|\n1\.?\s+intro)",
        text[:3000],
        re.IGNORECASE | re.DOTALL,
    )
    if abstract_match:
        raw_abstract = abstract_match.group(1).strip().replace("\n", " ")
        metadata["abstract"] = raw_abstract[:2000]

    return metadata


def chunk_text(text: str, chunk_size: int = 512, overlap: int = 64) -> List[str]:
    """
    Split text into overlapping chunks for embedding.
    """
    words = text.split()
    if not words:
        return []

    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        if end >= len(words):
            break
        start += chunk_size - overlap
    return chunks


def extract_document(file_path: str, file_type: str) -> Dict[str, Any]:
    """
    Full extraction pipeline for a document.
    Returns extracted text, detected metadata, and chunks.
    """
    file_type_lower = file_type.lower()

    if file_type_lower == "pdf":
        text = extract_text_from_pdf(file_path)
    elif file_type_lower in ("txt", "md", "text"):
        text = extract_text_from_txt(file_path)
    elif file_type_lower == "csv":
        text = extract_text_from_csv(file_path)
    else:
        text = extract_text_from_txt(file_path)  # Try as text

    metadata = detect_paper_metadata(text)
    chunks = chunk_text(text)

    return {
        "text": text,
        "metadata": metadata,
        "chunks": chunks,
        "chunk_count": len(chunks),
    }


ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md", ".csv", ".text"}
MAX_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB


def validate_upload(filename: str, file_size: int) -> Tuple[bool, str]:
    """Validate uploaded file by extension and size."""
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"Unsupported file type: {ext}. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
    if file_size > MAX_SIZE_BYTES:
        return False, f"File too large: {file_size / 1e6:.1f} MB. Max: 50 MB"
    return True, ""
