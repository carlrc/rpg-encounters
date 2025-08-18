# Backend

## Installation

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

Create a `.env` file with the following keys in the `backend` directory

```bash
OPENAI_API_KEY={SERVICE_ACC_API_KEY}
ELEVENLABS_API_KEY={USER_API_KEY}
POSTGRES_USER=postgres
POSTGRES_PASSWORD=mysecretpassword
POSTGRES_DB=dnd-postgres
DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@localhost:5432/${POSTGRES_DB}
# Test Database (same server, different database name)
TEST_DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@localhost:5432/${POSTGRES_DB}-test
```

## Usage

Run docker

```bash
docker compose up -d
```

Create dev db

```bash
python -m app.db.init_db
```

Create and seed test db with fixture data

```bash
python -m tests.fixtures.seed_data
```

Create and seed dev db with fixture data

```bash
python -m tests.fixtures.seed_data --live
```

Run backend

```bash
python -m app.main
```

Stop docker

```bash
docker compose down -v
```
