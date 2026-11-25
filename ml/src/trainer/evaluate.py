"""Check how well a model recognises single pieces.

Run it FIRST on the existing Hugging Face models as they are. Only fine-tune if the
result isn't good enough, then run it again and compare with --baseline.

Data layout — one folder per piece, folder name = the piece's text:
    data/pieces/ក/001.png
    data/pieces/្ល/001.png        (a leading ◌ in the folder name is fine, it's ignored)
    data/pieces/ា/001.png

Examples:
    python -m trainer.evaluate chakkhu   data/pieces
    python -m trainer.evaluate mengheang data/pieces --lm
    python -m trainer.evaluate onnx      data/pieces --model out/model.onnx \\
        --labels out/labels.json --baseline out/eval/<best-model>.json

Prints overall accuracy, the worst pieces and the most common confusions, and saves
out/eval/<name>.json (summary, usable as --baseline later) and out/eval/<name>.csv
(every prediction).

The two Hugging Face models are line/word OCR, not piece classifiers, so this tests them
on something they weren't built for. Expect lone subscripts and vowels to be the weak spot.

SECURITY: the chakkhu and mengheang adapters import Python code that ships inside the
Hugging Face repo (that's how those models are meant to be used). Read that file once,
then pass --revision <commit> so you always run the code you read.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import time
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, Sequence

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".webp"}
BATCH = 32
# Don't change what the child wrote: dotted circle (used to show a lone vowel/subscript),
# zero-width space / non-joiner / joiner. Whitespace is dropped too.
_IGNORE = {"◌", "​", "‌", "‍"}


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFC", text)
    return "".join(ch for ch in text if ch not in _IGNORE and not ch.isspace())


# ---------------------------------------------------------------- models

class Predictor(Protocol):
    name: str

    def predict(self, paths: Sequence[Path]) -> list[str]: ...


def _hf_folder(repo: str, revision: str | None) -> str:
    from huggingface_hub import snapshot_download

    if revision is None:
        print(f"warning: {repo} not pinned — pass --revision <commit>", file=sys.stderr)
    folder = snapshot_download(repo, revision=revision)
    sys.path.insert(0, folder)
    return folder


class ChakkhuOCR:
    """muyleanging/Chakkhu-OCR-Khmer-ONNX — line OCR on ONNX Runtime, Apache-2.0.
    This repo is ONNX only; for fine-tuning see the original muyleanging/Chakkhu-OCR-Khmer."""

    repo = "muyleanging/Chakkhu-OCR-Khmer-ONNX"

    def __init__(self, revision: str | None, fp32: bool = False):
        folder = _hf_folder(self.repo, revision)
        from chakkhu_onnx import Chakkhu  # ships in the repo

        self.ocr = Chakkhu(folder, int8=not fp32)
        self.name = "chakkhu-fp32" if fp32 else "chakkhu"

    def predict(self, paths):
        return [str(t) for t in self.ocr.read([str(p) for p in paths])]


class MengheangOCR:
    """mengheang/khmer-handwritten-ocr — handwriting CRNN+CTC in PyTorch, CC-BY-NC.
    Has safetensors weights, so it could be fine-tuned directly."""

    repo = "mengheang/khmer-handwritten-ocr"

    def __init__(self, revision: str | None, use_lm: bool = False):
        folder = _hf_folder(self.repo, revision)
        from khmer_ocr import KhmerOCR  # ships in the repo

        self.ocr = KhmerOCR(folder)
        self.use_lm = use_lm
        self.name = "mengheang-lm" if use_lm else "mengheang"

    def predict(self, paths):
        return [str(self.ocr.read(str(p), use_lm=self.use_lm)) for p in paths]


class OnnxClassifier:
    """Our fine-tuned piece classifier: model.onnx (input (B,1,64,64), output (B,n) scores)
    + labels.json (list of n piece strings, same order as the output)."""

    def __init__(self, model: Path, labels: Path):
        import onnxruntime as ort

        self.sess = ort.InferenceSession(str(model), providers=["CPUExecutionProvider"])
        self.input = self.sess.get_inputs()[0].name
        self.labels = json.loads(Path(labels).read_text(encoding="utf-8"))
        self.name = Path(model).stem

    def predict(self, paths):
        import numpy as np

        from .preprocess import load_image

        x = np.stack([load_image(p) for p in paths]).astype(np.float32)
        scores = self.sess.run(None, {self.input: x})[0]
        return [self.labels[i] for i in scores.argmax(axis=1)]


# ---------------------------------------------------------------- evaluation

@dataclass
class Row:
    path: str
    truth: str
    raw: str
    pred: str

    @property
    def correct(self) -> bool:
        return self.pred == self.truth


def collect(data_dir: Path, limit: int | None = None) -> list[tuple[Path, str]]:
    samples = []
    for d in sorted(p for p in data_dir.iterdir() if p.is_dir()):
        files = sorted(f for f in d.iterdir() if f.suffix.lower() in IMAGE_EXTS)
        samples += [(f, normalize(d.name)) for f in files[:limit]]
    if not samples:
        raise SystemExit(f"no images found under {data_dir}/<piece>/")
    return samples


def run(predictor: Predictor, samples: list[tuple[Path, str]]) -> tuple[list[Row], float]:
    rows, start = [], time.perf_counter()
    for i in range(0, len(samples), BATCH):
        chunk = samples[i : i + BATCH]
        preds = predictor.predict([p for p, _ in chunk])
        rows += [Row(str(p), t, raw, normalize(raw)) for (p, t), raw in zip(chunk, preds)]
    ms = (time.perf_counter() - start) * 1000 / len(samples)
    return rows, ms


def summarize(name: str, rows: list[Row], ms_per_image: float) -> dict:
    per: dict[str, list[bool]] = defaultdict(list)
    for r in rows:
        per[r.truth].append(r.correct)
    confusions = Counter((r.truth, r.pred) for r in rows if not r.correct)
    return {
        "name": name,
        "samples": len(rows),
        "accuracy": sum(r.correct for r in rows) / len(rows),
        "empty_rate": sum(r.pred == "" for r in rows) / len(rows),
        "ms_per_image": round(ms_per_image, 2),
        "per_piece": {
            k: {"n": len(v), "accuracy": sum(v) / len(v)} for k, v in sorted(per.items())
        },
        "confusions": [[t, p, n] for (t, p), n in confusions.most_common(30)],
    }


def _show(s: str) -> str:
    return s if s else "∅"


def report(summary: dict, baseline: dict | None = None, top: int = 15) -> str:
    out = [
        f"== {summary['name']}: {summary['samples']} images, "
        f"{len(summary['per_piece'])} pieces",
        f"accuracy   {summary['accuracy']:.1%}",
        f"empty      {summary['empty_rate']:.1%}",
        f"speed      {summary['ms_per_image']} ms/image",
        "",
        f"worst {top} pieces:",
    ]
    worst = sorted(summary["per_piece"].items(), key=lambda kv: kv[1]["accuracy"])[:top]
    out += [f"  {k}\t{v['accuracy']:.0%}\t(n={v['n']})" for k, v in worst]
    out += ["", f"top {top} confusions (wrote → read as):"]
    out += [f"  {t} → {_show(p)}\t×{n}" for t, p, n in summary["confusions"][:top]]

    if baseline:
        d = summary["accuracy"] - baseline["accuracy"]
        out += ["", f"vs {baseline['name']}: {baseline['accuracy']:.1%} → "
                f"{summary['accuracy']:.1%} ({d:+.1%})"]
        both = summary["per_piece"].keys() & baseline["per_piece"].keys()
        deltas = sorted(
            ((k, summary["per_piece"][k]["accuracy"] - baseline["per_piece"][k]["accuracy"])
             for k in both),
            key=lambda kv: kv[1],
        )
        out += ["  biggest drops: " + "  ".join(f"{k} {v:+.0%}" for k, v in deltas[:5])]
        out += ["  biggest gains: " + "  ".join(f"{k} {v:+.0%}" for k, v in deltas[-5:][::-1])]
    return "\n".join(out)


def save(summary: dict, rows: list[Row], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = out_dir / summary["name"]
    stem.with_suffix(".json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    with stem.with_suffix(".csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["path", "truth", "raw_output", "prediction", "correct"])
        w.writerows([r.path, r.truth, r.raw, r.pred, int(r.correct)] for r in rows)


# ---------------------------------------------------------------- cli

def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("model", choices=["chakkhu", "mengheang", "onnx"])
    ap.add_argument("data", type=Path, help="folder with one subfolder per piece")
    ap.add_argument("--revision", help="Hugging Face commit to pin (chakkhu/mengheang)")
    ap.add_argument("--fp32", action="store_true", help="chakkhu: fp32 instead of int8")
    ap.add_argument("--lm", action="store_true", help="mengheang: use its language model")
    ap.add_argument("--model", dest="onnx_model", type=Path, help="onnx: model.onnx")
    ap.add_argument("--labels", type=Path, help="onnx: labels.json")
    ap.add_argument("--limit", type=int, help="max images per piece")
    ap.add_argument("--baseline", type=Path, help="earlier summary .json to compare with")
    ap.add_argument("--name", help="name for the saved results (default: model name)")
    ap.add_argument("--out", type=Path, default=Path("out/eval"))
    a = ap.parse_args(argv)

    if a.model == "chakkhu":
        predictor: Predictor = ChakkhuOCR(a.revision, fp32=a.fp32)
    elif a.model == "mengheang":
        predictor = MengheangOCR(a.revision, use_lm=a.lm)
    else:
        if not (a.onnx_model and a.labels):
            ap.error("onnx needs --model and --labels")
        predictor = OnnxClassifier(a.onnx_model, a.labels)

    rows, ms = run(predictor, collect(a.data, a.limit))
    summary = summarize(a.name or predictor.name, rows, ms)
    baseline = json.loads(a.baseline.read_text(encoding="utf-8")) if a.baseline else None
    print(report(summary, baseline))
    save(summary, rows, a.out)
    print(f"\nsaved {a.out / summary['name']}.json and .csv")


if __name__ == "__main__":
    main()
