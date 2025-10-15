from typing import List, Optional
from pydantic import BaseModel


class UploadResponse(BaseModel):
    success: bool
    num_files: int
    message: str


class CrawlRequest(BaseModel):
    seeds: List[str]
    allowed_domains: Optional[List[str]] = None
    max_pages: Optional[int] = 100


class CrawlResponse(BaseModel):
    success: bool
    pages_indexed: int
    message: str


class ChatRequest(BaseModel):
    query: str
    top_k: Optional[int] = None


class SourceDoc(BaseModel):
    id: str
    uri: Optional[str] = None
    score: Optional[float] = None
    snippet: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceDoc]