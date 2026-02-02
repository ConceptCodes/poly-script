---
title: Building a multi-tenant STT pipeline
description: How we designed job isolation, retries, and export workflows.
pubDate: 2024-12-01
tags: ['launch', 'architecture']
lang: en
---

When we started building PolyScript, we knew reliability would be everything. Transcription jobs can take minutes to complete, users expect real-time progress, and teams need isolation at every layer.

## Design principles

Our pipeline follows three core principles:

1. **Queue-first architecture** — All jobs flow through Redis, allowing us to control throughput, retry failed work, and scale workers independently.
2. **Team-scoped data** — Every query is filtered by `team_id`, ensuring zero cross-team leakage.
3. **Idempotent workers** — Jobs can be safely retried without creating duplicate results or billing events.

## Job lifecycle

A transcription job moves through these states:

```
QUEUED → RUNNING → SUCCEEDED / FAILED / CANCELED
```

Workers pick jobs from Redis, update status in the database, and stream progress via SSE to connected clients.

## Retry strategy

We use exponential backoff with 3 max attempts. Failed jobs are tracked for debugging without blocking the queue.

## Export generation

Once a job succeeds, we generate TXT, JSON, SRT, and VTT formats on demand and cache them for fast downloads.

This architecture has proven stable at scale, with 97% of jobs succeeding within 24 hours.
