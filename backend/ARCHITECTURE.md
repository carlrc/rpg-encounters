# Token Usage Flow

- Postgres is source of truth and Redis is runtime cache.
- If user token cache is missing, backend hydrates Redis from Postgres.
- Runtime writes/checks are handled by `UserTokenService`.
- Persisted table/model/store stay as `user_billing` in this phase.
