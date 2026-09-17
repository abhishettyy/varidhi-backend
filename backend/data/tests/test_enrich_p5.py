from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from backend.data.enrich_p5 import SYNTHETIC_FIELDS, enrich_file, enrich_rows


ROOT = Path(__file__).resolve().parents[3]
INPUT = ROOT / "data" / "processed" / "p5_demo.json"


class EnrichP5Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.real_rows = json.loads(INPUT.read_text(encoding="utf-8"))
        cls.enriched_rows = enrich_rows(cls.real_rows, seed=1234)

    def test_preserves_all_real_observations(self):
        for row in self.real_rows:
            group = next(item for item in self.enriched_rows
                         if item["valid_time"] == row["valid_time"]
                         and item["latitude"] == row["latitude"]
                         and item["longitude"] == row["longitude"])
            self.assertEqual(group["data"][row["variable"]], row["value"])
        self.assertEqual(len(self.real_rows), 30)
        self.assertEqual(len(self.enriched_rows), 3)

    def test_adds_every_missing_field_per_group(self):
        groups = {(row["valid_time"], row["latitude"], row["longitude"]) for row in self.real_rows}
        for group in groups:
            output = next(row for row in self.enriched_rows
                          if (row["valid_time"], row["latitude"], row["longitude"]) == group)
            variables = set(output["data"])
            self.assertTrue(set(SYNTHETIC_FIELDS) <= variables)

    def test_synthetic_rows_are_provenanced_and_bounded(self):
        for output in self.enriched_rows:
            self.assertEqual(output["real_field_count"], 10)
            self.assertEqual(output["synthetic_field_count"], 7)
            for variable, (_, low, high, _) in SYNTHETIC_FIELDS.items():
                entry = output["field_provenance"][variable]
                self.assertEqual(entry["source"], "synthetic-enrichment")
                self.assertEqual(entry["quality"], "synthetic")
                self.assertTrue(entry["provenance"]["details"]["synthetic"])
                self.assertEqual(entry["provenance"]["details"]["seed"], 1234)
                self.assertGreaterEqual(output["data"][variable], low)
                self.assertLessEqual(output["data"][variable], high)

    def test_same_seed_produces_same_rows(self):
        self.assertEqual(enrich_rows(self.real_rows, seed=77), enrich_rows(self.real_rows, seed=77))
        self.assertNotEqual(enrich_rows(self.real_rows, seed=77), enrich_rows(self.real_rows, seed=78))

    def test_file_pipeline_writes_json(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "p5_data.json"
            enrich_file(INPUT, output, seed=9)
            rows = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(len(rows), 3)
            self.assertTrue(all(len(row["data"]) == 17 for row in rows))
            self.assertTrue(all(row["synthetic_field_count"] == 7 for row in rows))


if __name__ == "__main__":
    unittest.main()
