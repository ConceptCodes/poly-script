---
title: Exports
description: Generate TXT, JSON, SRT, and VTT exports programmatically.
order: 3
lang: en
---

Transcripts can be exported in multiple formats. Use the API to generate downloads.

## Export formats

| Format | Content | Use case |
|--------|---------|----------|
| TXT | Plain text | Reports, documentation |
| JSON | Full metadata + segments | Processing, analytics |
| SRT | Subtitles with timing | Video players |
| VTT | Web captions | Browser playback |

## Generate an export

```bash
curl -X POST https://api.polyscript.io/v1/jobs/{job_id}/exports \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "format": "srt",
    "include_speakers": true
  }'
```

Response:

```json
{
  "id": "export-uuid",
  "format": "srt",
  "url": "https://storage.polyscript.io/exports/...",
  "expires_at": "2024-01-16T10:30:00Z"
}
```

## JSON structure

```json
{
  "language": "en",
  "segments": [
    {
      "text": "Hello world",
      "start": 0.0,
      "end": 1.5,
      "speaker": "S1",
      "confidence": 0.95
    }
  ]
}
```

Export URLs are signed and expire after 24 hours for security.
