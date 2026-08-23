# Evaluator-Generator AI Knowledge Platform

## Redis (caching)

The app caches retrieval results in Redis. Start it with Docker Compose --
no manual `docker run`, image pulls, or config needed:

```bash
docker compose up -d
```

This pulls the official `redis` image (if not already local) and starts it
on `localhost:6379`, matching the defaults in `.env.example`. Data persists
in a named Docker volume across restarts.

Check it's up:
```bash
docker compose ps
```

Stop it:
```bash
docker compose down
```

If Redis isn't running, the app still works -- caching just fails soft
(every retrieval becomes a cache miss, logged as a warning) instead of
crashing.

## Running the app

```bash
pip install -r requirements.txt
cp .env.example .env   # fill in your own values
uvicorn app:app --reload
```

Interactive API docs at `http://127.0.0.1:8000/docs`.

## Running tests

```bash
pytest tests/
```
