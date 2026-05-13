import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

from src.email_send import build_html, send_html_email
from src.fetch_adzuna import dedupe_by_url, fetch_all_for_preferences
from src.match import score_job, strip_html, tokenize


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def load_prefs(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def load_resume(path: Path) -> str:
    if not path.exists():
        print(f"Missing resume file: {path}", file=sys.stderr)
        print("Copy profile/resume_text.sample.txt to profile/resume_text.txt and paste your resume.", file=sys.stderr)
        sys.exit(1)
    return path.read_text(encoding="utf-8")


def main() -> None:
    load_dotenv(_repo_root() / ".env")

    root = _repo_root()
    prefs_path = root / "preferences.json"
    if not prefs_path.exists():
        print(f"Missing {prefs_path}. Copy preferences.example.json and edit.", file=sys.stderr)
        sys.exit(1)

    prefs = load_prefs(prefs_path)
    resume_text = load_resume(root / "profile" / "resume_text.txt")
    resume_vocab = tokenize(resume_text)

    salary_floor = prefs.get("salary_min_usd")

    jobs = dedupe_by_url(fetch_all_for_preferences(prefs))

    enriched: list[dict] = []
    for j in jobs:
        plain_desc = strip_html(j.get("description_html") or "")
        j["_score"] = score_job(resume_vocab, j.get("title") or "", plain_desc)

        smin = j.get("salary_min")
        if salary_floor is not None and smin is not None:
            try:
                if float(smin) < float(salary_floor):
                    continue
            except (TypeError, ValueError):
                pass

        enriched.append(j)

    enriched.sort(key=lambda x: float(x.get("_score") or 0), reverse=True)
    cap = int(prefs.get("max_jobs_in_email") or 20)
    top = enriched[:cap]

    if not top:
        print("No jobs after fetch/filter. Loosen salary_min_usd or queries.", file=sys.stderr)
        sys.exit(2)

    to_addr = os.environ.get("DIGEST_TO") or os.environ.get("SMTP_USER")
    if not to_addr:
        print("Set DIGEST_TO or SMTP_USER in .env", file=sys.stderr)
        sys.exit(1)

    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    subject = f"Job digest {day} ({len(top)} listings)"
    send_html_email(subject=subject, html_body=build_html(top), to_addr=to_addr)
    print(f"Sent digest with {len(top)} jobs to {to_addr}")


if __name__ == "__main__":
    main()
