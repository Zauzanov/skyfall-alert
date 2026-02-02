import os

def _getenv(name: str, default: str | None = None) -> str:
    v = os.getenv(name, default)
    if v is None or v == "":
        raise RuntimeError(f"Missing required env var: {name}")
    return v

def _getint(name: str, default: int) -> int:
    v = os.getenv(name)
    if v is None or v == "":
        return default
    return int(v)

DB_PATH = os.getenv("APP_DB_PATH", "/data/app.db")

TELEGRAM_BOT_TOKEN = _getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = _getenv("TELEGRAM_CHAT_ID")

POLL_INTERVAL_SECONDS = _getint("POLL_INTERVAL_SECONDS", 1800)

NEWS_QUERY = os.getenv(
    "NEWS_QUERY",
    "meteorite fell OR meteorite crash OR meteorite impact OR fireball landed",
)

USER_AGENT = os.getenv("USER_AGENT", "skyfall-alert-bot/1.0")
GEOCODE_TIMEOUT_SECONDS = _getint("GEOCODE_TIMEOUT_SECONDS", 10)

API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = _getint("API_PORT", 8000)
