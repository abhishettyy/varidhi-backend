from __future__ import annotations

import unittest

from fastapi.testclient import TestClient

from backend.p5.api import create_app
from backend.p5.source import CompleteP5DataSource, P5Query


class CompleteP5SourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = CompleteP5DataSource()
        cls.client = TestClient(create_app(cls.source))

    def test_complete_source_has_three_zones(self):
        self.assertEqual(len(self.source.zones()), 3)
        self.assertEqual(self.source.describe()["dataset_file"].replace("\\", "/").split("/")[-1], "p5_data.json")

    def test_supported_fields_are_queryable(self):
        for record_type in ("sst", "chlorophyll", "wind", "wave", "swell", "tide", "currents"):
            response = self.source.query(record_type, P5Query(zone_ids=["ZONE_001"]))
            self.assertEqual(response.status, "success", record_type)
            self.assertEqual(len(response.records), 1, record_type)
            self.assertEqual(response.records[0]["metadata"]["dataset"], "p5_data.json")

    def test_unsupported_fields_are_explicitly_unavailable(self):
        response = self.source.query("pfz")
        self.assertEqual(response.status, "unavailable")
        self.assertEqual(response.records, [])

    def test_http_endpoint_uses_complete_contract(self):
        response = self.client.get("/p5/v1/wave", params={"zone_id": "ZONE_001"})
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["status"], "success")
        self.assertEqual(body["records"][0]["metadata"]["dataset"], "p5_data.json")


if __name__ == "__main__":
    unittest.main()
