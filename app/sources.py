import urllib.parse

def google_news_rss(query: str, hl: str = "en", gl: str = "US", ceid: str = "US:en") -> str:
    # Google News RSS search endpoint
    # Example: https://news.google.com/rss/search?q=meteorite&hl=en-US&gl=US&ceid=US:en
    q = urllib.parse.quote(query)
    return f"https://news.google.com/rss/search?q={q}&hl={hl}&gl={gl}&ceid={ceid}"

def get_feed_urls(query: str) -> list[str]:
    return [
        google_news_rss(query, hl="en", gl="US", ceid="US:en"),
        google_news_rss(query, hl="en", gl="GB", ceid="GB:en"),
        google_news_rss(query, hl="en", gl="AU", ceid="AU:en"),
        google_news_rss(query, hl="en", gl="CA", ceid="CA:en"),
    ]
