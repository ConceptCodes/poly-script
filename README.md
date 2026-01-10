# PolyScript

Multi-Language Transcription Service.

## Architecture

### Apps
- `apps/web`: Vite + React web application
- `apps/admin`: Vite + React admin panel
- `apps/marketing`: static Astro marketing site
- `apps/api`: FastAPI HTTP API
- `apps/worker`: Background worker service

### Packages
- `packages/ui`: Shared shadcn/ui component library
- `packages/core`: Business logic services
- `packages/storage/db`: SQLAlchemy models + repositories
- `packages/storage/redis`: Redis client + queue primitives
- `packages/stt`: Speech-to-text engines

## Local Development

### Prerequisites
- [Bun](https://bun.sh)
- [uv](https://github.com/astral-sh/uv)
- [PostgreSQL](https://www.postgresql.org/)
- [Redis](https://redis.io/)

### Setup
1. Clone the repo
2. Run `bun install` at the root
3. Copy `.env.example` to `.env` and fill in the values
4. Run `uv sync` in each Python app/package

## Deployment
!> Coming soon