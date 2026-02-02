import time
from datetime import datetime, timezone

from app.config import NEWS_QUERY, POLL_INTERVAL_SECONDS
from app.db import init_db, seen_url, insert_event
from app.sources import get_feed_urls
from app.fetcher import fetch_rss
from app.extract import (
    normalize_date,
    fetch_article_text,
    extract_location_guess,
    looks_like_meteorite_report,
)
from app.geocode import geocode
from app.telegram_notify import send_telegram_message

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def format_msg(event: dict) -> str:
    loc_parts = [p for p in [event.get("country"), event.get("region"), event.get("city")] if p]
    loc = ", ".join(loc_parts) if loc_parts else (event.get("raw_location_text") or "Unknown")

    date = event.get("published_at") or event.get("detected_at", "")[:10]

    return (
        "☄️ Meteorite fall report detected\n\n"
        f"📍 Location: {loc}\n"
        f"📅 Date: {date}\n"
        f"📰 Source: {event['source_url']}\n"
    )

def run_once() -> int:
    init_db()
    new_count = 0

    feed_urls = get_feed_urls(NEWS_QUERY)
    for feed_url in feed_urls:
        try:
            items = fetch_rss(feed_url)
        except Exception as e:
            print(f"[fetch_rss] failed: {feed_url} :: {e}")
            continue

        for item in items:
            title = item.get("title", "").strip()
            link = item.get("link", "").strip()
            summary = item.get("summary", "").strip()

            if not link or seen_url(link):
                continue

            if not looks_like_meteorite_report(title, summary):
                continue

            published_at = normalize_date(item.get("published"))

            # Fetch article text for better location extraction
            article_text = ""
            try:
                article_text = fetch_article_text(link)
            except Exception as e:
                print(f"[fetch_article_text] failed: {link} :: {e}")

            loc = extract_location_guess(title, summary, article_text)

            # Geocode best guess
            geo = None
            query_bits = [b for b in [loc.get("city"), loc.get("country")] if b]
            query = ", ".join(query_bits) if query_bits else (loc.get("country") or "")
            if query:
                try:
                    geo = geocode(query)
                except Exception as e:
                    print(f"[geocode] failed: {query} :: {e}")

            event = {
                "title": title or "(no title)",
                "source_url": link,
                "published_at": published_at,
                "detected_at": _now_iso(),
                "country": loc.get("country"),
                "region": loc.get("region"),
                "city": loc.get("city"),
                "latitude": geo.get("latitude") if geo else None,
                "longitude": geo.get("longitude") if geo else None,
                "raw_location_text": loc.get("raw_location_text"),
            }

            try:
                insert_event(event)
            except Exception as e:
                # unique constraint race or malformed
                print(f"[insert_event] failed: {link} :: {e}")
                continue

            # Notify
            try:
                send_telegram_message(format_msg(event))
            except Exception as e:
                print(f"[telegram] failed: {e}")

            new_count += 1

    return new_count

def main_loop() -> None:
    print("skyfall-alert worker started")
    while True:
        try:
            n = run_once()
            print(f"scan complete: {n} new event(s)")
        except Exception as e:
            print(f"[worker] fatal-ish error: {e}")
        time.sleep(POLL_INTERVAL_SECONDS)

if __name__ == "__main__":
    main_loop()
