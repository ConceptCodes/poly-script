---
title: Monitoring transcription at scale
description: Our approach to SSE progress streams and queue metrics.
pubDate: 2024-12-10
tags: ['ops', 'monitoring']
lang: en
---

Running a transcription service means keeping track of thousands of concurrent jobs. Here's how we maintain visibility without drowning in noise.

## Progress streams

Every job emits Server-Sent Events (SSE) as it processes:

- `started` — Job picked up by worker
- `progress` — Percentage complete with current stage
- `completed` — All segments written, exports ready
- `failed` — Error with reason code

Clients subscribe once and get real-time updates without polling.

## Queue metrics

We track these metrics at the infrastructure level:

- Queue depth (Redis `LLEN`)
- Worker throughput (jobs/minute)
- Average processing time by engine
- Error rate by failure reason

These feed into our dashboards and alert on anomalies.

## Correlation IDs

Every request, job, and log line carries:

- `request_id` — From API to worker
- `job_id` — Job UUID
- `team_id` — For multi-tenant filtering

This makes debugging distributed issues straightforward.

## Alert strategy

We alert on:

- Queue depth > 1000 for > 5 minutes
- Error rate > 5% over 10 minutes
- Worker not responding for > 60 seconds

Everything else is handled via automated retries and soft degrades.
