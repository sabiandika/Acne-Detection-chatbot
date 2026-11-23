"""Validation helpers and response shape for the HTTP API."""


def validate_chat_request(data):
    if not isinstance(data, dict):
        return None, "Body request harus berupa JSON object."
    message = data.get("message")
    if not isinstance(message, str) or not message.strip():
        return None, "Pesan tidak boleh kosong."
    message = message.strip()
    if len(message) > 4000:
        return None, "Pesan terlalu panjang (maksimal 4000 karakter)."
    return {"message": message}, None


def chat_response(ok, reply):
    return {"ok": ok, "reply": reply}
