from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.config import API_HOST, API_PORT
from app.db import init_db, list_events

app = FastAPI(title="skyfall-alert")

# Serve static map UI
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
def _startup():
    init_db()

@app.get("/", response_class=HTMLResponse)
def index():
    # simple redirect-ish: serve the map
    with open("static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

@app.get("/events")
def events(limit: int = 2000):
    """
    Returns events suitable for the map.
    """
    return list_events(limit=limit)

def main():
    import uvicorn
    uvicorn.run("app.api:app", host=API_HOST, port=API_PORT, reload=False)

if __name__ == "__main__":
    main()
