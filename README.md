# RPG Encounters

## Usage

### Local

Launch backend services

```bash
sudo docker compose -f docker-compose.dev.yml up
```

Stop backend services

```bash
sudo docker compose -f docker-compose.dev.yml down
```

Start frontend

```bash
npm run dev
```

Re-install local packages (e.g., new .venv)

```bash
sudo docker compose -f docker-compose.dev.yml build --no-cache backend
```