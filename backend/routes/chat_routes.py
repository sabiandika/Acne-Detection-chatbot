"""HTTP endpoint for chatbot conversations."""

import logging
import uuid

from flask import Blueprint, jsonify, request

from models.schemas import ProductChatResult, chat_response, validate_chat_request
from services.chatbot_service import process
from services.ollama_service import OllamaError
from utils.logger import PipelineTrace

logger = logging.getLogger(__name__)
chat_blueprint = Blueprint("chat", __name__)


@chat_blueprint.post("/api/chat")
def chat_endpoint():
    validated, error = validate_chat_request(request.get_json(silent=True))
    if error:
        return jsonify(chat_response(False, error, is_fallback=True)), 400

    request_id = uuid.uuid4().hex
    trace = PipelineTrace(
        request_id=request_id,
        conversation_id=validated.get("conversation_id"),
        history_length=len(validated.get("history", [])),
    )
    trace.set_message(validated["message"])

    try:
        result = process(
            validated["message"],
            request_id=request_id,
            history=validated.get("history", []),
            conversation_id=validated.get("conversation_id"),
            trace=trace,
        )
        trace.emit(logger)
        if isinstance(result, ProductChatResult):
            return jsonify(chat_response(
                True, result.reply, result.products,
                is_fallback=bool(trace.fallback_reason), trace_id=request_id,
            ))
        return jsonify(chat_response(
            True, result,
            is_fallback=bool(trace.fallback_reason), trace_id=request_id,
        ))
    except OllamaError as exc:
        trace.ollama_status = f"error:{type(exc).__name__}"
        trace.fallback_reason = "ollama_unavailable"
        trace.emit(logger, level=logging.WARNING)
        return jsonify(chat_response(
            False,
            'Ollama belum aktif atau model belum tersedia. Pastikan Ollama berjalan dan model "gemma3:4b" sudah diunduh.',
            is_fallback=True,
            trace_id=request_id,
        )), 503
    except Exception as exc:
        trace.fallback_reason = f"unhandled_exception:{type(exc).__name__}"
        trace.emit(logger, level=logging.ERROR)
        logger.exception("Unexpected chatbot processing error: request_id=%s", request_id)
        return jsonify(chat_response(
            False,
            "Terjadi kesalahan saat memproses pesan. Silakan coba lagi.",
            is_fallback=True,
            trace_id=request_id,
        )), 500
