from __future__ import annotations

from typing import List

import serpapi

from .config import load_settings


def search_web(query: str, num_results: int = 5) -> List[str]:
    settings = load_settings()
    if not settings.serpapi_api_key:
        return []

    params = {
        "engine": "google",
        "q": query,
        "api_key": settings.serpapi_api_key,
        "num": num_results,
    }
    try:
        if hasattr(serpapi, "Client"):
            client = serpapi.Client(api_key=settings.serpapi_api_key)
            result = client.search(params)
        elif hasattr(serpapi, "SerpApiClient"):
            client = serpapi.SerpApiClient(api_key=settings.serpapi_api_key)
            result = client.search(params)
        elif hasattr(serpapi, "GoogleSearch"):
            result = serpapi.GoogleSearch(params).get_dict()
        elif hasattr(serpapi, "google_search"):
            result = serpapi.google_search(params)
        else:
            return []
    except Exception:
        # Web search is optional input; failing closed prevents API 500s.
        return []

    organic = (
        result.get("organic_results", [])
        if isinstance(result, dict)
        else result.as_dict().get("organic_results", [])
    )

    snippets: List[str] = []
    for item in organic[:num_results]:
        title = item.get("title", "").strip()
        link = item.get("link", "").strip()
        snippet = item.get("snippet", "").strip()
        if not title and not snippet:
            continue
        line = f"- {title} ({link})"
        if snippet:
            line = f"{line}\n  {snippet}"
        snippets.append(line)
    return snippets
