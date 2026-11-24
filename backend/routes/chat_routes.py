"""HTTP endpoint for chatbot conversations."""

import logging
import uuid

from flask import Blueprint, jsonify, request

from models.schemas import chat_response, validate_chat_request
from services.chatbot_service import process
from services.ollama_service import OllamaError

logger = logging.getLogger(__name__)
chat_blueprint = Blueprint("chat", __name__)


@chat_blueprint.post("/api/chat")
def chat_endpoint():
    validated, error = validate_chat_request(request.get_json(silent=True))
    if error:
        return jsonify(chat_response(False, error)), 400
    request_id = uuid.uuid4().hex
    logger.info("Incoming chat request: request_id=%s message_chars=%d", request_id, len(validated["message"]))
    try:
        return jsonify(chat_response(True, process(validated["message"], request_id=request_id)))
    except OllamaError:
        logger.warning("Chat request failed because Ollama is unavailable: request_id=%s", request_id)
        return jsonify(chat_response(
            False,
            'Ollama belum aktif atau model belum tersedia. Pastikan Ollama berjalan dan model "gemma3:4b" sudah diunduh.',
        )), 503
    except Exception:
        logger.exception("Unexpected chatbot processing error: request_id=%s", request_id)
        return jsonify(chat_response(False, "Terjadi kesalahan saat memproses pesan. Silakan coba lagi.")), 500
