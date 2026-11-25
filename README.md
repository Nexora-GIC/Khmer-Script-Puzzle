# khmer-script-puzzle

Khmer word-building game for grade 1–2. One repo, four apps — each folder builds and deploys on its own.

| Folder | Stack | Job |
|---|---|---|
| `web/` | React + TypeScript (Vite) | Screens. No game calculation. |
| `api/` | NestJS (Fastify adapter) + Postgres (TypeORM) | Everything that isn't game logic. Only DB user, only engine caller. |
| `engine/` | Go + onnxruntime_go | All game logic + handwriting model. Stateless, private network. |
| `ml/` | Python | Model training + trial analysis. Never deployed. |

## How they connect
```
ml      ──model.onnx, labels.json, preprocess_cases.json──► engine
engine  ──api/engine.yaml (contract)──────────────────────► api   (npm run gen:engine)
api     ──openapi.json (@nestjs/swagger)──────────────────► web   (npm run gen:api)
api     ──content/words.json (copied at build)────────────► engine
api     ──GET /export/strokes─────────────────────────────► ml    (training data)
```

## Request flow (one answer)
browser → api `POST /attempts` → engine `POST /v1/attempts/judge` (child state in, new state out)
→ api saves attempt + strokes + guesses + versions → browser

## Deployment
- Machine 1: `api/docker-compose.yml` (api + Postgres + content files)
- Machine 2: engine (with model) — private network only, `Authorization: Bearer $ENGINE_KEY`

## Getting started

### Need installed
Go 1.26+, Node 22+, Docker, Python 3.11+

### 1. Setup (once)
```sh
cd engine && make test && cd ..
cd api    && npm i && cp .env.example .env && npm run gen:engine && cd ..
cd web    && npm i && cd ..
cd ml     && python3 -m venv .venv && .venv/bin/pip install -e . && cd ..
```

### 2. Run (3 terminals)
| Terminal | Command | Ready when you see |
|---|---|---|
| 1 — engine | `cd engine && make run` | `listening on :8080` |
| 2 — api | `cd api && docker compose up -d db && npm run start:dev` | `Nest application successfully started` |
| 3 — web | `cd web && npm run dev` | `Local: http://localhost:5173` |

First time only, once the api has started: `cd web && npm run gen:api` (typed api client).

### 3. Check it works
| Open | Expect |
|---|---|
| http://localhost:3100/health | `"engine":{"status":"ok", ...}` — stop the engine and it says `"down"` |
| http://localhost:3100/docs | Swagger page for the api |
| http://localhost:5173 | Web app; tab title = `APP_NAME` from `web/src/config.ts` |

### Ports
| Service | Port |
|---|---|
| web | 5173 |
| api | 3100 |
| engine | 8080 |
| Postgres | 5433 |

api and Postgres avoid 3000 / 5432 so they don't clash with other projects
(change with `API_PORT` / `DB_PORT` in `api/.env`).

### Good to know
- Always use `npm run ...`, not a global `nest` — it uses the project's own versions.
- `ENGINE_KEY=dev-key` works out of the box locally; use a long random value in production.
- TypeScript stays on 6 in api and web (`openapi-typescript` doesn't support 7 yet).
- Each folder's README has the details for that app.
- A change to `engine/api/engine.yaml` and the regenerated clients go in the same commit.
