# Worker Service

Standalone transcription worker service that processes jobs from the Redis queue.

## Running the Worker

```bash
cd apps/worker
python main.py
```

Or with uv:
```bash
cd apps/worker
/opt/homebrew/bin/uv run python main.py
```

## Architecture

- Runs as a separate process from the API
- Uses a dedicated consumer thread with its own event loop
- Subscribes to Redis queue `transcription:queue`
- Publishes progress to Redis pub/sub channel `job:{job_id}:progress`

## Shutdown

Gracefully shuts down on SIGINT (Ctrl+C) or SIGTERM, completing any currently processing job.
