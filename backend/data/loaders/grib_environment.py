"""Selective, dependency-free reader for the verified ECMWF GRIB1 dataset."""

from __future__ import annotations

import math
import struct
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable

from ..models import MarineObservation, Provenance


@dataclass(frozen=True, slots=True)
class _Message:
    offset: int
    length: int
    raw_variable: str
    original_unit: str
    observation_time: datetime
    valid_time: datetime
    accumulation_start: datetime | None
    ni: int
    nj: int
    latitudes: tuple[float, ...]
    longitudes: tuple[float, ...]
    decimal_scale: int
    bms_offset: int | None
    bds_offset: int


class GribEnvironmentLoader:
    """Index GRIB messages, then decode only requested variables and cells."""

    PARAMETER_MAP = {
        34: ("sst", "sea_surface_temperature", "K", "degC"),
        165: ("10u", "wind_u", "m/s", "m/s"),
        166: ("10v", "wind_v", "m/s", "m/s"),
        167: ("2t", "air_temperature_2m", "K", "degC"),
        168: ("2d", "dewpoint_temperature_2m", "K", "degC"),
        228: ("tp", "total_precipitation", "m", "m"),
    }

    def __init__(self, path: str | Path):
        self.path = Path(path).resolve()
        self._messages = self._build_index()

    @property
    def available_times(self) -> tuple[datetime, ...]:
        return tuple(sorted({message.valid_time for message in self._messages}))

    @staticmethod
    def _u3(data: bytes, offset: int) -> int:
        return int.from_bytes(data[offset : offset + 3], "big")

    @staticmethod
    def _signed_magnitude(data: bytes) -> int:
        unsigned = int.from_bytes(data, "big")
        sign = 1 << (len(data) * 8 - 1)
        return -(unsigned & (sign - 1)) if unsigned & sign else unsigned

    @staticmethod
    def _ibm_float(data: bytes) -> float:
        if data == b"\x00\x00\x00\x00":
            return 0.0
        value = int.from_bytes(data, "big")
        sign = -1.0 if value & 0x80000000 else 1.0
        exponent = ((value >> 24) & 0x7F) - 64
        fraction = value & 0x00FFFFFF
        return sign * (fraction / 16777216.0) * (16.0**exponent)

    def _build_index(self) -> tuple[_Message, ...]:
        messages: list[_Message] = []
        with self.path.open("rb") as handle:
            offset = 0
            file_size = self.path.stat().st_size
            while offset < file_size:
                handle.seek(offset)
                indicator = handle.read(8)
                if len(indicator) != 8 or indicator[:4] != b"GRIB" or indicator[7] != 1:
                    raise ValueError(f"Unsupported or corrupt GRIB message at byte {offset}")
                message_length = self._u3(indicator, 4)
                pds_offset = offset + 8
                handle.seek(pds_offset)
                pds_head = handle.read(28)
                pds_length = self._u3(pds_head, 0)
                handle.seek(pds_offset)
                pds = handle.read(pds_length)
                if pds[3] != 128 or pds[4] != 98:
                    raise ValueError("Expected ECMWF centre 98, parameter table 128")
                parameter = pds[8]
                if parameter not in self.PARAMETER_MAP:
                    raise ValueError(f"Unmapped GRIB parameter {parameter}")
                raw_variable, _, original_unit, _ = self.PARAMETER_MAP[parameter]
                year = (pds[24] - 1) * 100 + pds[12]
                reference = datetime(
                    year, pds[13], pds[14], pds[15], pds[16], tzinfo=timezone.utc
                )
                time_unit = pds[17]
                if time_unit != 1:
                    raise ValueError(f"Unsupported GRIB time unit {time_unit}")
                p1, p2, time_range = pds[18], pds[19], pds[20]
                if time_range == 0:
                    valid_time = reference + timedelta(hours=p1)
                    accumulation_start = None
                elif time_range == 4 and parameter == 228:
                    accumulation_start = reference + timedelta(hours=p1)
                    valid_time = reference + timedelta(hours=p2)
                else:
                    raise ValueError(f"Unsupported time range indicator {time_range}")
                decimal_scale = self._signed_magnitude(pds[26:28])
                cursor = pds_offset + pds_length
                if not pds[7] & 0x80:
                    raise ValueError("GRIB message has no grid definition")
                handle.seek(cursor)
                gds = handle.read(32)
                gds_length = self._u3(gds, 0)
                if gds[5] != 0:
                    raise ValueError(f"Unsupported grid type {gds[5]}")
                ni = int.from_bytes(gds[6:8], "big")
                nj = int.from_bytes(gds[8:10], "big")
                lat1 = self._signed_magnitude(gds[10:13]) / 1000.0
                lon1 = self._signed_magnitude(gds[13:16]) / 1000.0
                lat2 = self._signed_magnitude(gds[17:20]) / 1000.0
                lon2 = self._signed_magnitude(gds[20:23]) / 1000.0
                latitudes = tuple(lat1 + i * (lat2 - lat1) / (nj - 1) for i in range(nj))
                longitudes = tuple(lon1 + i * (lon2 - lon1) / (ni - 1) for i in range(ni))
                cursor += gds_length
                bms_offset = cursor if pds[7] & 0x40 else None
                if bms_offset is not None:
                    handle.seek(cursor)
                    bms_length = self._u3(handle.read(3), 0)
                    cursor += bms_length
                messages.append(
                    _Message(
                        offset,
                        message_length,
                        raw_variable,
                        original_unit,
                        reference,
                        valid_time,
                        accumulation_start,
                        ni,
                        nj,
                        latitudes,
                        longitudes,
                        decimal_scale,
                        bms_offset,
                        cursor,
                    )
                )
                offset += message_length
        return tuple(messages)

    @staticmethod
    def _unpack_bits(data: bytes, bits_per_value: int, count: int) -> list[int]:
        if bits_per_value == 0:
            return [0] * count
        values: list[int] = []
        accumulator = 0
        available = 0
        iterator = iter(data)
        mask = (1 << bits_per_value) - 1
        for _ in range(count):
            while available < bits_per_value:
                accumulator = (accumulator << 8) | next(iterator)
                available += 8
            available -= bits_per_value
            values.append((accumulator >> available) & mask)
            accumulator &= (1 << available) - 1 if available else 0
        return values

    def _decode(self, message: _Message) -> list[float | None]:
        total = message.ni * message.nj
        bitmap: list[bool] | None = None
        with self.path.open("rb") as handle:
            if message.bms_offset is not None:
                handle.seek(message.bms_offset)
                length = self._u3(handle.read(3), 0)
                rest = handle.read(length - 3)
                if int.from_bytes(rest[1:3], "big") != 0:
                    raise ValueError("Predefined GRIB bitmaps are unsupported")
                bitmap_bytes = rest[3:]
                bitmap = [
                    bool(bitmap_bytes[index // 8] & (0x80 >> (index % 8)))
                    for index in range(total)
                ]
            handle.seek(message.bds_offset)
            header = handle.read(11)
            length = self._u3(header, 0)
            flags = header[3]
            if flags & 0xC0:
                raise ValueError("Only grid-point simple packing is supported")
            binary_scale = self._signed_magnitude(header[4:6])
            reference = self._ibm_float(header[6:10])
            bits_per_value = header[10]
            packed = handle.read(length - 11)
        present_count = sum(bitmap) if bitmap is not None else total
        integers = iter(self._unpack_bits(packed, bits_per_value, present_count))
        scale = 10.0 ** (-message.decimal_scale)
        values: list[float | None] = []
        for index in range(total):
            if bitmap is not None and not bitmap[index]:
                values.append(None)
            else:
                values.append((reference + next(integers) * (2.0**binary_scale)) * scale)
        return values

    def load(
        self,
        *,
        start_time: datetime,
        end_time: datetime | None = None,
        variables: Iterable[str],
        latitude_range: tuple[float, float],
        longitude_range: tuple[float, float],
        include_wind_speed: bool = True,
    ) -> list[MarineObservation]:
        end_time = end_time or start_time
        requested = set(variables)
        valid_canonical = {item[1] for item in self.PARAMETER_MAP.values()}
        unknown = requested - valid_canonical - {"wind_speed"}
        if unknown:
            raise ValueError(f"Unknown canonical variables: {sorted(unknown)}")
        if "wind_speed" in requested:
            requested.update({"wind_u", "wind_v"})
        selected = [
            message
            for message in self._messages
            if start_time <= message.valid_time <= end_time
            and self.PARAMETER_MAP[next(k for k, v in self.PARAMETER_MAP.items() if v[0] == message.raw_variable)][1]
            in requested
        ]
        observations: list[MarineObservation] = []
        vector_components: dict[tuple[datetime, float, float], dict[str, float]] = {}
        for message in selected:
            mapping = next(value for value in self.PARAMETER_MAP.values() if value[0] == message.raw_variable)
            _, canonical, original_unit, output_unit = mapping
            values = self._decode(message)
            for row, latitude in enumerate(message.latitudes):
                if not min(latitude_range) <= latitude <= max(latitude_range):
                    continue
                for column, longitude in enumerate(message.longitudes):
                    if not min(longitude_range) <= longitude <= max(longitude_range):
                        continue
                    value = values[row * message.ni + column]
                    if value is None:
                        continue
                    if original_unit == "K":
                        value -= 273.15
                    details = None
                    if canonical == "total_precipitation":
                        details = {
                            "accumulated": True,
                            "accumulation_start": message.accumulation_start.isoformat(),
                            "accumulation_end": message.valid_time.isoformat(),
                        }
                    provenance = Provenance(
                        "ECMWF",
                        str(self.path),
                        message.raw_variable,
                        original_unit,
                        details,
                    )
                    observations.append(
                        MarineObservation(
                            canonical,
                            value,
                            output_unit,
                            latitude,
                            longitude,
                            message.observation_time,
                            message.valid_time,
                            "ECMWF GRIB1",
                            "ECMWF parameter table 128",
                            "valid",
                            provenance,
                        )
                    )
                    if canonical in {"wind_u", "wind_v"}:
                        vector_components.setdefault(
                            (message.valid_time, latitude, longitude), {}
                        )[canonical] = value
        if include_wind_speed and ({"wind_speed", "wind_u", "wind_v"} & set(variables)):
            for (valid_time, latitude, longitude), components in vector_components.items():
                if {"wind_u", "wind_v"} <= components.keys():
                    observations.append(
                        MarineObservation(
                            "wind_speed",
                            math.hypot(components["wind_u"], components["wind_v"]),
                            "m/s",
                            latitude,
                            longitude,
                            valid_time,
                            valid_time,
                            "derived from ECMWF GRIB1",
                            "ECMWF parameter table 128",
                            "derived",
                            Provenance(
                                "ECMWF",
                                str(self.path),
                                "10u,10v",
                                "m/s",
                                {"formula": "sqrt(wind_u**2 + wind_v**2)"},
                            ),
                        )
                    )
        return sorted(
            observations,
            key=lambda item: (item.valid_time, item.latitude, item.longitude, item.variable),
        )
