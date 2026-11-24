# Backend audit and migration plan

## Audit (2026-11-24)

### Current architecture

- `app.py` creates the Flask app and registers `/api/chat` and `/api/health`.
- `routes/` validates the chat payload and translates service failures to HTTP responses.
- `services/chatbot_service.py` orchestrates scope classification, symptom extraction, fuzzy analysis, and Ollama response generation.
- `services/ollama_service.py` is the local HTTP client; model, URL, and timeouts come from `config.py` / environment variables.
- `utils/text_normalizer.py` supplies slang normalization and deterministic symptom lexicons.
- `fuzzy/` separates membership functions and rules, with scikit-fuzzy control inference and centroid defuzzification.
- `knowledge_base/acne_knowledge.json` contains recommendations and safety copy, but has no source metadata or verification status. It is not yet an evidence-backed RAG corpus.
- The Vite frontend posts `{ "message": string }` to `/api/chat` and expects `{ "ok": boolean, "reply": string }`; `/api/health` returns `{ "backend": boolean, "ollama": boolean }`.
- Dependencies are Flask, Flask-CORS, Requests, NumPy, scikit-fuzzy, and python-dotenv. Existing tests use unittest and mock Ollama; pytest and Pydantic are not installed in the inspected environment.

### Findings and risks

1. A normal in-scope chat can call Ollama for scope scoring, symptom extraction, and answer generation (three sequential calls).
2. General skincare questions with no lexicon symptom are routed to a symptom clarification instead of an educational answer.
3. LLM symptom extraction accepts any JSON object, clamps malformed/out-of-range values, and merges by taking the maximum with the lexicon. This can turn an unmentioned or negated symptom into a positive fuzzy input.
4. Missing symptom dimensions are silently replaced with score `2`, so the fuzzy result implies observations the user did not provide.
5. Fuzzy inputs are clipped to 0–10 rather than rejected; `recommend()` also assumes comparable numeric values.
6. The system prompt constrains generation, but there is no post-generation evidence or safety validation. Existing advice has no citations/source metadata.
7. `scope_filter.llm_score()` turns Ollama failures into score zero, which can misclassify relevant questions as out of scope.
8. Error responses preserve frontend compatibility and avoid returning stack traces. Request size is limited to 32 KB at Flask level and messages to 4,000 characters.
9. Existing fuzzy rules and membership functions are separated and deterministic in intent; tests cover key labels and parameter endpoints. There is no retrieval, evidence evaluation, extraction schema, or integration with a verified knowledge corpus.

## Migration plan

1. Preserve existing endpoints and fuzzy parameters/rules. Add strict boundary validation and observable deterministic behavior before changing architecture.
2. Separate intent/scope decisions from symptom extraction; general questions should not enter symptom analysis. Keep a deterministic lexicon fallback and treat absent symptoms as unknown.
3. Add typed structured schemas for requests, extracted symptoms, evidence metadata, and responses. Limit retries and fail closed to the lexicon when extraction is invalid.
4. Curate source metadata and reviewed content from primary medical sources before enabling retrieval. Do not represent the current unsourced JSON as verified evidence.
5. Add local document ingestion, hybrid retrieval, evidence-grounded generation, and conservative post-generation checks as independently testable services.
6. Add decision thresholds only after evaluation data and baselines exist; record retrieval, abstention, safety, latency, and resource metrics.
7. Keep Ollama optional for deterministic/offline tests, keep secrets out of source control, and preserve the frontend API response shape.

## Implementation status

The audit confirms this repository is already partially modular. The initial implementation preserves its endpoints and existing fuzzy membership functions/rules, adds Pydantic request/symptom/fuzzy/evidence/response schemas, prevents missing or negated symptoms from becoming positive fuzzy scores, and routes educational questions through reviewed-source retrieval. Retrieval uses local BM25 with optional Ollama embedding reranking/RRF over lexical candidates; if the embedding model is absent it falls back to BM25. Symptom analysis output is deterministic and the LLM cannot rewrite its fuzzy result.

The current evidence set is intentionally small. Full semantic search independent of keyword matching, persistent vector storage, document ingestion/update tooling, source deletion APIs, a broad evaluation dataset, confidence calibration, and an end-to-end hallucination/faithfulness metric remain later migration work. The current post-generation check is a narrow guard against obvious unsafe language and fabricated bracketed IDs, not a general hallucination detector. Existing recommendation text in `acne_knowledge.json` also remains legacy, unsourced content and should not be treated as verified evidence.
