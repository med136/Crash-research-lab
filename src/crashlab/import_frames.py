"""Import locally collected SignalR text frames into an auditable CSV.

Input is newline-delimited JSON with {"received_at": ISO8601, "frame": string}.
No network connectivity, credentials, or requests to gambling services.
"""
from __future__ import annotations
import argparse
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
from .signalr import parse_frame

def normalize_timestamp(value: str) -> str:
    if not isinstance(value, str):
        raise ValueError("received_at must be a timestamp string")
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("Invalid received_at timestamp") from exc
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise ValueError("received_at must include timezone")
    return dt.astimezone(timezone.utc).isoformat()

def import_jsonl(source: str | Path, destination: str | Path) -> dict:
    """Deduplicate identical results, reject conflicts, retain observed arrival time.

    The receipt time is supplied by the exporter; it is not cryptographically verified.
    OnCrash is a *post-event* observation, never a future multiplier signal.
    """
    rows: dict[str, tuple[str, float]] = {}
    total_lines = 0
    with Path(source).open(encoding="utf-8") as stream:
        for line in stream:
            if not line.strip():
                continue
            total_lines += 1
            record = json.loads(line)
            if not isinstance(record, dict) or set(record) != {"received_at", "frame"}:
                raise ValueError(f"Invalid JSONL schema at line {total_lines}")
            received_at = normalize_timestamp(record["received_at"])
            for event in parse_frame(record["frame"]):
                previous = rows.get(event.round_id)
                if previous is not None:
                    if previous[1] != event.multiplier:
                        raise ValueError(f"Conflicting result for round {event.round_id}")
                    if received_at < previous[0]:
                        rows[event.round_id] = (received_at, event.multiplier)
                else:
                    rows[event.round_id] = (received_at, event.multiplier)
    if not rows:
        raise ValueError("No OnCrash results found")
    # Sort by observed receipt time; this may not equal actual round order.
    ordered = sorted(rows.items(), key=lambda kv: (kv[1][0], kv[0]))
    target = Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["round_id", "multiplier", "received_at"])
        for round_id, (received_at, multiplier) in ordered:
            writer.writerow([round_id, multiplier, received_at])
    return {"frames": total_lines, "unique_rounds": len(rows), "duplicates": 0, "output": str(target),
            "warning": "Receipt time and historical results do not predict future rounds."}

def main() -> None:
    parser = argparse.ArgumentParser(description="Offline SignalR export importer")
    parser.add_argument("--input", required=True, help="Local JSONL frames")
    parser.add_argument("--output", required=True, help="Result CSV")
    args = parser.parse_args()
    print(json.dumps(import_jsonl(args.input, args.output), indent=2))

if __name__ == "__main__":
    main()
