from __future__ import annotations
from typing import List
import tiktoken


def _encode_length(text: str, encoding: str) -> int:
    enc = tiktoken.get_encoding(encoding)
    return len(enc.encode(text))


def split_text_by_tokens(text: str, chunk_size: int, overlap: int, encoding: str = "cl100k_base") -> List[str]:
    enc = tiktoken.get_encoding(encoding)
    tokens = enc.encode(text)
    chunks: List[str] = []

    if chunk_size <= 0:
        return [text]

    start = 0
    while start < len(tokens):
        end = min(start + chunk_size, len(tokens))
        chunk_tokens = tokens[start:end]
        chunks.append(enc.decode(chunk_tokens))
        if end == len(tokens):
            break
        start = max(0, end - overlap)

    return chunks