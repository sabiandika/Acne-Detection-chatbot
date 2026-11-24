# Ollama request trace and reliability fixes

## Request path

1. `POST /api/chat` accepts a Pydantic-validated `{message}` payload only. Extra `history` fields are rejected; each request gets a random request ID for logs. The response remains `{ok, reply}`.
2. `chatbot_service.process()` calls `scope_filter.classify_intent()` before any model call. This is deterministic and routes unrelated, unsafe medical, emergency, application, general education, and symptom-analysis requests.
3. Out-of-scope, unsafe, emergency, and application requests return deterministic text without calling Ollama. Symptom requests use the deterministic normalized lexicon. Unknown symptoms trigger clarification. Complete symptom inputs go through Fuzzy Mamdani and are rendered by Python; fuzzy data never enters an LLM prompt.
4. General education requests retrieve verified documents using BM25 and optional Ollama embeddings. The Ollama messages always begin with the dedicated `SYSTEM_PROMPT`, contain only the current user question as a user message, and place retrieved evidence in a separate system message. There is no prior assistant output or history in this prompt.
5. Ollama must return JSON matching `GeneratedAnswer`. Source IDs must be among the retrieved document IDs; answer text must pass unsafe-language, URL/citation, question relevance, and evidence vocabulary checks. A failed parse or validation gets at most one corrective retry, then a fixed safe fallback. Raw model text is never returned unvalidated.

## What the trace found

- The old `classify()` fused a keyword score with an LLM score. A mistaken scope score could admit unrelated text. Scope decisions now use explicit deterministic cues; there is no LLM scope vote.
- The previous generation prompt was short and put the question and evidence in one user message. It lacked explicit domain, injection, medical safety, and output schema rules. It now uses a dedicated system prompt and separate message roles.
- The earlier output checker only rejected a few unsafe phrases and unknown bracketed IDs. It did not check question overlap or whether answer terms existed in evidence. Validation now adds those checks and uses one bounded retry.
- No conversation history was ever sent by the frontend or backend. There was no system-prompt overwrite or cross-conversation history leak. The client keeps display messages locally, but sends only the current message. The API remains stateless to preserve that frontend contract and prevent assistant hallucinations from becoming trusted history.

## Ollama request configuration

- Model remains `gemma3:4b`; base URL and 120-second timeout remain environment-configurable.
- `temperature=0.1`, `top_p=0.8`, `top_k=20`, and `repeat_penalty=1.1` reduce generation variation/repetition for factual short answers. `num_predict=300` bounds output length.
- Streaming stays disabled so the complete structured response can be parsed and validated before returning it.
- `num_ctx` is not forced; Ollama keeps the model default to avoid imposing extra memory use on unknown hardware.
- Prompt/output debug logging is off by default and only activates when both `FLASK_DEBUG=true` and `OLLAMA_DEBUG_LOGS=true`. Regular logs record request ID, intent, message length, model, prompt size, output size, and latency, not user text.

## Limits

Scope cues do not understand every phrasing or misspelling. The validator is deterministic and conservative, but lexical support cannot prove semantic entailment. General answers should abstain when the small curated corpus does not cover the requested detail. Follow-up context is unavailable until the frontend sends a conversation ID and selected recent turns; this pass intentionally does not change the frontend.
