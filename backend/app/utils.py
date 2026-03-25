from __future__ import annotations

from datetime import datetime

import numpy as np


def parse_datetime(value: str | None) -> datetime | None:
    if value is None:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def hours_between(start: str, end: str | None) -> float | None:
    end_dt = parse_datetime(end)
    if end_dt is None:
        return None
    start_dt = parse_datetime(start)
    assert start_dt is not None
    return round((end_dt - start_dt).total_seconds() / 3600, 2)


def median_or_none(values: list[float]) -> float | None:
    if not values:
        return None
    return round(float(np.median(np.array(values, dtype=float))), 2)


def min_max_scores(values: dict[str, float]) -> dict[str, float]:
    assert values
    floor = min(values.values())
    ceiling = max(values.values())
    if floor == ceiling:
        return {key: 1.0 for key in values}
    return {
        key: round((value - floor) / (ceiling - floor), 4)
        for key, value in values.items()
    }


def round_score(value: float) -> float:
    return round(value * 100, 1)
