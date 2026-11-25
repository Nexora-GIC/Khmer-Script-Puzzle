# ml

Python. **Never deployed.** Two jobs:

1. **Handwriting model** — start from an existing Hugging Face model, check it as-is,
   and only fine-tune a bit if needed (~64×64 piece image → ~80 piece scores).
   Then hand three files to the engine:
   | File | Goes to |
   |---|---|
   | `out/model.onnx` | `engine/models/` |
   | `out/labels.json` | `engine/models/` |
   | `out/preprocess_cases.json` | `engine/internal/recognize/testdata/` |
2. **Trial analysis** (`analysis/`) — pre/post gains, t-test / Mann-Whitney, learning curves,
   from the api's exports.

## Candidate models
| Model | What | Licence | Can fine-tune? |
|---|---|---|---|
| `muyleanging/Chakkhu-OCR-Khmer-ONNX` | line OCR, CNN+Transformer+CTC, ONNX | Apache-2.0 | Not this repo (ONNX only) — check the original `muyleanging/Chakkhu-OCR-Khmer` |
| `mengheang/khmer-handwritten-ocr` | handwriting line/word OCR, CRNN+CTC, PyTorch | CC-BY-NC | Yes (safetensors) |

No model is chosen yet — pick after running evaluate on both.
Both load through Python code shipped in their repo, not `transformers`.
Read that file once and pin `--revision <commit>`.

## Data (gitignored, in `data/`)
- `pieces/<piece>/*.png` — one folder per piece, folder name = the piece's text (for evaluate/train)
- `kid_strokes/` — from the api's `GET /export/strokes` (collect mode)
- `synthetic/` — optional, from `synth.py` (font-rendered pieces)
- `raw/` — anything downloaded

## Setup
```sh
python3 -m venv .venv && . .venv/bin/activate
pip install -e .              # enough for Chakkhu + our own ONNX model
pip install -e '.[torch]'     # mengheang, fine-tuning, export
pip install -e '.[analysis]'  # trial analysis
python -m unittest discover -s tests
```

## Pipeline
```sh
# 1. Check the models as they are
python -m trainer.evaluate chakkhu   data/pieces --revision <commit>
python -m trainer.evaluate mengheang data/pieces --revision <commit>

# 2. Only if that's not good enough: fine-tune a bit, then compare
python -m trainer.synth                     # optional
python -m trainer.train
python -m trainer.export_onnx
python -m trainer.evaluate onnx data/pieces --model out/model.onnx \
    --labels out/labels.json --baseline out/eval/<best-model>.json

# 3. Hand-off to the engine
python -m trainer.make_test_cases
```
Each evaluate run prints accuracy, worst pieces and top confusions (e.g. ្ល → ្រ),
and saves `out/eval/<name>.json` + `.csv`.
`preprocess.py` and the engine's `preprocess.go` must match exactly — `make_test_cases` is how that's enforced.
