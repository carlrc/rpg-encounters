# Backend

## Usage

Install [UV](https://docs.astral.sh/uv/getting-started/installation/) then setup the virtual environment

```bash
uv venv
```

Install system level dependencies

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Activate `venv`

```bash
source .venv/bin/activate
```

Sync project dependencies

```bash
uv pip sync
```

Install pre commit hooks

```bash
pre-commit install
```

Run backend

```bash
python -m app.main
```