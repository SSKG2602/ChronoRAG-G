import csv
import unittest
from pathlib import Path

from chronorag_public.results import PUBLIC_METRICS, assert_public_metrics, percent


ROOT = Path(__file__).resolve().parents[1]


class ResultsAssetTests(unittest.TestCase):
    def test_public_metric_invariants(self):
        assert_public_metrics(dict(PUBLIC_METRICS))

    def test_percent_precision(self):
        self.assertEqual(percent(811, 1005), 80.6965)

    def test_table_triplets(self):
        stems = sorted(path.stem for path in (ROOT / "tables").glob("*.csv"))
        self.assertEqual(len(stems), 17)
        for stem in stems:
            self.assertTrue((ROOT / "tables" / f"{stem}.md").exists())
            self.assertTrue((ROOT / "tables" / f"{stem}.tex").exists())

    def test_figure_triplets(self):
        stems = sorted(path.stem for path in (ROOT / "figures").glob("*.svg") if path.name[:2].isdigit())
        self.assertEqual(len(stems), 8)
        for stem in stems:
            self.assertTrue((ROOT / "figures" / f"{stem}.png").exists())
            self.assertTrue((ROOT / "figures" / f"{stem}.pdf").exists())

    def test_overall_answer_table_value(self):
        with (ROOT / "tables" / "01_overall_answer.csv").open(newline="", encoding="utf-8") as handle:
            row = next(csv.DictReader(handle))
        self.assertEqual(row["accepted"], "811")
        self.assertEqual(row["rejected"], "194")
        self.assertEqual(row["denominator"], "1005")


if __name__ == "__main__":
    unittest.main()
