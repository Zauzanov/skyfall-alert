import feedparser
import requests
from app.config import USER_AGENT

def fetch_rss(url: str) -> list[dict]:
    # Some RSS responses are blocked unless fetched via requests with UA.
    r = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=20)
    r.raise_for_status()

    feed = feedparser.parse(r.text)
    items: list[dict] = []
    for e in feed.entries:
        items.append(
            {
                "title": getattr(e, "title", "") or "",
                "link": getattr(e, "link", "") or "",
                "published": getattr(e, "published", None),
                "summary": getattr(e, "summary", "") or "",
            }
        )
    return items
