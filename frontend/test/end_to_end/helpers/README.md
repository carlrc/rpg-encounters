# Playwright Helper Rules

1. Use deterministic seeded fixtures (name/ID resolution), not probe loops or first-visible targeting.
2. Share setup logic in helpers when reused by more than one spec.
3. Resolve base URL from Playwright config; never hard-code host/port.
4. Start network waits before actions and assert method, path, and status.
5. Register extra browser contexts and always close them in `finally`.
6. Non-audio tests must fail when seeded prerequisites are broken; do not skip-mask.
7. `test.skip(...)` is allowed only for audio gates: WebKit microphone limitation and `ENCOUNTERS_AUDIO_TEST` env gating.
