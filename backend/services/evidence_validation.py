"""Conservative checks for generated educational answers."""

import re

from utils.text_normalizer import normalisasi


_UNSAFE_PATTERNS = (
    r"\bdiagnosis(?:nya)?\s+(?:adalah|pasti)\b",
    r"\bkamu\s+(?:pasti\s+)?(?:mengalami|menderita)\b",
    r"\bdosis\b",
    r"\bminum\s+\d+\s*(?:mg|ml|tablet|kali)\b",
    r"\b(?:resep|resepkan)\b",
    r"https?://",
)
_STOP_WORDS = {
    "adalah", "agar", "akan", "atau", "bagi", "bahwa", "belum", "bisa", "coba",
    "dapat", "dari", "dengan", "di", "ini", "itu", "jika", "juga", "kamu",
    "ke", "karena", "lebih", "maka", "membantu", "menjadi", "oleh", "pada",
    "para", "per", "perlu", "saat", "saja", "sebagai", "secara", "sehingga",
    "seperti", "serta", "sudah", "tanpa", "tidak", "untuk", "yang", "apa",
    "bagaimana", "apakah", "mengapa", "kenapa", "boleh", "dalam", "tentang",
    "tersebut", "beberapa", "banyak", "informasi", "cukup", "belas", "bisa", "nya",
}


def _content_terms(text):
    return {
        token for token in re.findall(r"[a-z0-9]+", normalisasi(text).lower())
        if len(token) > 2 and token not in _STOP_WORDS
    }


def validate_answer(question, answer, documents):
    """Reject obvious unsafe claims, irrelevant replies, and unsupported vocabulary."""
    if not isinstance(answer, str) or not answer.strip() or len(answer) > 3000:
        return False
    if any(re.search(pattern, answer, re.IGNORECASE) for pattern in _UNSAFE_PATTERNS):
        return False
    if re.search(r"\[[^\]]+\]\s*\(", answer):
        return False

    evidence_terms = _content_terms(" ".join(
        f"{doc.title} {doc.content} {doc.source}" for doc in documents
    ))
    question_terms = _content_terms(question)
    answer_terms = _content_terms(answer)
    if not question_terms.intersection(evidence_terms):
        return False
    if (not answer_terms or not answer_terms.intersection(question_terms)
            or not answer_terms.issubset(evidence_terms)):
        return False
    allowed_ids = {doc.document_id for doc in documents}
    cited_ids = set(re.findall(r"\[([a-z0-9-]+)\]", answer, re.IGNORECASE))
    return cited_ids <= allowed_ids
