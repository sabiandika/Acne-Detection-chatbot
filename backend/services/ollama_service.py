"""HTTP client for the local Ollama chat API."""

import requests

from config import HEALTH_TIMEOUT, OLLAMA_BASE_URL, OLLAMA_MODEL, OLLAMA_TIMEOUT


class OllamaError(RuntimeError):
    """Raised when Ollama is unavailable or returns an invalid response."""


def chat(messages, json_mode=False):
    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": False,
        "options": {"temperature": 0.3},
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
        return content
    except (requests.RequestException, ValueError, KeyError, TypeError) as exc:
        raise OllamaError("Ollama request failed") from exc


def is_available():
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=HEALTH_TIMEOUT)
        return response.status_code == 200
    except requests.RequestException:
        return False
