import sqlite3
from contextlib import contextmanager
from app.config import DB_PATH

SCHEMA = """
PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  source_url TEXT NOT NULL UNIQUE,
  published_at TEXT,
  detected_at TEXT NOT NULL,

  country TEXT,
  region TEXT,
  city TEXT,

  latitude REAL,
  longitude REAL,

  raw_location_text TEXT
);

CREATE TABLE IF NOT EXISTS geocache (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  query TEXT NOT NULL UNIQUE,
  latitude REAL,
  longitude REAL,
  display_name TEXT,
  created_at TEXT NOT NULL
);
"""

@contextmanager
def connect():
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db() -> None:
    with connect() as conn:
        conn.executescript(SCHEMA)
        conn.commit()

def seen_url(source_url: str) -> bool:
    with connect() as conn:
        row = conn.execute("SELECT 1 FROM events WHERE source_url = ?", (source_url,)).fetchone()
        return row is not None

def insert_event(data: dict) -> int:
    with connect() as conn:
        cur = conn.execute(
            """
            INSERT INTO events (
              title, source_url, published_at, detected_at,
              country, region, city, latitude, longitude,
              raw_location_text
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["title"],
                data["source_url"],
                data.get("published_at"),
                data["detected_at"],
                data.get("country"),
                data.get("region"),
                data.get("city"),
                data.get("latitude"),
                data.get("longitude"),
                data.get("raw_location_text"),
            ),
        )
        conn.commit()
        return int(cur.lastrowid)

def list_events(limit: int = 2000) -> list[dict]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT id, title, source_url, published_at, detected_at,
                   country, region, city, latitude, longitude
            FROM events
            ORDER BY detected_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]
