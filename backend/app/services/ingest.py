from __future__ import annotations
from typing import List, Dict, Any, Tuple
import os
import io
import pandas as pd
from pypdf import PdfReader
from backend.app.utils.chunking import split_text_by_tokens
from backend.app.services.embeddings import embed_texts
from backend.app.services.vectorstore import get_vector_store
from backend.app.core.config import get_settings

_settings = get_settings()


def _read_txt(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def _read_pdf(path: str) -> str:
    reader = PdfReader(path)
    texts = []
    for page in reader.pages:
        try:
            texts.append(page.extract_text() or "")
        except Exception:
            continue
    return "\n".join(texts)


def _read_csv_or_xlsx(path: str) -> str:
    if path.lower().endswith(".csv"):
        df = pd.read_csv(path)
    else:
        df = pd.read_excel(path)
    return df.to_csv(index=False)


def _chunk_and_index(text: str, source_uri: str) -> int:
    chunks = split_text_by_tokens(text, _settings.chunk_size_tokens, _settings.chunk_overlap_tokens)
    if not chunks:
        return 0
    vs = get_vector_store()
    ids: List[str] = []
    metadatas: List[Dict[str, Any]] = []
    for idx, chunk in enumerate(chunks):
        ids.append(f"{source_uri}#chunk-{idx}")
        metadatas.append({"source": source_uri, "chunk_index": idx})
    embeddings = embed_texts(chunks)
    vs.add(ids=ids, texts=chunks, metadatas=metadatas, embeddings=embeddings)
    return len(chunks)


def ingest_paths(paths: List[str]) -> Tuple[int, List[str]]:
    indexed = 0
    processed: List[str] = []
    for path in paths:
        ext = os.path.splitext(path)[1].lower()
        try:
            if ext in [".txt", ".md"]:
                text = _read_txt(path)
            elif ext in [".pdf"]:
                text = _read_pdf(path)
            elif ext in [".csv", ".xlsx", ".xls"]:
                text = _read_csv_or_xlsx(path)
            else:
                # try raw read
                text = _read_txt(path)
            n = _chunk_and_index(text, source_uri=path)
            indexed += n
            processed.append(path)
        except Exception:
            continue
    return indexed, processed