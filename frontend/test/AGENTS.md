# Frontend Tests Guide

## Setup Features

DM auth bootstrap helpers are in `test/end_to_end/helpers/bootstrapDm.ts`:

- `bootstrapDmSession()` creates a reusable authenticated DM session fixture.
- `applyDmSession(page, session)` injects that session into a Playwright page context.

Spec-scoped session caching is in `test/end_to_end/helpers/specDm.ts`:

- `getSpecDmSession(testInfo)` gives one stable session per spec file.

API response helpers are in `test/end_to_end/helpers/networkAsserts.ts`:

- `waitForApiResponse(...)` wraps common request/response waiting + assertion flow.

## How To Use

For authenticated E2E specs, follow the existing pattern:

- `beforeAll(getSpecDmSession)` then `beforeEach(applyDmSession)`.
- For tests that mutate auth/account state (logout/delete), create an isolated session with `bootstrapDmSession()` to avoid cross-test leakage.
- Prefer existing network wait patterns (`waitForApiResponse` or `page.waitForResponse`) instead of adding new helpers.
- In unit tests, use `vi.hoisted` + `vi.mock` for module-level dependency mocks, then set behavior per test in `beforeEach`/`it`.

## Invocation Gates

- `ENCOUNTERS-CHALLENGE-SKILL-GATE-01` exists to enforce a product invariant: in challenge mode, `Speak` must stay disabled until a skill is selected, then re-disable if the skill is cleared.
- This test stays in the normal `encounters.spec.ts` flow (not `@audio` gated) because it protects a core UI/state contract, not microphone or websocket transport behavior.
- Keep this gate to prevent regressions where challenge calls are triggered without required challenge inputs (`skill`, then `d20_roll` path setup).
