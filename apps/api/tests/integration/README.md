# End-to-End Integration Tests

This directory contains integration tests that verify the full flow:

1. Web app (apps/web) → API (apps/api)
2. API enqueues job → Redis queue
3. Worker (apps/worker) dequeues job
4. Worker transcribes using STT (packages/stt)
5. Worker saves transcript to DB
6. SSE progress streaming to web app

To run these tests:
```bash
cd apps/api
uv run pytest tests/integration/
```

Prerequisites:
- PostgreSQL database running
- Redis server running
- All services (API, Worker) started

Test fixtures are used for isolated test data.
