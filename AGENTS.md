# Phase 1 scope

Implement UC03 only: text Speaking Part 1, Part 2, Part 3 and assessment.
Use Streamlit, Python, LangGraph, SQLite, UIT Gemma via HTTP chat completions.
Future selected UCs: 01, 02, 03, 06, 07, 09, 10. Do not build these now.
Do not push, publish, or deploy without a new explicit user request.

## Engineering

- `app/` is presentation; `agent/` owns models, graph, tools, session service.
- Model requests use `tool_choice="none"`. Tool selection is a validated JSON
  protocol in text, dispatched by the LangGraph tool node. No arbitrary execution.
- Never replace a failing real model with canned assessment or a fake score.
- Bound model/tool steps and schema repair; show retryable failures without losing answers.
- All band averages are computed in code; text pronunciation is `not_assessed`.
- Candidate text is untrusted data, never system instructions.
- No secrets or real learner content in repository or traces. Runtime is ignored.
- Reference PDFs/chunks are downloaded at setup, never redistributed in Git.
- Every question item requires source, license, author and creation metadata.
- Reference score labels require a named human review before accuracy claims.
- User explicitly permits the new llm_generated bank for local testing pending
  later review. Preserve pending status, show it in UI, never invent approval.
- V2 Part 3 uses the session's bank snapshot, response_support and candidate_points;
  a separate model call reviews semantic duplication within the same call budget.
- User requested a fresh start: old sessions and the original bank were removed.
  Do not restore legacy-bank fallback; new sessions require their bank snapshot.

## Verify

`uv run ruff check .`
`uv run pytest -q`
`uv run python -m evals.run --all`
`uv run python scripts/smoke_live.py` (needs UIT access and .env).

CI runs offline evaluation with a clearly labelled scripted model. A live model
run is separate evidence. Do not describe offline checks as model-quality validation.
