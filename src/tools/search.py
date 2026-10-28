"""Free Web Search Tool using DuckDuckGo."""

import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

def search_market_data(query: str, max_results: int = 4) -> str:
    """
    Search the web for market data, competitors, and industry discussions using DuckDuckGo.
    Requires NO API key and is 100% free.
    """
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
            if not results:
                return "No external search results found for this query."
            
            formatted_chunks: List[str] = []
            for idx, r in enumerate(results, start=1):
                title = r.get("title", "Untitled")
                snippet = r.get("body", "No snippet available.")
                href = r.get("href", "")
                formatted_chunks.append(
                    f"Result {idx}:\n- Title: {title}\n- Snippet: {snippet}\n- URL: {href}"
                )
            return "\n\n".join(formatted_chunks)
    except ImportError:
        logger.warning("duckduckgo_search package not installed. Using fallback message.")
        return (
            "Web search package not installed yet. "
            "(To enable live search, run: pip install duckduckgo-search)"
        )
    except Exception as exc:
        logger.warning(f"DuckDuckGo search error: {exc}")
        return f"Live web search temporarily unavailable: {str(exc)}. Proceeding with parametric market intelligence."

