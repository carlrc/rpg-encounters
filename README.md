<p align="center">
    <a href="frontend/public/logo.png">
        <img src="frontend/public/logo.png" alt="rpg encounters logo" width="20%"/>
    </a>
</p>

<h2 align="center">
    <p>RPG Encounters</p>
</h2>

<div align="center">

[**Setup**](#setup) | [**Getting started**](#getting-started)

</div>

RPG Encounters is a program for adding AI RPG characters into your in-person tabletop sessions. It is designed for DMs to easily create characters with biases, memories, trust based secrets that players can selectively interact with. It is designed to replace encounters where the DM does not want to impersonate characters and instead introduce some variability, and free-form role play.

## Getting Started

- Check out some [media](./frontend/public/landing/assets/images/home/).
- Read the [game instructions](./frontend/public/instructions.md) to understand the mechanics and the default scenario.
- Follow the [setup guide](#setup) or use the [paid version](https://rpg-encounters.com).
- Test out talking to some characters!

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
