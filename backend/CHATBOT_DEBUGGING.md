# Ollama request trace and reliability fixes

## Request path

1. `POST /api/chat` accepts Pydantic-validated `{message}`, optional `conversation_id`, and up to six typed recent `history` messages. Unsupported fields/roles are rejected. Each request gets a random request ID for logs. The response keeps `{ok, reply}` and adds `products` only for catalog responses.
2. `chatbot_service.process()` calls `scope_filter.classify_intent()` before any model call. This is deterministic and routes unrelated, unsafe medical, emergency, application, general education, and symptom-analysis requests.
3. Out-of-scope, unsafe, emergency, and application requests return deterministic text without calling Ollama. Symptom requests use the deterministic normalized lexicon. Unknown symptoms trigger clarification. Complete symptom inputs go through Fuzzy Mamdani and are rendered by Python; fuzzy data never enters an LLM prompt.
4. General education requests retrieve verified documents using BM25 and optional Ollama embeddings. The Ollama messages always begin with the dedicated `SYSTEM_PROMPT`, include only the bounded recent turns from this client conversation, then the current question, and place retrieved evidence in a separate system message. History is context only, never evidence.
5. Ollama must return JSON matching `GeneratedAnswer`. Source IDs must be among the retrieved document IDs; answer text must pass unsafe-language, URL/citation, question relevance, and evidence vocabulary checks. A failed parse or validation gets at most one corrective retry, then a fixed safe fallback. Raw model text is never returned unvalidated.

## What the trace found

- The old `classify()` fused a keyword score with an LLM score. A mistaken scope score could admit unrelated text. Scope decisions now use explicit deterministic cues; there is no LLM scope vote.
- The previous generation prompt was short and put the question and evidence in one user message. It lacked explicit domain, injection, medical safety, and output schema rules. It now uses a dedicated system prompt and separate message roles.
- The earlier output checker only rejected a few unsafe phrases and unknown bracketed IDs. It did not check question overlap or whether answer terms existed in evidence. Validation now adds those checks and uses one bounded retry.
- Before the product/context integration, the frontend sent only the current message. The API now accepts a bounded client history; it has no server-side session store. A new frontend conversation gets a new ID and resets local turns. Historical assistant claims remain untrusted and cannot support medical answers; product IDs are looked up again in the actual catalog.

## Ollama request configuration

- Model remains `gemma3:4b`; base URL and 120-second timeout remain environment-configurable.
- `temperature=0.1`, `top_p=0.8`, `top_k=20`, and `repeat_penalty=1.1` reduce generation variation/repetition for factual short answers. `num_predict=300` bounds output length.
- Streaming stays disabled so the complete structured response can be parsed and validated before returning it.
- `num_ctx` is not forced; Ollama keeps the model default to avoid imposing extra memory use on unknown hardware.
- Prompt/output debug logging is off by default and only activates when both `FLASK_DEBUG=true` and `OLLAMA_DEBUG_LOGS=true`. Regular logs record request ID, intent, message length, model, prompt size, output size, and latency, not user text.

## Limits

Scope cues do not understand every phrasing or misspelling. The validator is deterministic and conservative, but lexical support cannot prove semantic entailment. General answers should abstain when the small curated corpus does not cover the requested detail. Conversation state is client-supplied and not persisted by the backend.
