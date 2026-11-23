"""HTTP endpoint for backend and Ollama health."""

from flask import Blueprint, jsonify

from services.ollama_service import is_available

health_blueprint = Blueprint("health", __name__)


@health_blueprint.get("/api/health")
def health_endpoint():
    return jsonify({"backend": True, "ollama": is_available()})
