from __future__ import annotations

import math
from functools import lru_cache
from typing import Iterable

from backend.app.data.india_ev_data import INDIAN_CITIES


def haversine_km(a: dict, b: dict) -> float:
    r = 6371.0
    lat1, lon1 = math.radians(a["lat"]), math.radians(a["lng"])
    lat2, lon2 = math.radians(b["lat"]), math.radians(b["lng"])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * r * math.asin(math.sqrt(h))


def normalize_location(value: str) -> dict:
    if not value:
        return INDIAN_CITIES["Delhi, India"] | {"label": "Delhi, India"}
    clean = value.strip().lower()
    for label, item in INDIAN_CITIES.items():
        if clean == label.lower() or clean in label.lower():
            return item | {"label": label}
    # nearest keyword fallback for short user inputs such as "delhi" or "blr"
    aliases = {"blr": "Bengaluru, Karnataka", "bangalore": "Bengaluru, Karnataka", "bombay": "Mumbai, Maharashtra"}
    if clean in aliases:
        label = aliases[clean]
        return INDIAN_CITIES[label] | {"label": label}
    return INDIAN_CITIES["Delhi, India"] | {"label": "Delhi, India"}


def interpolate_route(start: dict, end: dict, points: int = 48) -> list[dict]:
    """Generate a stable route polyline with a slight highway-like curve.

    This fallback keeps the app fully functional without paid route API keys.
    When OpenRouteService/OSRM keys are configured, this function can be replaced
    by provider geometry while preserving the same response schema.
    """
    pts = []
    for i in range(points):
        t = i / (points - 1)
        bow = math.sin(t * math.pi) * 0.55
        lat = start["lat"] * (1 - t) + end["lat"] * t + bow * (end["lng"] - start["lng"]) / 25
        lng = start["lng"] * (1 - t) + end["lng"] * t - bow * (end["lat"] - start["lat"]) / 25
        pts.append({"lat": round(lat, 6), "lng": round(lng, 6)})
    return pts


def route_distance_km(route: Iterable[dict]) -> float:
    pts = list(route)
    return sum(haversine_km(pts[i], pts[i + 1]) for i in range(len(pts) - 1)) * 1.18


def distance_to_polyline_km(point: dict, route: list[dict]) -> tuple[float, float]:
    distances = []
    cumulative = 0.0
    best = (9999.0, 0.0)
    for i, rp in enumerate(route):
        d = haversine_km(point, rp)
        if i > 0:
            cumulative += haversine_km(route[i - 1], rp) * 1.18
        if d < best[0]:
            best = (d, cumulative)
        distances.append(d)
    return best


@lru_cache(maxsize=1)
def city_options() -> list[str]:
    return sorted(INDIAN_CITIES.keys())
