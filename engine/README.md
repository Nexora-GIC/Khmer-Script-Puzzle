# engine

Go service with **all game logic and calculation**: reads handwriting with the model,
judges answers, scores tracing, updates mastery/confusions, picks the next word,
decoys, mode and hints, awards stars and unlocks, and builds practise recommendations.

## Rules
- **Stateless / pure.** No database. The api sends the child's state with every call and
  stores the new state the engine returns. Same request → same response, so retries are safe.
- **Only the api calls it.** Runs on a private network; every call needs
  `Authorization: Bearer $ENGINE_KEY` (except `/healthz`).
- **Contract first.** `api/engine.yaml` is the source of truth. Change it → `make gen`
  here and `npm run gen:engine` in the api.
- Every response includes `engineVersion`, `modelVersion` and `contentVersion`.

## Inputs copied in at build (gitignored)
| File | From |
|---|---|
| `models/model.onnx`, `models/labels.json` | `ml/out/` |
| `internal/recognize/testdata/preprocess_cases.json` | `ml/out/` (committed — it's the test fixture) |
| `content/words.json` | `api/content/words.json` |

A new model or content = copy the file + restart. Never during the trial.

## Run
```sh
make test
make run            # ENGINE_KEY=dev-key, listens on :8080
curl localhost:8080/healthz
```
