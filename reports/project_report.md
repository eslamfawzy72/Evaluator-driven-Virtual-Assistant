# Evaluator–Generator AI Knowledge Platform — Project Report

**Date:** 2026-08-22
**Repo:** `Evaluator-driven-Virtual-Assistant` (branch `main`)

## 1. Project Summary

An AI-powered Q&A platform built around an **Evaluator–Generator workflow**. Users
supply knowledge (PDF, DOCX, TXT, source code, PPT, URLs, Wikipedia, WAV audio); the
system ingests it into a vector store, retrieves relevant chunks for a question, and
runs a Generator LLM → Evaluator LLM feedback loop (max 4 iterations) to produce a
validated, grounded answer.

## 2. Architecture

```
Source (file/URL/topic)
   -> ingest() -> loader (per type) -> chunking -> embeddings -> Chroma vector store
                                                                        |
Question -> retrieve(question, k) [Redis cache -> similarity search] -> context
                                                                        |
                                          context + question -> Generator LLM -> answer
                                                                        |
                                                    answer + context -> Evaluator LLM -> decision
                                                            ACCEPT -> final answer
                                                            REJECT -> feedback -> Generator (repeat, max 4x)
```

## 3. Team Split

| | Responsibility |
|---|---|
| **Teammate 1** | Knowledge ingestion (all source types) + chunking + embeddings + vector store + `retrieve()` + Redis cache for retrieval |
| **Teammate 2** | Generator/Evaluator LLM agents, isolated memories, feedback loop, iteration limit, `run_workflow()` |

Integration contract:
```python
context = retrieve(question)                     # Teammate 1 -> Teammate 2
result  = run_workflow(question, context)         # Teammate 2's output
```

---

## 4. Teammate 1 — Status: Complete (Priority 1 + Priority 3)

### Ingestion — all 8 source types implemented and tested

| Source | File | Status |
|---|---|---|
| TXT | `ingestion/txt_loader.py` | ✅ tested |
| PDF | `ingestion/pdf_loader.py` | ✅ tested |
| DOCX | `ingestion/docx_loader.py` | ✅ tested |
| Source code (~20 languages) | `ingestion/code_loader.py` | ✅ tested |
| PPT/PPTX | `ingestion/ppt_loader.py` | ✅ tested |
| URL | `ingestion/url_loader.py` | ✅ tested (+ invalid/unreachable URL handling) |
| Wikipedia | `ingestion/wikipedia_loader.py` | ✅ tested (+ missing-page handling) |
| WAV (speech-to-text) | `ingestion/audio_loader.py` (faster-whisper) | ✅ tested |

Routing: `ingestion/file_router.py` auto-detects type (URL scheme / file extension /
fallback-to-Wikipedia) and dispatches via a lookup table, so adding a new format never
requires touching the dispatch logic itself.

### RAG pipeline

- **Chunking** — `rag/chunking.py`: `RecursiveCharacterTextSplitter`, chunk_size=1000,
  overlap=200, metadata preserved per chunk.
- **Embeddings** — `rag/embeddings.py`: local `sentence-transformers/all-MiniLM-L6-v2`
  (no API key required).
- **Vector store** — `rag/vector_store.py`: Chroma, persisted to `CHROMA_PERSIST_DIR`.
- **Retrieval** — `rag/retriever.py`: `retrieve(question, k=4)` → the integration
  contract:
  ```python
  [{"content": "...", "source": "project.pdf"}]
  ```
  Never raises — returns `[]` on empty/failed retrieval, which is what lets the
  Generator side detect "no relevant knowledge found."

### Caching

- `cache/redis_cache.py`: caches retrieval results (SHA-256 of question+k → JSON,
  1-hour TTL). Fails soft — if Redis is unreachable, every call becomes a no-op cache
  miss instead of raising.
- **Not yet verified against a live Redis server** — logic is complete and covered by
  the fail-soft path, but a real cache-hit has not been observed end-to-end.

### Configuration

- `config/settings.py`: centralizes all env-var-driven config (Redis host/port/db,
  Chroma persist dir/collection name) behind `load_dotenv()` + a `Settings` dataclass.
  Both `redis_cache.py` and `vector_store.py` consume this instead of reading
  `os.getenv` directly.

