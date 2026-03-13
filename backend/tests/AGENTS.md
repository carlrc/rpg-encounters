# Backend Tests Guide

## Scope

- This folder contains backend test suites split by scope:
- `unit/`: isolated logic tests
- `integration/`: DB and downstream service integration
- `end_to_end/`: API and websocket contract tests

## How To Run

Run all backend tests from `backend/`:

- `uv run pytest tests -q`

Run a specific suite:

- `uv run pytest tests/unit -q`
- `uv run pytest tests/integration -q`
- `uv run pytest tests/end_to_end -q`

Run a specific file:

- `uv run pytest tests/end_to_end/test_canvas_connections_flow.py -q`

## Fixtures

- Reuse existing helpers in `tests/end_to_end/utils.py` for authenticated clients.
- Seed data with existing factories from `tests/fixtures/generate.py` (`default_*`) and store writes.

## Conventions

- Keep tests async where the suite is async.
- Keep assertions explicit in each test function (status/body/close code).
- Prefer local monkeypatching in test files over introducing shared helper modules.
- Do not add new shared helper modules unless explicitly requested.
- Follow existing scenario ID and naming style used in the current suite.
