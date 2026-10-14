"""Offline parser for user-supplied SignalR text frames.

It does not connect to gambling services or obtain authentication credentials.
A final OnCrash event is NOT an advance forecast.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
import math

SEPARATOR = "\x1e"

@dataclass(frozen=True)
class CrashObservation:
    round_id: str
    multiplier: float
    source_event: str = "OnCrash"

def parse_frame(frame: str) -> list[CrashObservation]:
    """Return validated final-round events from SignalR JSON messages.

    All other event types and control frames are ignored, not guessed.
    """
    if not isinstance(frame, str) or len(frame) > 2_000_000:
        raise ValueError("Invalid frame")
    observations: list[CrashObservation] = []
    for part in frame.split(SEPARATOR):
        if not part.strip():
            continue
        try:
            message = json.loads(part)
        except json.JSONDecodeError:
            continue
        if not isinstance(message, dict) or message.get("type") != 1:
            continue
        if message.get("target") != "OnCrash":
            continue
        args = message.get("arguments")
        if not isinstance(args, list):
            continue
        for arg in args:
            records = arg if isinstance(arg, list) else [arg]
            for record in records:
                if not isinstance(record, dict):
                    continue
                round_id, multiplier = record.get("l"), record.get("f")
                if round_id is None or isinstance(round_id, bool) or isinstance(multiplier, bool):
                    continue
                if not isinstance(round_id, (int, str)) or not str(round_id).strip():
                    continue
                try:
                    m = float(multiplier)
                except (ValueError, TypeError, OverflowError):
                    continue
                if not math.isfinite(m) or m < 1:
                    continue
                observations.append(CrashObservation(round_id=str(round_id), multiplier=m))
    return observations

def parse_unique_frames(frames: list[str]) -> list[CrashObservation]:
    """Deduplicate by round ID; conflicting final outcomes fail closed."""
    seen: dict[str, CrashObservation] = {}
    for frame in frames:
        for event in parse_frame(frame):
            existing = seen.get(event.round_id)
            if existing is not None and existing.multiplier != event.multiplier:
                raise ValueError(f"Conflicting results for round {event.round_id}")
            seen[event.round_id] = event
    return list(seen.values())
