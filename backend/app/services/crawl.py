from __future__ import annotations
from typing import List, Set, Tuple
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from backend.app.services.ingest import _chunk_and_index


def _same_domain_str(url: str, allowed: Set[str]) -> bool:
    hostname = urlparse(url).hostname or ""
    if not allowed:
        return True
    return any(hostname.endswith(dom) for dom in allowed)


def crawl_and_index(seeds: List[str], allowed_domains: List[str], max_pages: int = 100) -> Tuple[int, List[str]]:
    allowed_set: Set[str] = set(allowed_domains or [])
    to_visit: List[str] = list(seeds)
    seen: Set[str] = set()
    indexed_pages = 0
    visited: List[str] = []

    while to_visit and len(seen) < max_pages:
        url = to_visit.pop(0)
        if url in seen:
            continue
        seen.add(url)
        if not _same_domain_str(url, allowed_set):
            continue
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code != 200 or "text/html" not in resp.headers.get("Content-Type", ""):
                continue
            soup = BeautifulSoup(resp.text, "html.parser")
            # Extract text
            for s in soup(["script", "style", "noscript"]):
                s.extract()
            text = soup.get_text(" ")
            if text.strip():
                n = _chunk_and_index(text, source_uri=url)
                indexed_pages += 1 if n > 0 else 0
                visited.append(url)
            # enqueue links
            for a in soup.find_all("a", href=True):
                href = a.get("href")
                next_url = urljoin(url, href)
                if next_url not in seen and _same_domain_str(next_url, allowed_set):
                    to_visit.append(next_url)
        except Exception:
            continue

    return indexed_pages, visited