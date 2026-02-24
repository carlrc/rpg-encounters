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

Create dbs

```bash
# Dev db
createdb -h localhost -p 5432 -U postgres 'rpg-encounters'

# Test db
createdb -h localhost -p 5432 -U postgres 'rpg-encounters-test'
```

Manage db

```bash
# Create
python -m app.db.init_db

# Migrate 
uv run alembic -c alembic.ini upgrade head

# Seed defaults
python -m tests.fixtures.seed_data

# Seed defaults for specific email
python -m tests.fixtures.seed_data --email <USER_EMAIL>
```

Ensure backend services are running and verify with tests

```bash
uv run pytest
```

## Admin

<details>
<summary>Click for helpful test & debugging commands</summary>

### DB Commands

Create migration revision

```bash
uv run alembic -c alembic.ini revision -m "describe_change"
```

### Docker Commands

Rebuild dev image after dependency changes (e.g., new libs)

```bash
sudo docker compose -f backend/docker-compose.yml -f backend/docker-compose.dev.yml build --no-cache backend
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
