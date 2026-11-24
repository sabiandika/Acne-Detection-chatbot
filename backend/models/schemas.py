"""Validated request, symptom, fuzzy, evidence, and response contracts."""

from datetime import date
from typing import Literal

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field, ValidationError


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    message: str = Field(min_length=1, max_length=4000)


class SymptomScores(BaseModel):
    """Explicitly reported symptom scores; None means the user did not say."""
    model_config = ConfigDict(extra="forbid")
    keminyakan: float | None = Field(default=None, ge=0, le=10)
    jerawat: float | None = Field(default=None, ge=0, le=10)
    iritasi: float | None = Field(default=None, ge=0, le=10)
    kekeringan: float | None = Field(default=None, ge=0, le=10)

class FuzzyInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    keminyakan: float = Field(ge=0, le=10)
    jerawat: float = Field(ge=0, le=10)
    iritasi: float = Field(ge=0, le=10)
    kekeringan: float = Field(ge=0, le=10)


class KnowledgeDocument(BaseModel):
    model_config = ConfigDict(extra="forbid")
    document_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    content: str = Field(min_length=1)
    source: str = Field(min_length=1)
    source_url: AnyHttpUrl
    category: str = Field(min_length=1)
    publication_date: date | None = None
    last_reviewed_date: date
    verification_status: Literal["verified", "needs_review"]


class ChatResponse(BaseModel):
    ok: bool
    reply: str


class GeneratedAnswer(BaseModel):
    model_config = ConfigDict(extra="forbid")
    answer: str = Field(min_length=1, max_length=3000)
    source_ids: list[str] = Field(min_length=1)


def validate_chat_request(data):
    try:
        request = ChatRequest.model_validate(data)
        return {"message": request.message}, None
    except ValidationError as exc:
        if not isinstance(data, dict):
            return None, "Body request harus berupa JSON object."
        if not isinstance(data.get("message"), str) or not data.get("message", "").strip():
            return None, "Pesan tidak boleh kosong."
        if len(data.get("message", "")) > 4000:
            return None, "Pesan terlalu panjang (maksimal 4000 karakter)."
        return None, "Format request tidak valid."


def chat_response(ok, reply):
    return ChatResponse(ok=ok, reply=reply).model_dump()
