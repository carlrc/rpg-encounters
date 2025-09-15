# Backend

## Setup

Install [UV](https://docs.astral.sh/uv/getting-started/installation/) then setup the virtual environment

```bash
uv venv
```

Install ffmpeg (required for Whisper model)

```bash
# Ubuntu
sudo apt update && sudo apt install ffmpeg

# MacOS
brew install ffmpeg
```

Install PostgreSQL

```bash
apt install postgresql
```

Install [Docker](https://docs.docker.com/engine/install/) and verify

```bash
docker
```

Activate `venv`

```bash
source .venv/bin/activate
```

Sync project dependencies

```bash
uv sync
```

Install pre commit hooks and format files

```bash
pre-commit install
pre-commit run --all-files
```

Setup telemetry backend by cloning [langfuse](https://github.com/langfuse/langfuse) alongside this repo

```bash
git clone https://github.com/langfuse/langfuse.git
```

If you don't want telemetry, you can disable tracing with Langfuse and by removing it from the root docker compose file

```bash
LANGFUSE_TRACING_ENABLED=false
```

### DB Admin

Create db

```bash
createdb -h localhost -p 5432 -U postgres '${POSTGRES_DB}'
```

Create test db

```bash
createdb -h localhost -p 5432 -U postgres '${POSTGRES_DB}-test'
```

Create dev db tables

```bash
python -m app.db.init_db
```

Drop dev db tables

```bash
python -m app.db.init_db --drop
```

Create and seed test db with fixture data

```bash
python -m tests.fixtures.seed_data
```

Create and seed dev db with fixture data

```bash
python -m tests.fixtures.seed_data --dev
```

Trigger seed script inside docker container

```bash
docker exec -it rpg-encounters-backend python tests/fixtures/seed_data.py --dev
```

Drop docker volume

```bash
docker volume ls

docker volume rm <volume_name>
```

### Docker & ECR

Authenticate

```bash
aws ecr get-login-password --region eu-central-1 --profile build-admin | docker login --username AWS --password-stdin 255447701128.dkr.ecr.eu-central-1.amazonaws.com
```

Build image

```bash
sudo ./scripts/build.sh
```

Tag and push with versioning

```bash
sudo ./scripts/push.sh
```

## Debugging

Re-install local packages

```bash
sudo docker build --no-cache -f Dockerfile -t rpg-encounters-backend .
```

Get backend service logs

```bash
docker logs -f rpg-encounters-backend
```

Restart backend

```bash
docker-compose restart backend
```