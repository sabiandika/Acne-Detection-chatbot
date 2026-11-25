"""Validated request, symptom, fuzzy, evidence, and response contracts."""

from datetime import date
from typing import Literal
from uuid import UUID

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field, ValidationError


class ChatHistoryMessage(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=1000)
    product_ids: list[int] = Field(default_factory=list, max_length=6)
    is_fallback: bool = False


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    message: str = Field(min_length=1, max_length=4000)
    conversation_id: UUID | None = None
    history: list[ChatHistoryMessage] = Field(default_factory=list, max_length=6)


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


class StoreProduct(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: int
    name: str = Field(min_length=1)
    category: Literal["Cleanser", "Moisturizer", "Serum", "Sunscreen"]
    price: int = Field(ge=0)
    rating: float = Field(ge=0, le=5)
    image: AnyHttpUrl
    description: str = Field(min_length=1)
    ingredients: list[str]
    skin: str = Field(min_length=1)


class ChatResponse(BaseModel):
    ok: bool
    reply: str
    products: list[StoreProduct] | None = None
    is_fallback: bool = False
    trace_id: str | None = None


class ProductChatResult(BaseModel):
    reply: str
    products: list[StoreProduct]


class GeneratedAnswer(BaseModel):
    model_config = ConfigDict(extra="forbid")
    answer: str = Field(min_length=1, max_length=3000)
    source_ids: list[str] = Field(min_length=1)


def validate_chat_request(data):
    try:
        request = ChatRequest.model_validate(data)
        result = {"message": request.message}
        if request.conversation_id:
            result["conversation_id"] = str(request.conversation_id)
        if request.history:
            result["history"] = [item.model_dump(mode="json") for item in request.history]
        return result, None
    except ValidationError as exc:
        if not isinstance(data, dict):
            return None, "Body request harus berupa JSON object."
        if not isinstance(data.get("message"), str) or not data.get("message", "").strip():
            return None, "Pesan tidak boleh kosong."
        if len(data.get("message", "")) > 4000:
            return None, "Pesan terlalu panjang (maksimal 4000 karakter)."
        return None, "Format request tidak valid."


def chat_response(ok, reply, products=None, is_fallback=False, trace_id=None):
    return ChatResponse(
        ok=ok,
        reply=reply,
        products=products,
        is_fallback=is_fallback,
        trace_id=trace_id,
    ).model_dump(mode="json", exclude_none=True)
