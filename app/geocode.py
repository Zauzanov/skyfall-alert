import time
import requests
from datetime import datetime, timezone
from app.config import USER_AGENT, GEOCODE_TIMEOUT_SECONDS
from app.db import connect

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def get_cached(query: str) -> dict | None:
    with connect() as conn:
        row = conn.execute(
            "SELECT query, latitude, longitude, display_name FROM geocache WHERE query = ?",
            (query,),
        ).fetchone()
        return dict(row) if row else None

def set_cache(query: str, lat: float, lon: float, display_name: str | None) -> None:
    with connect() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO geocache (query, latitude, longitude, display_name, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (query, lat, lon, display_name, _now_iso()),
        )
        conn.commit()

def geocode(query: str) -> dict | None:
    """
    Geocode with Nominatim (OSM):
    - include User-Agent
    - cache results
    - small delay to avoid hammering
    """
    if not query or len(query.strip()) < 3:
        return None

    cached = get_cached(query)
    if cached:
        return {
            "latitude": cached["latitude"],
            "longitude": cached["longitude"],
            "display_name": cached.get("display_name"),
        }

    params = {"q": query, "format": "json", "limit": 1}
    headers = {"User-Agent": USER_AGENT}

    r = requests.get(NOMINATIM_URL, params=params, headers=headers, timeout=GEOCODE_TIMEOUT_SECONDS)
    r.raise_for_status()
    data = r.json()

    # delay (important)
    time.sleep(1.1)

    if not data:
        return None

    item = data[0]
    lat = float(item["lat"])
    lon = float(item["lon"])
    display_name = item.get("display_name")

    set_cache(query, lat, lon, display_name)

    return {"latitude": lat, "longitude": lon, "display_name": display_name}
