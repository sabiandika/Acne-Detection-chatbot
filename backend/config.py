"""Environment based backend configuration."""

import os


FLASK_HOST = os.getenv("FLASK_HOST", "127.0.0.1")
FLASK_PORT = int(os.getenv("FLASK_PORT", "5000"))
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "false").lower() in {"1", "true", "yes"}
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:4b")
OLLAMA_TIMEOUT = float(os.getenv("OLLAMA_TIMEOUT", "120"))
HEALTH_TIMEOUT = float(os.getenv("HEALTH_TIMEOUT", "3"))
