# PolyScript - Multi-Language Transcription Service

Multi-language speech-to-text (STT) transcription service with team-based access control, billing, and full localization.

## Features

- **Multi-language support**: 5 languages (en, de, es, fr, jp) for UI and transcripts
- **Team-based access**: Admin, member, and viewer roles with isolation
- **Job-based processing**: Async transcription via Redis queue
- **Admin panel**: Full system management for super admins
- **Billing**: Stripe integration with plans and credits
- **Export formats**: TXT, JSON, SRT, VTT
- **Edit history**: Track and revert transcript changes

## Architecture

\`\`\`mermaid
graph TB
    subgraph Frontend
        Web[apps/web]
        Admin[apps/admin]
        Marketing[apps/marketing]
    end
    
    subgraph Backend
        API[apps/api]
        Worker[apps/worker]
    end
    
    subgraph Shared
        UI[packages/ui]
    end
    
    subgraph Core_Layer
        Core[packages/core]
    end
    
    subgraph Storage_Layer
        DB[packages/storage/db]
        Redis[packages/storage/redis]
    end
    
    subgraph STT_Layer
        STT[packages/stt]
    end
    
    %% Frontend connections
    Web -->|auth| Core
    Web -->|HTTP, SSE| API
    Web --> UI
    Admin -->|admin auth| Core
    Admin -->|HTTP, SSE| API
    Admin --> UI
    Marketing -->|public| API
    
    %% Backend connections
    API --> Core
    API --> DB
    API --> Redis
    API --> STT
    Worker --> Redis
    Worker --> Core
    Worker --> DB
    Worker --> STT
    
    %% Data flow
    subgraph Data_Persistence
        PG[(PostgreSQL)]
        REDIS[(Redis)]
    end
    
    DB --> PG
    Redis --> REDIS
    Core --> DB
    Core --> Redis
    
    style Web fill:#e1f5ff
    style Admin fill:#e1f5ff
    style Marketing fill:#e1f5ff
    style API fill:#ffe1e1
    style Worker fill:#ffe1e1
    style Core fill:#e8f5e9
    style Storage_Layer fill:#fff3e0
    style STT_Layer fill:#fff3e0
    style UI fill:#f3e5f5
\`\`\`

### Apps (Bun + TypeScript)

- \`apps/web\` — Vite + React web application for authenticated users
- \`apps/admin\` — Vite + React admin panel for super admin system management
- \`apps/marketing\` — Astro static marketing site (5 languages: en, de, es, fr, jp)
- \`apps/api\` — FastAPI HTTP API + SSE endpoints
- \`apps/worker\` — Background transcription worker service with dedicated event loop

### Packages (Python + uv)

- \`packages/core\` — Business logic services (auth, billing, teams, jobs)
- \`packages/storage/db\` — SQLAlchemy models + repositories
- \`packages/storage/redis\` — Redis client + queue primitives
- \`packages/stt\` — Speech-to-text engines + normalization layer

### Shared Package

- \`packages/ui\` — shadcn/ui component library (TypeScript, Bun)

## Local Development

### Prerequisites

- [Bun](https://bun.sh)
- [uv](https://github.com/astral-sh/uv)
- [PostgreSQL](https://www.postgresql.org/)
- [Redis](https://redis.io/)

### Setup

1. Clone the repo
2. Run \`bun install\` at the root
3. Copy \`.env.example\` to \`.env\` and fill in the values
4. Run \`uv sync\` in each Python app/package:
   \`\`\`bash
   cd apps/api && uv sync
   cd apps/worker && uv sync
   cd packages/core && uv sync
   cd packages/storage/db && uv sync
   cd packages/storage/redis && uv sync
   cd packages/stt && uv sync
   cd packages/ui && bun install
   \`\`\`
5. Set up PostgreSQL database and Redis
6. Run migrations:
   \`\`\`bash
   cd packages/storage/db && uv run alembic upgrade head
   \`\`\`

### Running Development Servers

- **Web app**: \`bun run web:dev\`
- **Admin panel**: \`bun run admin:dev\`
- **Marketing site**: \`bun run marketing:dev\`
- **API**: \`bun run api:dev\`
- **Worker**: \`bun run worker:dev\`

### Testing

\`\`\`bash
# Run all tests
bun run test

# Web tests
bun run web:test
bun run web:test:e2e

# Python package tests
bun run poly-core:dev  # core tests
bun run db:dev     # database tests
bun run poly-redis:dev  # redis tests
bun run stt:dev         # STT tests

# Linting
bun run lint
bun run lint:fix

# Formatting
bun run format
bun run format:check
\`\`\`

## Project Structure

\`\`\`
poly-script/
├── apps/
│   ├── api/          # FastAPI backend
│   ├── admin/        # Admin panel
│   ├── marketing/    # Marketing site
│   ├── web/          # Main web app
│   └── worker/       # Background worker
├── packages/
│   ├── core/         # Business logic
│   ├── storage/db/   # Database layer
│   ├── storage/redis/# Redis layer
│   ├── stt/          # STT engines
│   └── ui/           # UI components
├── app-spec.txt      # Technical specification (single source of truth)
└── package.json      # Root scripts
\`\`\`

## API Documentation

Once the API is running, access interactive API docs at:
- \`http://localhost:8000/docs\` (Swagger UI)
- \`http://localhost:8000/redoc\` (ReDoc)

## Environment Variables

See \`.env.example\` for required environment variables:
- Database connection
- Redis connection
- JWT secrets
- Stripe configuration
- Email server settings

## Deployment

See \`app-spec.txt\` for detailed deployment specifications.

## Development Guidelines

- Single source of truth: \`app-spec.txt\` (any conflicts: spec wins)
- Business logic in \`packages/core\`, API routes remain thin
- Multi-tenant isolation enforced at query level
- All errors localized based on \`Accept-Language\` header
- Soft delete pattern with configurable grace period

## License

[Your License Here]
