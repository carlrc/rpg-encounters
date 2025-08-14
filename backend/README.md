# Backend

## Usage

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

Populate `.env`

```bash
OPENAI_API_KEY=
ELEVENLABS_API_KEY=
POSTGRES_USER=postgres
POSTGRES_PASSWORD=mysecretpassword
POSTGRES_DB=dnd-postgres
DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@localhost:5432/${POSTGRES_DB}
```

Setup docker

```bash
docker compose up -d
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
```

Run backend

```bash
python -m app.main
```
