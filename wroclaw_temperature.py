#!/usr/bin/env python3
"""Fetch and print the current temperature in Wroclaw."""
from __future__ import annotations

import json
from datetime import datetime, timedelta
from typing import Iterable
from urllib.error import URLError
from urllib.request import urlopen

import matplotlib.pyplot as plt

LATITUDE = 51.1079
LONGITUDE = 17.0385
API_URL = (
    "https://api.open-meteo.com/v1/forecast"
    f"?latitude={LATITUDE}&longitude={LONGITUDE}"
    "&hourly=temperature_2m"
    "&current_weather=true"
    "&timezone=Europe%2FWarsaw"
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


def fetch_hourly_temperatures() -> tuple[list[datetime], list[float]]:
    """Return hourly timestamps and temperatures for Wroclaw."""
    try:
        with urlopen(API_URL, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except URLError as exc:
        raise RuntimeError(f"Failed to fetch weather data: {exc}") from exc

    hourly = payload.get("hourly") or {}
    times = hourly.get("time")
    temps = hourly.get("temperature_2m")
    if not times or not temps or len(times) != len(temps):
        raise RuntimeError("Weather API response missing hourly temperature data.")

    timestamps = [datetime.fromisoformat(value) for value in times]
    temperatures = [float(value) for value in temps]
    return timestamps, temperatures


def slice_temperature_window(
    timestamps: Iterable[datetime],
    temperatures: Iterable[float],
    reference: datetime,
    past_hours: int = 8,
    future_hours: int = 8,
) -> tuple[list[datetime], list[float]]:
    """Slice temperatures from past_hours back to future_hours ahead."""
    window_start = reference - timedelta(hours=past_hours)
    window_end = reference + timedelta(hours=future_hours)
    sliced_times: list[datetime] = []
    sliced_temps: list[float] = []
    for timestamp, temperature in zip(timestamps, temperatures):
        if window_start <= timestamp <= window_end:
            sliced_times.append(timestamp)
            sliced_temps.append(temperature)
    return sliced_times, sliced_temps


def plot_temperature_window(timestamps: list[datetime], temperatures: list[float]) -> None:
    """Plot temperatures for the selected time window."""
    if not timestamps:
        raise RuntimeError("No data available for the selected time window.")

    plt.figure(figsize=(10, 5))
    plt.plot(timestamps, temperatures, marker="o", linewidth=2)
    plt.title("Temperatura we Wroclawiu (8h wstecz i 8h naprzod)")
    plt.xlabel("Czas")
    plt.ylabel("Temperatura (°C)")
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    temperature = fetch_current_temperature()
    print(f"Aktualna temperatura we Wroclawiu: {temperature:.1f}°C")
    all_times, all_temps = fetch_hourly_temperatures()
    now = datetime.now().replace(minute=0, second=0, microsecond=0)
    window_times, window_temps = slice_temperature_window(
        all_times,
        all_temps,
        now,
    )
    plot_temperature_window(window_times, window_temps)
