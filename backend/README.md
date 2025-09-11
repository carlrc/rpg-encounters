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

## Local Testing

Run docker

```bash
docker compose up -d
```

Create test db

```bash
createdb -h localhost -p 5432 -U postgres dnd-postgres-test
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

Run backend

```bash
python -m app.main
```

Stop docker

```bash
docker compose down -v
```

## Docker & ECR Deployment

Build image:

```bash
./scripts/build.sh
```

Authenticate with ECR

```bash
aws ecr get-login-password --region eu-central-1 --profile build-admin | docker login --username AWS --password-stdin 255447701128.dkr.ecr.eu-central-1.amazonaws.com
```

Tag image

```bash
sudo docker tag <IMAGE_ID> 255447701128.dkr.ecr.eu-central-1.amazonaws.com/crc-cicd-ecr-prd-repo:latest
```

Push image

```bash
sudo docker push 255447701128.dkr.ecr.eu-central-1.amazonaws.com/crc-cicd-ecr-prd-repo:latest
```