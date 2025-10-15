from __future__ import annotations
from typing import List
import os
from fastapi import APIRouter, UploadFile, File
from backend.app.models.schemas import UploadResponse, CrawlRequest, CrawlResponse, ChatRequest, ChatResponse
from backend.app.services.ingest import ingest_paths
from backend.app.services.crawl import crawl_and_index
from backend.app.services.agent import answer_query
from backend.app.core.config import get_settings

router = APIRouter()


@router.post("/upload", response_model=UploadResponse)
async def upload_files(files: List[UploadFile] = File(...)) -> UploadResponse:
    upload_dir = "/workspace/data/uploads"
    os.makedirs(upload_dir, exist_ok=True)
    paths: List[str] = []
    for f in files:
        path = os.path.join(upload_dir, f.filename)
        with open(path, "wb") as out:
            out.write(await f.read())
        paths.append(path)
    chunks, processed = ingest_paths(paths)
    return UploadResponse(success=True, num_files=len(processed), message=f"Indexed {chunks} chunks from {len(processed)} files")


@router.post("/crawl", response_model=CrawlResponse)
async def crawl(req: CrawlRequest) -> CrawlResponse:
    settings = get_settings()
    pages, visited = crawl_and_index(req.seeds, req.allowed_domains or settings.default_allowed_domains, req.max_pages or settings.default_max_pages)
    return CrawlResponse(success=True, pages_indexed=pages, message=f"Crawled {len(visited)} pages")


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    result = answer_query(req.query, top_k=req.top_k)
    return ChatResponse(answer=result["answer"], sources=result["sources"])