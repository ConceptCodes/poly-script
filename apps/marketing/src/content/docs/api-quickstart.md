---
title: API Quickstart
description: Create jobs, stream progress, and retrieve results with the REST API.
order: 1
lang: en
---

The PolyScript API provides full control over transcription jobs. This guide will get you running in minutes.

## Authentication

All API requests require a Bearer token:

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.polyscript.io/v1/jobs
```

## Create a job

```bash
curl -X POST https://api.polyscript.io/v1/jobs \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "audio_url": "https://example.com/audio.mp3",
    "language": "en"
  }'
```

Response:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "QUEUED",
  "language": "en",
  "created_at": "2024-01-15T10:30:00Z"
}
```

## Stream progress

Subscribe to job progress via SSE:

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.polyscript.io/v1/jobs/550e8400-e29b-41d4-a716-446655440000/progress
```

Events:

```json
{"type": "progress", "percent": 45, "stage": "transcribing"}
{"type": "completed", "segments": 142}
```

## Retrieve results

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.polyscript.io/v1/jobs/550e8400-e29b-41d4-a716-446655440000/transcript
```

Response includes full transcript, segments, and timing information.

## Rate limits

- Free: 5 jobs/day
- Standard: 25 jobs/day
- Pro: Unlimited
