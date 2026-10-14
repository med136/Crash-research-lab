"""Passive, opt-in local stream observer; does not connect to game servers.

Usage: tail -f local_authorized_frames.jsonl | python -m crashlab.live_observer
Input schema: {"received_at":"2026-10-14T02:00:00Z","frame":"<SignalR message>"}.
Never pipe authentication tokens/cookies into this process.
"""
from __future__ import annotations
import json
import sys
from .import_frames import normalize_timestamp
from .signalr import parse_frame

def observe_line(line: str) -> list[dict]:
    record = json.loads(line)
    if not isinstance(record, dict) or set(record) != {"received_at", "frame"}:
        raise ValueError("Expected received_at and frame only")
    received_at = normalize_timestamp(record["received_at"])
    return [{"received_at": received_at, "round_id": e.round_id,
             "multiplier": e.multiplier, "event": "final_result"}
            for e in parse_frame(record["frame"])]

def main() -> None:
    seen: dict[str, float] = {}
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            for event in observe_line(line):
                rid, multiplier = event["round_id"], event["multiplier"]
                if rid in seen:
                    if seen[rid] != multiplier:
                        print(json.dumps({"error":"conflicting_result","round_id":rid}), file=sys.stderr)
                    continue
                seen[rid] = multiplier
                print(json.dumps(event), flush=True)
        except (ValueError, TypeError, KeyError, json.JSONDecodeError):
            print(json.dumps({"error":"invalid_record"}), file=sys.stderr)

if __name__ == "__main__":
    main()
