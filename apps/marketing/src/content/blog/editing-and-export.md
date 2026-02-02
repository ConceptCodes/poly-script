---
title: Designing for editing and export
description: Patterns for clean, fast transcript review loops.
pubDate: 2024-12-15
tags: ['product', 'ux']
lang: en
---

A raw transcription is rarely perfect. Teams need to edit, verify, and export in formats that match their workflow.

## Editing experience

Our editor is designed around three principles:

1. **Timecode-aligned navigation** — Click any segment to jump to that moment in the audio.
2. **Speaker detection** — Auto-identify speakers and allow manual labeling.
3. **Conflict-free collaboration** — Multiple users can edit different regions simultaneously.

## Normalization

Before the editor loads, we normalize all engine outputs:

- Segments: Consistent duration ranges (2-8 seconds)
- Timestamps: Aligned to nearest 100ms
- Punctuation: Applied via post-processing model
- Casing: Sentence case with proper noun detection

This means switching STT providers doesn't break your workflow.

## Export formats

We support four formats out of the box:

- **TXT** — Clean text for reports and docs
- **JSON** — Full metadata with segments, timestamps, and confidence
- **SRT** — Subtitle format with timing
- **VTT** — Web-compatible captions

Exports are generated on-demand and cached for fast repeated downloads.

## Future work

We're exploring:

- Diff-based version control for transcripts
- Inline translations for multi-language content
- Custom export templates via JSON schema
