"""
ResearchPilot AI - Document Upload & Processing Routes
"""
import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from backend.config import UPLOAD_DIR, MAX_UPLOAD_SIZE_MB
from backend.database.session import get_db
from backend.database.models import Document
from backend.services.document_processor.extractor import extract_document, validate_upload
from backend.services.rag.vector_store import index_chunks
from backend.services.ibm.watsonx_client import watsonx

router = APIRouter()


@router.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Upload and process a document (PDF, TXT, CSV)."""
    filename = file.filename or "upload"
    file_ext = Path(filename).suffix.lower().lstrip(".")

    # Read file content
    content = await file.read()
    file_size = len(content)

    # Validate
    ok, err = validate_upload(filename, file_size)
    if not ok:
        raise HTTPException(status_code=400, detail=err)

    # Save to disk
    safe_name = f"{uuid.uuid4().hex}_{filename}"
    file_path = UPLOAD_DIR / safe_name
    with open(file_path, "wb") as f:
        f.write(content)

    # Extract content
    extraction = extract_document(str(file_path), file_ext)
    metadata = extraction.get("metadata", {})
    chunks = extraction.get("chunks", [])

    # Save to database
    doc = Document(
        filename=filename,
        file_type=file_ext,
        file_path=str(file_path),
        file_size=file_size,
        extracted_text=extraction.get("text", "")[:50000],  # Limit stored text
        detected_title=metadata.get("title"),
        detected_authors=metadata.get("authors"),
        detected_abstract=metadata.get("abstract"),
        chunk_count=len(chunks),
        is_indexed=False,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # Index in vector store
    if chunks:
        index_chunks(
            chunks=chunks,
            doc_id=str(doc.id),
            metadata={
                "doc_id": str(doc.id),
                "title": metadata.get("title") or filename,
                "source": "uploaded_document",
            }
        )
        doc.is_indexed = True
        db.commit()

    return {
        "id": doc.id,
        "filename": doc.filename,
        "file_type": doc.file_type,
        "file_size": doc.file_size,
        "detected_title": doc.detected_title,
        "detected_abstract": doc.detected_abstract,
        "chunk_count": doc.chunk_count,
        "is_indexed": doc.is_indexed,
        "message": f"Successfully processed {len(chunks)} text chunks.",
    }


@router.post("/documents/analyze")
async def analyze_document(document_id: int, db: Session = Depends(get_db)):
    """Generate AI insights from an uploaded document."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    text_sample = (doc.extracted_text or "")[:2000]
    prompt = f"""Analyze this research document and provide structured insights.

Document: {doc.filename}
Title: {doc.detected_title or 'Unknown'}
Content excerpt: {text_sample}

Provide:
1. Main topic/subject
2. Key findings or claims
3. Research methodology if present
4. Important keywords
5. Relevance assessment for academic research

Be concise and evidence-based.
"""
    insights = await watsonx.generate(prompt)

    return {
        "document": {
            "id": doc.id,
            "filename": doc.filename,
            "detected_title": doc.detected_title,
            "detected_abstract": doc.detected_abstract,
            "chunk_count": doc.chunk_count,
        },
        "insights": insights,
        "extracted_info": {
            "title": doc.detected_title,
            "authors": doc.detected_authors,
            "abstract": doc.detected_abstract,
        }
    }


@router.get("/documents")
def list_documents(db: Session = Depends(get_db)):
    docs = db.query(Document).order_by(Document.id.desc()).all()
    return [
        {
            "id": d.id,
            "filename": d.filename,
            "file_type": d.file_type,
            "file_size": d.file_size,
            "detected_title": d.detected_title,
            "chunk_count": d.chunk_count,
            "is_indexed": d.is_indexed,
        }
        for d in docs
    ]
