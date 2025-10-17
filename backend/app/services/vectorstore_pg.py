from __future__ import annotations
from typing import List, Dict, Any, Optional, Tuple
import os

from sqlalchemy import create_engine, text, Table, Column, Text as SAText, MetaData
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.engine import Engine, Result
from sqlalchemy.dialects.postgresql import insert as pg_insert
from pgvector.sqlalchemy import Vector

from backend.app.core.config import get_settings


_settings = get_settings()


def _build_database_url() -> str:
    # Prefer explicit DATABASE_URL if provided
    if _settings.database_url:
        url = _settings.database_url
    elif (
        _settings.postgres_host
        and _settings.postgres_db
        and _settings.postgres_user
        and _settings.postgres_password
    ):
        url = (
            f"postgresql+psycopg2://{_settings.postgres_user}:{_settings.postgres_password}"
            f"@{_settings.postgres_host}:{_settings.postgres_port}/{_settings.postgres_db}"
        )
    else:
        raise RuntimeError(
            "No database configuration found. Set DATABASE_URL or Postgres parts via env."
        )

    # Ensure SSL for Supabase if not explicitly disabled
    if (".supabase.co" in url or os.getenv("SUPABASE") == "1") and "sslmode=" not in url:
        if "?" in url:
            url = url + "&sslmode=require"
        else:
            url = url + "?sslmode=require"
    return url


class PgVectorStore:
    def __init__(self) -> None:
        self.embedding_dim: int = _settings.embedding_dim
        self.distance: str = _settings.pgvector_distance.lower()
        self.ivfflat_lists: int = _settings.pgvector_ivfflat_lists

        self.engine: Engine = create_engine(
            _build_database_url(), pool_pre_ping=True, future=True
        )
        self._metadata = MetaData()
        self._documents = Table(
            "documents",
            self._metadata,
            Column("id", SAText, primary_key=True),
            Column("content", SAText, nullable=False),
            Column("metadata", JSONB, nullable=True),
            Column("embedding", Vector(dim=self.embedding_dim), nullable=False),
        )
        self._init_schema()

    def _init_schema(self) -> None:
        opclass = {
            "cosine": "vector_cosine_ops",
            "l2": "vector_l2_ops",
            "ip": "vector_ip_ops",
        }.get(self.distance, "vector_cosine_ops")
        with self.engine.begin() as conn:
            # Enable extension and create table
            conn.exec_driver_sql("CREATE EXTENSION IF NOT EXISTS vector")
            self._metadata.create_all(conn)
            # Create IVFFLAT index for approximate nearest neighbors
            conn.exec_driver_sql(
                f"""
                CREATE INDEX IF NOT EXISTS idx_documents_embedding
                ON documents USING ivfflat (embedding {opclass})
                WITH (lists = {int(self.ivfflat_lists)});
                """
            )

    def add(
        self,
        ids: List[str],
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        embeddings: Optional[List[List[float]]] = None,
    ) -> None:
        if not ids:
            return
        if embeddings is None:
            raise ValueError("embeddings must be provided when using PgVectorStore")
        if len(ids) != len(texts) or len(ids) != len(embeddings):
            raise ValueError("ids, texts, embeddings must be the same length")
        rows = []
        for i, _id in enumerate(ids):
            row = {
                "id": _id,
                "content": texts[i],
                "metadata": (metadatas[i] if metadatas and i < len(metadatas) else None),
                "embedding": embeddings[i],
            }
            rows.append(row)
        with self.engine.begin() as conn:
            stmt = pg_insert(self._documents).values(rows)
            stmt = stmt.on_conflict_do_update(
                index_elements=[self._documents.c.id],
                set_={
                    "content": stmt.excluded.content,
                    "metadata": stmt.excluded.metadata,
                    "embedding": stmt.excluded.embedding,
                },
            )
            conn.execute(stmt)

    def _distance_sql(self) -> Tuple[str, str]:
        # Returns (order_by_expr, select_distance_expr)
        if self.distance == "l2":
            op = "<->"
        elif self.distance == "ip":
            op = "<#>"
        else:
            op = "<=>"  # cosine distance
        return (f"embedding {op} :qvec", f"embedding {op} :qvec AS distance")

    def query(
        self,
        query_texts: Optional[List[str]] = None,
        n_results: int = 8,
        query_embeddings: Optional[List[List[float]]] = None,
    ) -> Dict[str, Any]:
        if (not query_embeddings) and query_texts:
            # Lazy import to avoid circular dependency at module import time
            from backend.app.services.embeddings import embed_texts

            query_embeddings = embed_texts([query_texts[0]])

        if not query_embeddings:
            raise ValueError("Either query_embeddings or query_texts must be provided")

        qvec = query_embeddings[0]
        order_by_expr, distance_expr = self._distance_sql()

        typed_sql = text(
            f"""
            SELECT id, content, metadata, {distance_expr}
            FROM documents
            ORDER BY {order_by_expr}
            LIMIT :limit
            """
        )
        with self.engine.begin() as conn:
            res: Result = conn.execute(typed_sql, {"qvec": qvec, "limit": int(n_results)})
            rows = res.fetchall()

        documents: List[str] = []
        metadatas: List[Dict[str, Any]] = []
        ids: List[str] = []
        distances: List[float] = []
        for r in rows:
            ids.append(r[0])
            documents.append(r[1])
            metadatas.append(r[2] or {})
            distances.append(float(r[3]))

        return {
            "documents": [documents],
            "metadatas": [metadatas],
            "ids": [ids],
            "distances": [distances],
        }

    def count(self) -> int:
        with self.engine.begin() as conn:
            res: Result = conn.execute(text("SELECT COUNT(*) FROM documents"))
            return int(res.scalar_one())
