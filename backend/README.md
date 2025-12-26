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
# Ubuntu
apt install postgresql

# MacOS
brew install postgresql
```

Install [Docker](https://docs.docker.com/engine/install/) and verify installation

```bash
docker
```

Activate `venv`

```bash
source .venv/bin/activate
```

Install project dependencies. Specify either `cpu` or `gpu`.

```bash
# Pytorch w/ CPU
uv sync --extra cpu

# Pytorch w/ GPU
uv sync --extra gpu
```

Install pre commit hooks and format files

```bash
pre-commit install
pre-commit run --all-files
```

If you don't want telemetry with [langfuse](https://github.com/langfuse/langfuse), you can disable using the following `.env` variable

```bash
LANGFUSE_TRACING_ENABLED=false
```

## Admin

<details>
<summary>Click for helpful test & debugging commands</summary>

### DB Commands

Create db

```bash
# Dev db
createdb -h localhost -p 5432 -U postgres 'rpg-encounters'

# Test db
createdb -h localhost -p 5432 -U postgres 'rpg-encounters-test'
```

Manage db tables

```bash
# Create
python -m app.db.init_db

# Delete
python -m app.db.init_db --drop
```

Create and seed db with fixture data

```bash
# Seed db with default users
python -m tests.fixtures.seed_data

# Seed defaults to user
python -m tests.fixtures.seed_data --email <USER_EMAIL>

# Seed in docker container
sudo docker exec -it rpg-encounters-backend python tests/fixtures/seed_data.py
```

Launch only the database

```bash
docker-compose -f backend/docker-compose.yml -f backend/docker-compose.dev.yml up db
```

### Debugging

Rebuild dev image after dependency changes (e.g., new libs)

```bash
# Rebuild the dev image (dependencies stage) without cache
sudo docker compose -f docker-compose.dev.yml build --no-cache backend

# Recreate the container using the freshly built image
sudo docker compose -f docker-compose.dev.yml up --force-recreate
```

Reset docker env

```bash
# Stop all containers
sudo docker stop $(sudo docker ps -aq)

# Remove all containers
sudo docker rm $(sudo docker ps -aq)

# Remove all images
sudo docker rmi $(sudo docker images -q) --force

# Remove all volumes
sudo docker volume prune -f
```
