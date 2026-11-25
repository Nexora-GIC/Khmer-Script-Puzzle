# api

NestJS on the **Fastify adapter** + PostgreSQL (TypeORM). Everything that isn't game logic:
auth, parent codes, permissions, classes/children/consent, saving sessions/attempts/strokes,
dashboard & report data, exports, serving content files.

## Rules
- The **only** service that touches Postgres and the **only** caller of the engine.
- All engine calls go through `src/engine/engine.service.ts` (2 s timeout, 1 retry, auth header).
- Engine is a pure function: send the child's stored state, save the state it returns.
  `attemptId` is a unique column, so a repeated attempt is stored once.
- Schema changes only via migrations (`synchronize: false`):
  `npm run migration:generate -- src/db/migrations/<Name>` then `npm run migration:run`.
  Entities live next to their module as `*.entity.ts`.
- If the engine is down: still save the attempt, return "can't check right now".
- `content/` is the source of truth for game content; `words.json` is copied into the engine at build.

## Setup (once)
```sh
npm i
cp .env.example .env
npm run gen:engine        # typed engine client from ../engine/api/engine.yaml
```

## Run
```sh
docker compose up -d db   # Postgres on port 5433
npm run start:dev         # http://localhost:3100/health, Swagger at /docs
```
Always use `npm run ...` (not a global `nest`), so the project's own versions are used.

Note: TypeScript stays on 6 — `openapi-typescript` doesn't support 7 yet
(`overrides` in package.json lets it share TypeScript 6 with Nest).

## Layout
| Folder | What |
|---|---|
| `src/engine/` | EngineModule — generated client types + EngineService |
| `src/db/` | TypeORM data source (shared by app + CLI), `migrations/` |
| `src/auth`, `classes`, `children` | accounts, classes, children, consent, parent codes |
| `src/play/` | sessions + `POST /attempts` → engine |
| `src/dashboard`, `reports` | teacher dashboard + parent report |
| `src/samples`, `export` | training data collection + exports for analysis |
| `src/health/` | `/health`, `/version` |
| `content/` | words.json, audio, pictures (served at `/content/`) |
