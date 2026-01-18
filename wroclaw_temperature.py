#!/usr/bin/env python3
"""Fetch and print the current temperature in Wroclaw."""
from __future__ import annotations

import json
from urllib.error import URLError
from urllib.request import urlopen

LATITUDE = 51.1079
LONGITUDE = 17.0385
API_URL = (
    "https://api.open-meteo.com/v1/forecast"
    f"?latitude={LATITUDE}&longitude={LONGITUDE}&current_weather=true"
)


def fetch_current_temperature() -> float:
    """Return the current temperature in Wroclaw (°C)."""
    try:
        with urlopen(API_URL, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except URLError as exc:
        raise RuntimeError(f"Failed to fetch weather data: {exc}") from exc

    current = payload.get("current_weather")
    if not current or "temperature" not in current:
        raise RuntimeError("Weather API response missing temperature data.")

    return float(current["temperature"])


if __name__ == "__main__":
    temperature = fetch_current_temperature()
    print(f"Aktualna temperatura we Wroclawiu: {temperature:.1f}°C")
