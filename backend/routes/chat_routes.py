"""HTTP endpoint for chatbot conversations."""

import logging

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
    try:
        return jsonify(chat_response(True, process(validated["message"])))
    except OllamaError:
        logger.warning("Chat request failed because Ollama is unavailable")
        return jsonify(chat_response(
            False,
            'Ollama belum aktif atau model belum tersedia. Pastikan Ollama berjalan dan model "gemma3:4b" sudah diunduh.',
        )), 503
    except Exception:
        logger.exception("Unexpected chatbot processing error")
        return jsonify(chat_response(False, "Terjadi kesalahan saat memproses pesan. Silakan coba lagi.")), 500
