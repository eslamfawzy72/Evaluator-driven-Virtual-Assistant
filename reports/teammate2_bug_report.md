# Code Review Notes — Generator/Evaluator side

Found while reviewing the integration point (`retrieve()` -> your `services/`
code) after your latest commits (`5f6a14b`, `8955268`, `0cf53eb`). Nothing here
blocks your design — the architecture (agents, isolated memories, orchestrator
loop) matches the spec well. These are concrete bugs/gaps worth fixing before
the demo.

---

## 1. `tests/test_llm.py` breaks the entire test suite (highest priority)

```python
# tests/test_llm.py
response = llm_service.chat(
    "What is Natural Language Processing?"
)
```

`LLMService.chat(self, system_message, user_message)` requires two arguments.
This call only passes one, so it binds to `system_message` and leaves
`user_message` missing.

Because this call sits at **module level** (not inside a `def test_...():`
function), it runs the moment pytest tries to *collect* the file — before any
test even starts — and raises:

```
TypeError: LLMService.chat() missing 1 required positional argument: 'user_message'
```

This aborts collection for the **whole `pytest tests/` run**, not just this
file — right now nobody can run the full suite with one command.

**Fix:** wrap it in a real test function and pass both arguments, e.g.:

```python
def test_llm_chat_returns_response():
    llm_service = LLMService()
    response = llm_service.chat(
        system_message="You are a helpful assistant.",
        user_message="What is Natural Language Processing?",
    )
    assert response
```

Same issue exists in `test_generator.py`, `test_evaluator.py`,
`test_generator_memory.py`, `test_evaluator_memory.py`, `test_orchestrator.py`
— they're all `def main(): ... if __name__ == "__main__":` scripts, not
pytest tests, so pytest silently collects **0 test cases** from them (no
crash, but no coverage either). Worth converting the useful ones into real
`test_` functions with assertions.

---

## 2. Evaluator has no protection against non-JSON LLM output

```python
# services/evaluator_agent.py
try:
    evaluation = EvaluationResult.model_validate(json.loads(response))
except (json.JSONDecodeError, ValueError) as exc:
    raise ValueError(f"Invalid evaluator response:\n{response}") from exc
```

The system prompt tells the model "return ONLY JSON, no markdown fences" —
but smaller open models (you're using `Qwen/Qwen3-8B`) very commonly ignore
that and wrap the JSON in ` ```json ... ``` `, or add a leading/trailing
sentence. There's no stripping/extraction step before `json.loads()`, so any
deviation raises `ValueError` instead of being handled.

**Fix:** strip code fences before parsing, e.g.:
```python
response = response.strip()
if response.startswith("```"):
    response = response.strip("`").removeprefix("json").strip()
```
Consider also a one-retry-on-parse-failure before giving up.

---

## 3. Orchestrator has zero error handling around LLM calls

```python
# services/orchestrator.py :: QAOrchestrator.run()
answer = self.generator.generate_answer(...)
evaluation = self.evaluator.evaluate(...)
```

Neither call is wrapped in try/except. Any failure — the JSON bug above, an
HF endpoint timeout, a rate limit, network blip — propagates straight up and
crashes the whole request. Per Shared Task 3 in the spec ("LLM/API
failures... errors should not crash the whole application"), this needs a
try/except per iteration that either retries or fails that iteration
gracefully (e.g. treat as REJECT with a generic feedback message) rather than
raising out of `run()`.

---

## 4. Debug `print()` left in `evaluator_agent.py`

```python
print("\n=== RAW EVALUATOR RESPONSE ===")
print(repr(response))
```

Should go through `logging` (per Shared Task 4 in the spec) instead of a bare
`print`, so it can be turned off/redirected like the rest of the app's logs.

---

## 5. No short-circuit for empty retrieval context

`rag/retriever.py::retrieve()` returns `[]` (never raises) when nothing
relevant is found. Right now `QAOrchestrator.run()` doesn't check for that —
it sends the empty context straight into the Generator and runs the full
4-iteration loop anyway. Per the spec's "Unknown Question Handling" task, an
empty context should short-circuit immediately to something like:

```
The required information is not available in the provided sources.
```

instead of spending 4 LLM round-trips on a question you already know has no
supporting knowledge.

---

## 6. Minor — decision casing differs from the spec's example

The spec's example JSON uses `"decision": "ACCEPT"` (uppercase); your code
uses lowercase `"accept"`/`"reject"` consistently everywhere (`EvaluatorAgent`,
`EvaluatorMemory`, `QAOrchestrator`). Not currently broken since it's
internally consistent, but flag it now in case a future UI or grader expects
the spec's literal casing.

---

## Suggested priority

1. Fix `tests/test_llm.py` (blocks the whole suite)
2. Add orchestrator-level error handling (#3) — demo-crash risk
3. Harden JSON parsing in the evaluator (#2)
4. Convert the manual demo scripts into real tests
5. Empty-context short-circuit (#5)
6. Swap `print` for `logger` (#4)
