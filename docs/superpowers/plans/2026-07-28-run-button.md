# Run Button Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Run code from the lesson editor and display its output without changing runner security limits.

**Architecture:** Add a small `POST /api/code/run` wrapper around `run_code(code, [])`. Preserve the runner's AST filter and two-second subprocess timeout, while returning its captured stdout and execution error. The existing editor sends to that endpoint and renders the returned output below the editor.

**Tech Stack:** FastAPI, Pydantic, SQLite app, vanilla JavaScript, CSS, pytest.

## Global Constraints

- Work only in `/root/projects/python-path` on `feat/run-button`; never commit directly to `main`.
- Keep the current AST safety filter, isolated subprocess, 5,000-character source cap, and 2-second timeout unchanged.
- Do not add dependencies or delete project files.

---

### Task 1: Add API regression tests

**Files:**
- Modify: `tests/test_api.py`

**Interfaces:**
- Consumes: `POST /api/code/run` JSON `{ "code": str, "question_id": str | null }`.
- Produces: assertions for `{stdout, stderr, error, timed_out}`.

- [ ] **Step 1: Write failing tests**

```python
response = client.post("/api/code/run", json={"code": "print('hi')"})
assert response.json()["stdout"] == "hi\n"

response = client.post("/api/code/run", json={"code": "import os"})
assert response.json()["error"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_api.py -q`
Expected: FAIL because `/api/code/run` does not exist.

### Task 2: Implement and render code execution

**Files:**
- Modify: `app/evaluator.py`
- Modify: `app/main.py`
- Modify: `app/static/app.js`
- Modify: `app/static/styles.css`

**Interfaces:**
- Consumes: `run_code(source, tests)` with `tests=[]`.
- Produces: `POST /api/code/run` response `{stdout, stderr, error, timed_out}` and a `.code-output` block.

- [ ] **Step 1: Preserve runner data**

```python
return {"stdout": payload.get("stdout", ""), "stderr": result.stderr,
        "error": payload.get("error"), "timed_out": False}
```

- [ ] **Step 2: Add endpoint and UI event handler**

```python
@app.post("/api/code/run")
def run_code_endpoint(payload: CodeRun) -> dict:
    result = run_code(payload.code, [])
    return {
        "stdout": result.get("stdout", ""),
        "stderr": result.get("stderr", ""),
        "error": result.get("error"),
        "timed_out": result.get("timed_out", False),
    }
```

- [ ] **Step 3: Run focused tests then full suite**

Run: `uv run pytest tests/test_api.py -q && uv run pytest`
Expected: PASS.

- [ ] **Step 4: Commit and push**

```bash
git add -A
git commit -m "feat: run button with stdout output (P0.1)"
git push -u origin feat/run-button
```
