import math
import re
from typing import FrozenSet

_STOP = frozenset(
    """
    a an and are as at be but by for from had has have he her hers him his how i if in into is it its me my no nor not of on or our ours she so such than that the their them then there these they this to too very was we were what when where which who whom why will with you your
    """.split()
)


def tokenize(text: str) -> FrozenSet[str]:
    text = text.lower()
    text = re.sub(r"[^a-z0-9+#./]+", " ", text)
    words = [w for w in text.split() if len(w) > 2 and w not in _STOP]
    return frozenset(words)


def score_job(resume_vocab: FrozenSet[str], title: str, description: str) -> float:
    blob = f"{title}\n{description}"
    job_vocab = tokenize(blob)
    if not resume_vocab or not job_vocab:
        return 0.0
    overlap = len(resume_vocab & job_vocab)
    # Normalize: overlap vs geometric mean of vocab sizes (simple relevance proxy)
    denom = math.sqrt(len(resume_vocab) * len(job_vocab))
    return overlap / denom if denom else 0.0


def strip_html(html: str) -> str:
    html = re.sub(r"<[^>]+>", " ", html)
    html = re.sub(r"\s+", " ", html)
    return html.strip()
