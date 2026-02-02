import re
from bs4 import BeautifulSoup
import requests
from dateutil import parser as dtparser
from geotext import GeoText
import pycountry
from app.config import USER_AGENT

COUNTRY_NAMES = {c.name for c in pycountry.countries}
COUNTRY_NAME_LOWER = {c.lower(): c for c in COUNTRY_NAMES}

def normalize_date(published_str: str | None) -> str | None:
    if not published_str:
        return None
    try:
        return dtparser.parse(published_str).date().isoformat()
    except Exception:
        return None

def fetch_article_text(url: str) -> str:
    # Very basic article text extraction
    r = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    # remove scripts/styles
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = soup.get_text("\n")
    text = re.sub(r"\n{2,}", "\n", text)
    return text[:20000]  # safety cap

def extract_location_guess(title: str, summary: str, article_text: str) -> dict:
    blob = " ".join([title, summary, article_text])

    places = GeoText(blob)
    cities = places.cities
    countries = places.countries

    # GeoText countries are often abbreviated; also detect full country names by substring
    blob_lower = blob.lower()
    for cname_lower, cname in COUNTRY_NAME_LOWER.items():
        if cname_lower in blob_lower:
            countries.append(cname)
            break

    city = cities[0] if cities else None
    country = countries[0] if countries else None

    raw = None
    if city and country:
        raw = f"{city}, {country}"
    elif city:
        raw = city
    elif country:
        raw = country

    return {
        "city": city,
        "region": None,
        "country": country,
        "raw_location_text": raw,
    }

def looks_like_meteorite_report(title: str, summary: str) -> bool:
    text = (title + " " + summary).lower()

    must_have = any(k in text for k in ["meteorite", "meteor"])
    if not must_have:
        return False

    # reduces false positives: "meteor shower", "meteorological" and so on. 
    if "meteor shower" in text or "meteorological" in text:
        return False

    # prioritizes "fell/landed/crashed/impact":
    signals = ["fell", "landed", "crash", "crashed", "impact", "hit", "struck", "smash"]
    return any(s in text for s in signals) or "meteorite" in text
