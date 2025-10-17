#!/usr/bin/env python3
"""
Ingest Emerson J-series manual text (or other documents) into Supabase with OpenAI embeddings.

Usage:
  export SUPABASE_URL=...
  export SUPABASE_KEY=...
  export OPENAI_API_KEY=...
  python scripts/ingest_emerson_j_series.py --input-file data/emerson_j_series.txt --source-id emerson_j_series_v1 --valve-model J-series

This script uses OpenAI's text-embedding-3-small embeddings and upserts chunks into Supabase.
"""
import os
import argparse
import math
import json
from typing import List
from supabase import create_client
import numpy as np
import time

OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"
BATCH_SIZE = 16

def chunk_text(text: str, max_chars: int = 2000):
    # Split by paragraphs where possible to keep chunks coherent.
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    current = ""
    for p in paragraphs:
        if len(current) + len(p) + 2 <= max_chars:
            current = (current + "\n\n" + p).strip() if current else p
        else:
            if current:
                chunks.append(current)
            if len(p) <= max_chars:
                current = p
            else:
                # further split long paragraph
                start = 0
                while start < len(p):
                    chunks.append(p[start:start+max_chars])
                    start += max_chars
                current = ""
    if current:
        chunks.append(current)
    return chunks

def get_openai_embeddings(texts: List[str]):
    import openai
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        raise RuntimeError("OPENAI_API_KEY environment variable is required for OpenAI embeddings")

    embeddings = []
    # Batch requests to avoid very large payloads
    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i:i+BATCH_SIZE]
        resp = openai.Embedding.create(model=OPENAI_EMBEDDING_MODEL, input=batch)
        for item in resp["data"]:
            embeddings.append(np.array(item["embedding"], dtype=float))
        time.sleep(0.1)  # small pause
    return np.stack(embeddings, axis=0)

def upsert_chunks(supabase, chunks, source_id, valve_model, source_type="manual"):
    rows = []
    for idx, (chunk_text, embedding) in enumerate(chunks):
        rows.append({
            "source_type": source_type,
            "source_id": f"{source_id}__chunk_{idx}",
            "valve_model": valve_model,
            "text_content": chunk_text,
            "metadata": {"orig_source": source_id, "chunk_index": idx},
            "embedding": embedding.tolist()
        })
    # Batch insert (adjust batch size as needed)
    batch_size = 50
    for i in range(0, len(rows), batch_size):
        batch = rows[i:i+batch_size]
        res = supabase.table("documents").insert(batch).execute()
        if res.error:
            print("Insert error:", res.error)
            raise RuntimeError("Supabase insert failed")
        else:
            print(f"Inserted batch {i//batch_size + 1}: {len(batch)} rows")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-file", required=True, help="Plain-text file containing manual content or excerpt")
    parser.add_argument("--source-id", required=True, help="Unique id for this source (used to avoid duplicates)")
    parser.add_argument("--valve-model", default="J-series", help="Valve model label to store with each chunk")
    parser.add_argument("--max-chars", type=int, default=2000)
    args = parser.parse_args()

    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise RuntimeError("SUPABASE_URL and SUPABASE_KEY environment variables must be set")

    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    with open(args.input_file, "r", encoding="utf-8") as f:
        text = f.read()

    chunks_text = chunk_text(text, max_chars=args.max_chars)
    print(f"Chunked input into {len(chunks_text)} chunks (max {args.max_chars} chars).")

    embeddings = get_openai_embeddings(chunks_text)
    if embeddings.shape[1] != 1536:
        print(f"Warning: embeddings dimension is {embeddings.shape[1]} (expected 1536). Make sure table vector dimension matches the model.")

    chunks = list(zip(chunks_text, embeddings))
    upsert_chunks(supabase, chunks, args.source_id, args.valve_model)
    print("Ingestion complete.")

if __name__ == "__main__":
    main()