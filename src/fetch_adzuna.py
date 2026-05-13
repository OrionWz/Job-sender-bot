import os
from typing import Any

import requests

BASE = "https://api.adzuna.com/v1/api/jobs"


def search_jobs(
    *,
    country: str,
    app_id: str,
    app_key: str,
    what: str,
    where: str,
    results_per_page: int = 50,
    page: int = 1,
) -> list[dict[str, Any]]:
    params: dict[str, str | int] = {
        "app_id": app_id,
        "app_key": app_key,
        "results_per_page": results_per_page,
        "page": page,
        "what": what,
    }
    if where and where.strip():
        params["where"] = where.strip()

    url = f"{BASE}/{country}/search/{page}"
    r = requests.get(url, params=params, timeout=45)
    r.raise_for_status()
    data = r.json()
    return list(data.get("results") or [])


def _display_name(blob: Any) -> str:
    if isinstance(blob, dict):
        return str(blob.get("display_name") or blob.get("area") or "").strip()
    if blob is None:
        return ""
    return str(blob).strip()


def normalize(raw: dict[str, Any], *, query_label: str) -> dict[str, Any]:
    company = _display_name(raw.get("company"))
    location = _display_name(raw.get("location"))
    title = raw.get("title") or ""
    description = raw.get("description") or ""
    url = raw.get("redirect_url") or ""
    return {
        "title": title,
        "company": company,
        "location": location,
        "description_html": description,
        "url": url,
        "salary_min": raw.get("salary_min"),
        "salary_max": raw.get("salary_max"),
        "query_label": query_label,
        "raw": raw,
    }


def fetch_all_for_preferences(prefs: dict[str, Any]) -> list[dict[str, Any]]:
    app_id = os.environ["ADZUNA_APP_ID"]
    app_key = os.environ["ADZUNA_APP_KEY"]
    country = prefs.get("country_code") or "us"
    queries = prefs.get("queries") or []

    out: list[dict[str, Any]] = []
    for q in queries:
        label = q.get("label") or q.get("what") or "search"
        what = q.get("what") or ""
        where = q.get("where") or ""
        rows = search_jobs(
            country=country,
            app_id=app_id,
            app_key=app_key,
            what=what,
            where=where,
        )
        for row in rows:
            out.append(normalize(row, query_label=label))
    return out


def dedupe_by_url(jobs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for j in jobs:
        url = (j.get("url") or "").strip()
        key = url or f"{j.get('title')}|{j.get('company')}|{j.get('location')}"
        if key in seen:
            continue
        seen.add(key)
        unique.append(j)
    return unique
