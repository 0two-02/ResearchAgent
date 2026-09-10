"""
ResearchPilot AI - Vector Store (ChromaDB)
Stores and retrieves document chunks by semantic similarity.
"""
from typing import Any, Dict, List, Optional
import chromadb
from chromadb.config import Settings

from backend.config import CHROMA_PERSIST_DIRECTORY
from backend.services.embeddings.embedder import embed_texts, embed_single


_CLIENT: Optional[chromadb.Client] = None


def get_chroma_client() -> chromadb.Client:
    global _CLIENT
    if _CLIENT is None:
        try:
            _CLIENT = chromadb.PersistentClient(path=CHROMA_PERSIST_DIRECTORY)
        except Exception as e:
            print(f"[VectorStore] PersistentClient failed: {e}. Using in-memory client.")
            _CLIENT = chromadb.Client()
    return _CLIENT


def get_or_create_collection(name: str = "research_papers") -> chromadb.Collection:
    client = get_chroma_client()
    return client.get_or_create_collection(
        name=name,
        metadata={"hnsw:space": "cosine"},
    )


def index_chunks(
    chunks: List[str],
    doc_id: str,
    metadata: Optional[Dict[str, Any]] = None,
    collection_name: str = "research_papers",
) -> int:
    """
    Embed and store text chunks in the vector database.
    Returns number of chunks indexed.
    """
    if not chunks:
        return 0

    collection = get_or_create_collection(collection_name)
    embeddings = embed_texts(chunks)
    meta = metadata or {}

    ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
    metadatas = [{**meta, "chunk_index": i, "doc_id": doc_id} for i in range(len(chunks))]

    # Delete existing chunks for this doc if any
    try:
        existing = collection.get(where={"doc_id": doc_id})
        if existing["ids"]:
            collection.delete(ids=existing["ids"])
    except Exception:
        pass

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=chunks,
        metadatas=metadatas,
    )
    return len(chunks)


def semantic_search(
    query: str,
    n_results: int = 5,
    collection_name: str = "research_papers",
    where: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """
    Retrieve the most semantically similar chunks for a query.
    """
    collection = get_or_create_collection(collection_name)
    query_embedding = embed_single(query)

    try:
        kwargs: Dict[str, Any] = {
            "query_embeddings": [query_embedding],
            "n_results": n_results,
            "include": ["documents", "metadatas", "distances"],
        }
        if where:
            kwargs["where"] = where

        results = collection.query(**kwargs)

        output = []
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        dists = results.get("distances", [[]])[0]

        for doc, meta, dist in zip(docs, metas, dists):
            output.append({
                "text": doc,
                "metadata": meta,
                "similarity": 1 - dist,
            })
        return output
    except Exception as e:
        print(f"[VectorStore] Search error: {e}")
        return []
