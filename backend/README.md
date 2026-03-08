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

Create `.env` file and set variables

```bash
cp .env.example .env
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
uv run python -m app.db.init_db

# Migrate 
uv run alembic -c alembic.ini upgrade head

# Seed defaults
uv run python -m tests.fixtures.seed_data

# Seed defaults for specific email
uv run python -m tests.fixtures.seed_data --email <USER_EMAIL>
```

Launch backend services following [usage instructions](../README.md) and verify with tests

```bash
uv run pytest
```

## Admin

Create migration revision

```bash
uv run alembic -c alembic.ini revision -m "describe_change"
```
