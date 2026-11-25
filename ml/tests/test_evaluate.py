"""Tests for the scoring logic, using a fake model (no downloads, no ML libraries)."""
import tempfile
import unittest
from pathlib import Path

from trainer.evaluate import collect, normalize, report, run, summarize


class FakeModel:
    name = "fake"

    def __init__(self, answers):  # file name → what the "model" reads
        self.answers = answers

    def predict(self, paths):
        return [self.answers[p.name] for p in paths]


class EvaluateTest(unittest.TestCase):
    def test_normalize_ignores_dotted_circle_and_spaces(self):
        self.assertEqual(normalize("◌្ល"), "្ល")
        self.assertEqual(normalize(" ក​ "), "ក")

    def test_scores_and_confusions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            files = {"ក": ["a.png", "b.png"], "◌្ល": ["c.png", "d.png"], "ា": ["e.png"]}
            for piece, names in files.items():
                (root / piece).mkdir()
                for n in names:
                    (root / piece / n).write_bytes(b"")
            (root / "ក" / "notes.txt").write_text("ignored")

            model = FakeModel(
                {"a.png": "ក", "b.png": "ក", "c.png": "្រ", "d.png": "្ល", "e.png": ""}
            )
            samples = collect(root)
            self.assertEqual(len(samples), 5)

            rows, _ = run(model, samples)
            s = summarize("fake", rows, 1.0)

        self.assertAlmostEqual(s["accuracy"], 3 / 5)
        self.assertAlmostEqual(s["empty_rate"], 1 / 5)
        self.assertEqual(s["per_piece"]["្ល"]["accuracy"], 0.5)
        self.assertIn(["្ល", "្រ", 1], s["confusions"])

        base = dict(s, name="before", accuracy=0.2)
        text = report(s, base)
        self.assertIn("accuracy   60.0%", text)
        self.assertIn("+40.0%", text)


if __name__ == "__main__":
    unittest.main()
