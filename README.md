# Job-sender-bot

Daily job digest (resume-aligned): fetches listings via the **Adzuna** API (official developer keys), ranks them with simple **keyword overlap** against your résumé text, and emails an HTML digest.

This is not résumé-aware ML—just transparent matching you can tune by editing your pasted résumé and search queries.

## Setup

1. **Python 3.10+**

2. **Adzuna API keys** (free): https://developer.adzuna.com/

3. Copy env:

   ```text
   copy .env.example .env
   ```

   Edit `.env` with `ADZUNA_*`, SMTP settings, and `DIGEST_TO`.

   Edit `preferences.json`: set `where` for on-site dealership/detail searches; tune `what` strings for remote tech.

4. **Résumé text**

   ```text
   copy profile\resume_text.sample.txt profile\resume_text.txt
   ```

   Replace contents with your full résumé as plain text (paste from PDF).

5. Install and run once:

   ```text
   cd job-digest-bot
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   python -m src.main
   ```

## Daily schedule

- **Windows Task Scheduler**: run `python -m src.main` daily after activating your venv (or use full path to `.venv\Scripts\python.exe`).
- **GitHub Actions**: see `.github/workflows/daily-digest.yml`. Add **Secrets**: `ADZUNA_APP_ID`, `ADZUNA_APP_KEY`, `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM`, `DIGEST_TO`. Optional: `RESUME_TEXT` (full résumé plain text) and `PREFERENCES_JSON` (full `preferences.json` body) so a **public** repo never stores your résumé or home city on disk.

## Notes

- **Salary**: Adzuna sometimes omits pay or uses annual figures—always verify on the employer site.
- **Coverage**: One aggregator never lists everything; adjust queries or add another source later if you outgrow Adzuna.
