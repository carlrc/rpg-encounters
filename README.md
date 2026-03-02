<h1 align="center">
  <img src="frontend/public/logo.png" width="40" style="vertical-align: middle;"/>
  RPG Encounters
</h1>

RPG Encounters is a program for adding AI RPG characters into your in-person tabletop sessions. It is designed for DMs, whereby characters can be configure to have biases, memories, trust based secrets that can make your sessions more interactive. It is designed to allow your players to perform free-form role play with any characters you don't wish to impersonate yourself.

## Setup

- Follow `backend` [setup guide](./backend/README.md)
- Follow `frontend` [setup guide](./frontend/README.md)

## Usage

Launch frontend

```bash
npm run dev
```

Launch backend services

```bash
docker compose -f backend/docker-compose.yml -f backend/docker-compose.dev.yml up
```

### Login

Because the application uses magic links in production, locally you need to:

- Set backend env var `LOG_MAGIC_LINK=true`
- Seed the database with a user and email
- Request login link
- Copy login link from backend service logs, which looks something like: `test1@example.com login link: http://localhost:3001/auth?token=e-e6Cs6paxa6H0fmC0gYfrwfLElxWwkeSF0Jb6ck-XY`
- Paste login link into the same browser session used to request it

### Avoiding Token Checks

When you BYOKs, you can avoid token checks by either:

- Setting backend env var `BILLING_IGNORE_BALANCE_CHECK=true` to skip all checks
- Adjusting token balances with the script in `backend/tests/scripts/set_billing_state.py`:

```python
cd backend
REDIS_URL=redis://localhost:6379/0 uv run python tests/scripts/set_billing_state.py \
  --email test1@example.com \
  --available 100000 \
  --last-used 0
```

### Avoiding Moderation

When you BYOKs, you can avoid moderation by:

- Setting backend env var `SKIP_MODERATION=true`
