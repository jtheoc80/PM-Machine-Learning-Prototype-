from __future__ import annotations
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from backend.app.core.config import get_settings

_settings = get_settings()


class VectorStore:
    def __init__(self) -> None:
        self.client = chromadb.Client(ChromaSettings(persist_directory=_settings.chroma_persist_path))
        self.collection = self.client.get_or_create_collection(name=_settings.chroma_collection, metadata={"hnsw:space": "cosine"})

    def add(
        self,
        ids: List[str],
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        embeddings: Optional[List[List[float]]] = None,
    ) -> None:
        self.collection.add(
            ids=ids,
            documents=texts,
            metadatas=metadatas or [],
            embeddings=embeddings,
        )

    def query(
        self,
        query_texts: Optional[List[str]] = None,
        n_results: int = 8,
        query_embeddings: Optional[List[List[float]]] = None,
    ) -> Dict[str, Any]:
        kwargs: Dict[str, Any] = {
            "n_results": n_results,
            "include": ["documents", "metadatas", "distances", "ids"],
        }
        if query_embeddings is not None:
            kwargs["query_embeddings"] = query_embeddings
        else:
            kwargs["query_texts"] = query_texts or [""]
        return self.collection.query(**kwargs)

    def count(self) -> int:
        return self.collection.count()


_vector_store: Optional[object] = None


def get_vector_store() -> object:
    global _vector_store
    if _vector_store is None:
        if _settings.vector_store_provider.lower() == "pgvector":
            from backend.app.services.vectorstore_pg import PgVectorStore

            _vector_store = PgVectorStore()
        else:
            _vector_store = VectorStore()
    return _vector_store