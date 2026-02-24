# RPG Encounters

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

Local development uses `backend/docker-compose.dev.yml` to add a local Postgres container and Adminer.
Production uses only `backend/docker-compose.yml`, connects to RDS, and includes RedisInsight.
