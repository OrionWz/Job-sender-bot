import html
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any


def _salary_line(job: dict[str, Any]) -> str:
    lo, hi = job.get("salary_min"), job.get("salary_max")
    if lo or hi:
        return f"{lo or '?'} – {hi or '?'} (API units vary; verify posting)"
    return "Salary not listed"


def build_html(jobs: list[dict[str, Any]]) -> str:
    parts: list[str] = []
    parts.append("<h2>Daily job digest</h2>")
    parts.append("<p>Ranked by keyword overlap with your resume text (see README).</p>")
    parts.append("<ol>")
    for j in jobs:
        title = html.escape(j.get("title") or "")
        company = html.escape(j.get("company") or "")
        location = html.escape(j.get("location") or "")
        ql = html.escape(j.get("query_label") or "")
        score = j.get("_score")
        score_s = f"{score:.3f}" if isinstance(score, float) else ""
        url = html.escape(j.get("url") or "#")
        sal = html.escape(_salary_line(j))
        parts.append(
            "<li>"
            f"<strong>{title}</strong> — {company}<br/>"
            f"<small>{location} · {ql} · match {score_s} · {sal}</small><br/>"
            f'<a href="{url}">Open posting</a>'
            "</li>"
        )
    parts.append("</ol>")
    return "\n".join(parts)


def send_html_email(*, subject: str, html_body: str, to_addr: str) -> None:
    host = os.environ["SMTP_HOST"]
    port = int(os.environ.get("SMTP_PORT") or "587")
    user = os.environ["SMTP_USER"]
    password = os.environ["SMTP_PASSWORD"]
    from_addr = os.environ.get("SMTP_FROM") or user

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    with smtplib.SMTP(host, port, timeout=60) as smtp:
        smtp.starttls()
        smtp.login(user, password)
        smtp.sendmail(from_addr, [to_addr], msg.as_string())
