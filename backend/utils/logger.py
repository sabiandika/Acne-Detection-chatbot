"""Shared logging setup and structured pipeline trace logger."""

from dataclasses import asdict, dataclass, field
import json
import logging
import re

_EMAIL_OR_PHONE_RE = re.compile(
    r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+|\b(?:\+62|08)\d{8,12}\b)"
)


def configure_logging(level=logging.INFO):
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


def _redact(text: str | None, max_len: int = 240) -> str | None:
    if text is None:
        return None
    cleaned = _EMAIL_OR_PHONE_RE.sub("[REDACTED]", text.strip())
    return cleaned[:max_len]


@dataclass
class PipelineTrace:
    request_id: str
    conversation_id: str | None = None
    incoming_message: str = ""
    history_length: int = 0
    resolved_context: str | None = None
    detected_intent: str | None = None
    scope_result: str | None = None
    symptoms: dict | None = None
    fuzzy_result: dict | None = None
    retrieved_docs: list[str] = field(default_factory=list)
    retrieved_products: list[str] = field(default_factory=list)
    ollama_status: str = "not_called"
    model_response_preview: str | None = None
    validation_result: str = "not_run"
    fallback_reason: str | None = None

    def set_message(self, message: str):
        self.incoming_message = _redact(message, max_len=200) or ""

    def set_model_response(self, raw_response: str | None):
        self.model_response_preview = _redact(raw_response, max_len=200)

    def emit(self, logger: logging.Logger, level: int = logging.INFO):
        payload = asdict(self)
        logger.log(level, "PIPELINE_TRACE %s", json.dumps(payload, ensure_ascii=False))
