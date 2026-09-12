from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

from data.models import MarineObservation, Provenance
from data.normalization import exact_shared_timestamps, group_by_time_and_location


class NormalizationTests(unittest.TestCase):
    def observation(self, timestamp):
        return MarineObservation(
            "x", 1.0, "1", 12.5, 74.75, timestamp, timestamp,
            "test", "test", "valid", Provenance("test", "test", "x", "1")
        )

    def test_exact_temporal_matching_only(self):
        timestamp = datetime(2023, 1, 1, 12, tzinfo=timezone.utc)
        other = timestamp + timedelta(hours=1)
        self.assertEqual(exact_shared_timestamps([self.observation(timestamp)], [self.observation(timestamp)]), [timestamp])
        self.assertEqual(exact_shared_timestamps([self.observation(timestamp)], [self.observation(other)]), [])

    def test_group_by_time_and_location(self):
        timestamp = datetime(2023, 1, 1, 12, tzinfo=timezone.utc)
        grouped = group_by_time_and_location([self.observation(timestamp), self.observation(timestamp)])
        self.assertEqual(len(grouped), 1)
        self.assertEqual(len(next(iter(grouped.values()))), 2)
