# RPG Encounters Agents Overview

## Source Code

- The backend code is in `./backend` directory
- The frontend code is in `./frontend` directory
- The infrastructure code is in `./infra` directory

## Architecture

### Backend

- FastAPI entrypoint is `backend/app/main.py`; HTTP surface area is organized as routers in `backend/app/routers/*` (health check at `/internal/health`).
- Persistence is Postgres with async SQLAlchemy in `backend/app/models` + `backend/app/db`, wired via `DATABASE_URL` (`asyncpg`) and typically run via Docker Compose.
- AI/voice features live in `backend/app/agents` and `backend/app/services` (Whisper transcription + TTS providers).

### Frontend

- Vue 3 SPA built with Vite; routes are in `frontend/src/router/index.js` and shared client state is in Pinia stores under `frontend/src/stores`.
- The app calls backend APIs under `/api/*` (designed to sit behind the same origin as the SPA) and relies on cookie/session-based auth flows for protected routes.
- UI is component-driven (`frontend/src/components`) with heavier interaction views under `frontend/src/views` (e.g., encounter/canvas uses `@vue-flow/*`).

### Infra

- Infrastructure is defined in CDKTF (`infra/main.ts`) and provisions a public VPC, ALB, and a single EC2 instance; access is intended via SSM (no SSH ingress).
- Delivery uses CloudFront as the edge: default origin is the frontend S3 website bucket and `/api/*` routes to the ALB; CloudFront injects an `X-Origin-Auth` header and applies a geo whitelist.
- Terraform state is stored in S3 (`rpg-encounters-state`); deployments assume manually created ACM certs (ALB in `eu-central-1`, CloudFront in `us-east-1`) and DNS params sourced from SSM.