### Testing

11 automated tests, all passing (`tests/test_*_ingestion.py`):
ingest → retrieve round-trip for every source type, plus explicit error-handling
tests (invalid URL scheme, unreachable domain, empty/nonexistent Wikipedia topic).

A dedicated `tests/conftest.py` isolates the test vector store (temp directory + a
per-run unique Chroma collection name) from the real persisted knowledge base, so
repeated test runs don't accumulate duplicate content that pollutes retrieval
assertions.

### Known gaps / not yet done

- Redis caching not verified against a real running Redis instance.
- File-upload UI (Shared Task 1) not started.
- `langchain_community.PyPDFLoader` emits a deprecation warning (community package
  being sunset) — not urgent, but should migrate to the standalone package eventually.

---

## 5. Teammate 2 — Status: In progress

Based on the current repo state (`services/` directory, commits `5f6a14b`, `8955268`,
`0cf53eb`):

| Component | File | Status |
|---|---|---|
| LLM service | `services/llm_service.py` | Implemented (uses `Qwen/Qwen3-8B` via Hugging Face, not the Anthropic API originally scaffolded in `.env.example`) |
| Generator agent | `services/generator_agent.py` | Implemented |
| Generator memory | `services/generator_memory.py` | Implemented |
| Evaluator agent | `services/evaluator_agent.py` | Implemented |
| Evaluator memory | `services/evaluator_memory.py` | Implemented |
| Orchestrator (feedback loop) | `services/orchestrator.py` | Implemented |

### Testing status

- `tests/test_generator.py`, `test_evaluator.py`, `test_generator_memory.py`,
  `test_evaluator_memory.py`, `test_orchestrator.py` are **manual demo scripts**
  (`def main(): ... if __name__ == "__main__":`), not automated pytest tests — pytest
  collects 0 test cases from these files. They're useful for manual smoke-testing but
  don't run as part of `pytest tests/`.
- `tests/test_llm.py` has a **collection-time bug**: it calls `llm_service.chat(...)`
  at module import level with a missing required argument (`user_message`), which
  raises `TypeError` during test collection and blocks `pytest tests/` from collecting
  *any* tests unless it's excluded or fixed. This should be converted into a real
  `test_*` function.

### Not yet verified

- The 4-iteration max loop, ACCEPT/REJECT structured evaluator output, and isolated
  Generator/Evaluator memories exist in code but have not been demonstrated against
  the automated test suite (no passing pytest coverage yet for this side).

---

## 6. Shared Tasks — Status

| Task | Status |
|---|---|
| User Interface | ❌ Not started |
| Integration contract (`retrieve` → `run_workflow`) | ✅ Contract defined and implemented on Teammate 1's side; consumption confirmed via `tests/test_generator.py`'s manual script, which calls `retrieve()` directly |
| Error handling & validation | ✅ Done for ingestion side; unclear for Generator/Evaluator side |
| Logging | ✅ `utils/logging_config.py` + logging throughout ingestion; not yet called from a central `app.py` (no `app.py` exists yet) |
| Testing (6 minimum tests from spec) | Partial — ingestion tests (Test 1, part of Test 3) covered; Test 2 (correct answer), Test 4 (feedback loop), Test 5 (max iterations), Test 6 (Redis cache hit) not yet automated |

---

## 7. Overall Next Steps

1. **Fix `tests/test_llm.py`** — currently breaks `pytest tests/` collection entirely;
   needs to be a real `test_` function, not a module-level script.
2. **Verify Redis end-to-end** — run a real Redis instance and confirm a cache hit is
   observed (Test 6).
3. **Convert Teammate 2's manual demo scripts into real pytest tests** so the full
   suite can be run with one command and CI/automation becomes possible.
4. **Build `app.py`** — the main entry point wiring `retrieve()` → `run_workflow()` →
   display, per the Shared Task 2 contract. Currently the two sides are integrated
   only ad hoc via manual scripts.
5. **Build the UI** (Shared Task 1) — file upload, URL/Wikipedia input, question box,
   results display (answer, validation status, iteration count, feedback).
6. **Commit and push** outstanding local changes regularly to keep both teammates in
   sync.
