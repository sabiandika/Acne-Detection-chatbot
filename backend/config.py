"""Environment based backend configuration."""

import os


FLASK_HOST = os.getenv("FLASK_HOST", "127.0.0.1")
FLASK_PORT = int(os.getenv("FLASK_PORT", "5000"))
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "false").lower() in {"1", "true", "yes"}
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:4b")
OLLAMA_TIMEOUT = float(os.getenv("OLLAMA_TIMEOUT", "120"))
OLLAMA_TEMPERATURE = float(os.getenv("OLLAMA_TEMPERATURE", "0.1"))
OLLAMA_TOP_P = float(os.getenv("OLLAMA_TOP_P", "0.8"))
OLLAMA_TOP_K = int(os.getenv("OLLAMA_TOP_K", "20"))
OLLAMA_REPEAT_PENALTY = float(os.getenv("OLLAMA_REPEAT_PENALTY", "1.1"))
OLLAMA_NUM_PREDICT = int(os.getenv("OLLAMA_NUM_PREDICT", "300"))
OLLAMA_DEBUG_LOGS = os.getenv("OLLAMA_DEBUG_LOGS", "false").lower() in {"1", "true", "yes"}
OLLAMA_EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
OLLAMA_EMBED_TIMEOUT = float(os.getenv("OLLAMA_EMBED_TIMEOUT", "10"))
HEALTH_TIMEOUT = float(os.getenv("HEALTH_TIMEOUT", "3"))
