"""HTTP client for the local Ollama chat API."""

import logging
import time

import requests

from config import (
    FLASK_DEBUG, HEALTH_TIMEOUT, OLLAMA_BASE_URL, OLLAMA_DEBUG_LOGS, OLLAMA_MODEL,
    OLLAMA_NUM_PREDICT, OLLAMA_REPEAT_PENALTY, OLLAMA_TIMEOUT, OLLAMA_TEMPERATURE,
    OLLAMA_TOP_K, OLLAMA_TOP_P, OLLAMA_NUM_CTX,
)

logger = logging.getLogger(__name__)


class OllamaError(RuntimeError):
    """Raised when Ollama is unavailable or returns an invalid response."""


def chat(messages, json_mode=False):
    started = time.perf_counter()
    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": OLLAMA_TEMPERATURE,
            "top_p": OLLAMA_TOP_P,
            "top_k": OLLAMA_TOP_K,
            "repeat_penalty": OLLAMA_REPEAT_PENALTY,
            "num_predict": OLLAMA_NUM_PREDICT,
            "num_ctx": OLLAMA_NUM_CTX,
        },
    }
    if json_mode:
        payload["format"] = "json"
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/chat", json=payload, timeout=OLLAMA_TIMEOUT
        )
        response.raise_for_status()
        content = response.json()["message"]["content"]
        if not isinstance(content, str):
            raise ValueError("Ollama response content is not text")
        logger.info(
            "Ollama request completed: model=%s duration_ms=%d messages=%d input_chars=%d output_chars=%d json=%s",
            OLLAMA_MODEL, int((time.perf_counter() - started) * 1000), len(messages),
            sum(len(item.get("content", "")) for item in messages), len(content), json_mode,
        )
        if FLASK_DEBUG and OLLAMA_DEBUG_LOGS:
            logger.debug("Ollama debug messages=%r output=%r", messages, content)
        return content
    except (requests.RequestException, ValueError, KeyError, TypeError) as exc:
        logger.warning(
            "Ollama request failed: model=%s duration_ms=%d messages=%d",
            OLLAMA_MODEL, int((time.perf_counter() - started) * 1000), len(messages),
        )
        raise OllamaError("Ollama request failed") from exc


def is_available():
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=HEALTH_TIMEOUT)
        return response.status_code == 200
    except requests.RequestException:
        return False
