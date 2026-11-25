# web

React + TypeScript (Vite). Game screens, teacher dashboard, parent report.
Responsive: phone, tablet, laptop. Online only.

## Rules
- **No game calculation here.** The browser shows prompts, collects answers/strokes,
  sends them to the api, and shows what comes back.
- The handwriting canvas sends raw stroke points; recognition happens in the engine.
- Typed api client is generated from the api's `openapi.json` (`npm run gen:api`).
- Product name lives only in `src/config.ts` (`APP_NAME`).

## Setup (once)
```sh
npm i
npm run gen:api     # typed api client; needs the api started once (it writes ../api/openapi.json)
```

## Run
```sh
npm run dev         # http://localhost:5173 — /api/* is proxied to localhost:3100
```
TypeScript stays on 6 to match the api (see api README).

## Layout
| Folder | What |
|---|---|
| `src/features/game/modes/` | Match, Tap, Trace, Write |
| `src/features/game/canvas/` | pointer events → stroke points |
| `src/features/game/audio/` | prompt audio playback |
| `src/features/auth/` | teacher/parent login, child picker |
| `src/features/dashboard/`, `report/` | teacher dashboard, parent report |
| `src/api/generated/` | generated client types (gitignored) |
| `src/i18n/` | Khmer + English UI labels |
| `public/fonts/` | Khmer font |
