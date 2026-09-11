"""Selective reader for the verified compact Copernicus wave NetCDF-4 file.

The MVP uses no external NetCDF dependency.  It validates the file's embedded
metadata and discovers its contiguous float32 payloads before decoding them.
"""

from __future__ import annotations

import math
import struct
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from ..models import MarineObservation, Provenance


class WaveLoader:
    VARIABLE_MAP = {
        "VHM0": ("significant_wave_height", "m", (0.0, 100.0)),
        "VMDR": ("mean_wave_direction", "degree", (0.0, 360.0)),
        "VTPK": ("peak_wave_period", "s", (0.0, 100.0)),
    }
    DATASET = "cmems_mod_glo_wav_anfc_0.083deg_PT3H-i_202411"

    def __init__(self, path: str | Path):
        self.path = Path(path).resolve()
        self._data = self.path.read_bytes()
        if not self._data.startswith(b"\x89HDF\r\n\x1a\n"):
            raise ValueError("Expected a NetCDF-4/HDF5 wave file")
        required = [b"VHM0", b"VMDR", b"VTPK", self.DATASET.encode()]
        if any(item not in self._data for item in required):
            raise ValueError("Wave file does not contain the required verified metadata")
        self.times = self._find_times()
        self.latitudes, latitude_end = self._find_coordinate(11.5, 14.5)
        self.longitudes, longitude_end = self._find_coordinate(73.0, 76.0)
        self._shape_size = len(self.times) * len(self.latitudes) * len(self.longitudes)
        search_start = max(latitude_end, longitude_end)
        self._payload_offsets: dict[str, int] = {}
        for raw_variable in ("VHM0", "VMDR", "VTPK"):
            bounds = self.VARIABLE_MAP[raw_variable][2]
            offset = self._find_contiguous_payload(search_start, *bounds)
            self._payload_offsets[raw_variable] = offset
            search_start = offset + self._shape_size * 4

    def _find_times(self) -> tuple[datetime, ...]:
        candidates: list[tuple[int, tuple[float, ...]]] = []
        for offset in range(0, min(len(self._data) - 16, 8192), 8):
            first, second = struct.unpack_from("<2d", self._data, offset)
            if 946684800 <= first <= 4102444800 and second - first == 10800:
                values = [first, second]
                cursor = offset + 16
                while cursor + 8 <= len(self._data):
                    value = struct.unpack_from("<d", self._data, cursor)[0]
                    if value - values[-1] != 10800:
                        break
                    values.append(value)
                    cursor += 8
                candidates.append((offset, tuple(values)))
        if not candidates:
            raise ValueError("Could not locate the 3-hourly time coordinate")
        _, values = max(candidates, key=lambda item: len(item[1]))
        return tuple(datetime.fromtimestamp(value, timezone.utc) for value in values)

    def _find_coordinate(self, expected_min: float, expected_max: float) -> tuple[tuple[float, ...], int]:
        expected_count = 37
        for offset in range(0, min(len(self._data) - expected_count * 4, 8192), 4):
            values = struct.unpack_from(f"<{expected_count}f", self._data, offset)
            if (
                math.isclose(values[0], expected_min, abs_tol=1e-5)
                and math.isclose(values[-1], expected_max, abs_tol=1e-5)
                and all(math.isclose(b - a, 1 / 12, abs_tol=1e-5) for a, b in zip(values, values[1:]))
            ):
                return tuple(float(value) for value in values), offset + expected_count * 4
        raise ValueError(f"Could not locate coordinate {expected_min}..{expected_max}")

    def _find_contiguous_payload(self, search_start: int, minimum: float, maximum: float) -> int:
        count = self._shape_size
        aligned = search_start + (-search_start % 4)
        floats = struct.unpack_from(f"<{(len(self._data) - aligned) // 4}f", self._data, aligned)
        invalid = [not (math.isnan(value) or minimum <= value <= maximum) for value in floats]
        finite = [not math.isnan(value) and minimum <= value <= maximum for value in floats]
        bad_count = sum(invalid[:count])
        finite_count = sum(finite[:count])
        candidates: list[int] = []
        for start in range(0, len(floats) - count + 1):
            if start:
                bad_count += invalid[start + count - 1] - invalid[start - 1]
                finite_count += finite[start + count - 1] - finite[start - 1]
            if bad_count == 0 and finite_count >= count // 10:
                candidates.append(start)
        if not candidates:
            raise ValueError("Could not locate contiguous wave payload")
        first_group = [candidates[0]]
        for candidate in candidates[1:]:
            if candidate != first_group[-1] + 1:
                break
            first_group.append(candidate)
        return aligned + first_group[-1] * 4

    @property
    def available_times(self) -> tuple[datetime, ...]:
        return self.times

    def load(
        self,
        *,
        start_time: datetime,
        end_time: datetime | None = None,
        variables: Iterable[str],
        latitude_range: tuple[float, float],
        longitude_range: tuple[float, float],
    ) -> list[MarineObservation]:
        end_time = end_time or start_time
        requested = set(variables)
        canonical_to_raw = {value[0]: key for key, value in self.VARIABLE_MAP.items()}
        unknown = requested - canonical_to_raw.keys()
        if unknown:
            raise ValueError(f"Unknown canonical wave variables: {sorted(unknown)}")
        observations: list[MarineObservation] = []
        plane = len(self.latitudes) * len(self.longitudes)
        for canonical in requested:
            raw = canonical_to_raw[canonical]
            _, unit, _ = self.VARIABLE_MAP[raw]
            payload_offset = self._payload_offsets[raw]
            values = struct.unpack_from(f"<{self._shape_size}f", self._data, payload_offset)
            for time_index, valid_time in enumerate(self.times):
                if not start_time <= valid_time <= end_time:
                    continue
                for row, latitude in enumerate(self.latitudes):
                    if not min(latitude_range) <= latitude <= max(latitude_range):
                        continue
                    for column, longitude in enumerate(self.longitudes):
                        if not min(longitude_range) <= longitude <= max(longitude_range):
                            continue
                        index = time_index * plane + row * len(self.longitudes) + column
                        value = values[index]
                        if math.isnan(value):
                            continue
                        observations.append(
                            MarineObservation(
                                canonical,
                                float(value),
                                unit,
                                latitude,
                                longitude,
                                valid_time,
                                valid_time,
                                "Copernicus Marine Service",
                                self.DATASET,
                                "valid",
                                Provenance(
                                    "Copernicus Marine Service / METEO-FRANCE",
                                    str(self.path),
                                    raw,
                                    unit,
                                ),
                            )
                        )
        return sorted(
            observations,
            key=lambda item: (item.valid_time, item.latitude, item.longitude, item.variable),
        )
