from __future__ import annotations
from typing import List
from backend.app.core.config import get_settings


_settings = get_settings()


def embed_texts(texts: List[str]) -> List[List[float]]:
    if _settings.embedding_provider == "openai" and _settings.openai_api_key:
        return _embed_openai(texts)
    return _embed_local(texts)


def _embed_local(texts: List[str]) -> List[List[float]]:
    # Lazy import to avoid heavy load on boot
    from sentence_transformers import SentenceTransformer

    model_name = _settings.sentence_transformer_model
    model = SentenceTransformer(model_name)
    embeddings = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
    return embeddings.tolist()


def _embed_openai(texts: List[str]) -> List[List[float]]:
    from openai import OpenAI

    client = OpenAI(api_key=_settings.openai_api_key)
    model = _settings.openai_embedding_model
    response = client.embeddings.create(model=model, input=texts)
    return [item.embedding for item in response.data]