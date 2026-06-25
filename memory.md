# Memory — GitScribe Neo4j & OpenRouter Integration

Last updated: 2026-06-24T20:38:00+05:30

## What was built

* Custom node types (`added` and `removed`) mapped in `frontend/src/app/page.tsx` to render the custom `FileNode` components correctly in React Flow.
* Integrated OpenRouter API into the backend LangGraph agents (`senior.py`, `critic.py`, `judge.py`) using `ChatOpenAI`.
* Resolved parameter warnings by passing `extra_body` configuration at the constructor level.

## Decisions made

* Chose OpenRouter as the primary LLM provider to access reasoning models (e.g. Gemma 4) and bypass free-tier rate limits.
* Kept the parsing database (Neo4j) deterministic (extracting AST nodes via Tree-sitter) while using LangGraph LLMs strictly for evaluation and critique of the extracted relationships and diffs.

## Problems solved

* Fixed a bug where React Flow nodes with statuses `"added"` and `"removed"` were displaying as plain text boxes instead of themed `FileNode` components.
* Handled OpenRouter reasoning state persistence across conversation turns using `reasoning_details`.

## Current state

* Local AST repository ingestion (`ingest_repo.py`) successfully parses files and builds `:IMPORTS` relationships in Neo4j.
* The API endpoints in `api.py` run background processing and support status polling from the client.
* Both frontend (`npm run dev`) and backend (`uvicorn`) development environments are fully functional.

## Next session starts with

1. Extending repository ingestion to handle arbitrary GitHub URLs rather than just the local `frontend/src` directory.
2. Building a repository/git helper to download/clone repos dynamically and clean up temporary paths post-ingestion.

## Open questions

* Do we want to support parsing other languages (e.g. Python, Go) or keep it strictly TypeScript/JavaScript for now?
* How should we handle public/private repository authentication for git operations?
