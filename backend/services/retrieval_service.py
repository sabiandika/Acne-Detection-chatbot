"""Local BM25 retrieval with optional Ollama embedding rank fusion."""

import json
import math
import re
from pathlib import Path

import numpy as np
import requests

from config import OLLAMA_BASE_URL, OLLAMA_EMBED_MODEL, OLLAMA_EMBED_TIMEOUT
from models.schemas import KnowledgeDocument
from utils.text_normalizer import normalisasi

_PATH = Path(__file__).resolve().parents[1] / "knowledge_base" / "curated_knowledge.json"
_EMBEDDINGS = {}
_RRF_K = 60


def load_documents():
    with _PATH.open(encoding="utf-8") as source_file:
        return [KnowledgeDocument.model_validate(item) for item in json.load(source_file)]


def retrieve(query, limit=3, category=None):
    query = normalisasi(query)
    terms = set(re.findall(r"[a-zA-Z0-9]+", query.lower()))
    documents = []
    for document in load_documents():
        if document.verification_status != "verified":
            continue
        if category and document.category != category:
            continue
        documents.append(document)

    document_tokens = [
        re.findall(r"[a-zA-Z0-9]+", f"{doc.title} {doc.content} {doc.category}".lower())
        for doc in documents
    ]
    average_length = sum(map(len, document_tokens)) / max(len(document_tokens), 1)
    bm25 = []
    for document, tokens in zip(documents, document_tokens):
        score = 0.0
        for term in terms:
            frequency = sum(term in set(other) for other in document_tokens)
            inverse_frequency = math.log(1 + (len(documents) - frequency + 0.5) / (frequency + 0.5))
            term_frequency = sum(token == term for token in tokens)
            denominator = term_frequency + 1.5 * (1 - 0.75 + 0.75 * len(tokens) / max(average_length, 1))
            score += inverse_frequency * term_frequency * 2.5 / max(denominator, 1e-8)
        if score:
            bm25.append((score, document))
    bm25.sort(key=lambda item: (-item[0], item[1].document_id))
    if not bm25:
        return []

    candidates = [document for _, document in bm25]
    semantic = _semantic_rank(query, candidates)
    bm25_rank = {doc.document_id: rank for rank, doc in enumerate(candidates, 1)}
    semantic_rank = {doc.document_id: rank for rank, doc in enumerate(semantic, 1)}
    fused = sorted(
        candidates,
        key=lambda doc: (
            -(
                1 / (_RRF_K + bm25_rank[doc.document_id])
                + 1 / (_RRF_K + semantic_rank.get(doc.document_id, len(candidates) + 1))
            ),
            doc.document_id,
        ),
    )
    return fused[:limit]


def _semantic_rank(query, documents):
    """Rerank keyword-matched candidates; gracefully fall back without embed model."""
    texts = [query] + [f"{doc.title}. {doc.content}" for doc in documents]
    missing = list(dict.fromkeys(text for text in texts if text not in _EMBEDDINGS))
    if missing:
        try:
            response = requests.post(
                f"{OLLAMA_BASE_URL}/api/embed",
                json={"model": OLLAMA_EMBED_MODEL, "input": missing},
                timeout=OLLAMA_EMBED_TIMEOUT,
            )
            response.raise_for_status()
            vectors = response.json()["embeddings"]
            if (not isinstance(vectors, list) or len(vectors) != len(missing)
                    or any(not isinstance(vector, list) or not vector for vector in vectors)
                    or any(not all(isinstance(value, (int, float)) and math.isfinite(value) for value in vector)
                           for vector in vectors)
                    or len({len(vector) for vector in vectors}) != 1):
                return []
            _EMBEDDINGS.update({text: vector for text, vector in zip(missing, vectors)})
        except (requests.RequestException, ValueError, KeyError, TypeError):
            return []

    query_vector = np.asarray(_EMBEDDINGS[query], dtype=float)
    query_norm = np.linalg.norm(query_vector)
    if query_norm == 0:
        return []
    ranked = []
    for document, text in zip(documents, texts[1:]):
        vector = np.asarray(_EMBEDDINGS[text], dtype=float)
        norm = np.linalg.norm(vector)
        similarity = float(np.dot(query_vector, vector) / (query_norm * norm)) if norm else 0.0
        ranked.append((similarity, document))
    ranked.sort(key=lambda item: (-item[0], item[1].document_id))
    return [document for _, document in ranked]
