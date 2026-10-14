"""Offline event-timing integrity audit.

Not a vulnerability scanner or live betting predictor. Evaluates only redacted,
user-authorized event metadata and flags cases worth manual review.
"""
from __future__ import annotations
from collections import defaultdict
from datetime import datetime
import json
from pathlib import Path

def audit_events(path: str | Path) -> dict:
    rounds = defaultdict(list)
    count = 0
    with open(path, encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            event = json.loads(line)
            if not isinstance(event, dict) or set(event) != {"round_id", "event", "received_at"}:
                raise ValueError(f"Invalid event schema at line {line_number}")
            if not isinstance(event["round_id"], (str,int)) or isinstance(event["round_id"],bool):
                raise ValueError("Invalid round identifier")
            if not str(event["round_id"]).strip() or event["event"] not in {"OnStart","OnProfits","OnCashouts","OnCrash"}:
                raise ValueError("Invalid round identifier or event name")
            dt = datetime.fromisoformat(event["received_at"].replace("Z","+00:00"))
            if dt.tzinfo is None or dt.utcoffset() is None:
                raise ValueError("Timezone required")
            rounds[str(event["round_id"])].append((dt,event["event"]))
            count += 1
    if not count:
        raise ValueError("Empty event stream")
    with_start = with_crash = reversed_order = duplicate_crashes = 0
    start_to_crash_seconds = []
    for items in rounds.values():
        starts = [t for t,e in items if e == "OnStart"]
        crashes = [t for t,e in items if e == "OnCrash"]
        with_start += bool(starts)
        with_crash += bool(crashes)
        duplicate_crashes += len(crashes) > 1
        if starts and crashes:
            interval = (min(crashes)-min(starts)).total_seconds()
            start_to_crash_seconds.append(interval)
            reversed_order += interval < 0
    return {
        "event_count":count,"round_count":len(rounds),
        "rounds_with_start":with_start,"rounds_with_crash":with_crash,
        "rounds_with_both":len(start_to_crash_seconds),
        "negative_start_crash_intervals":reversed_order,
        "duplicate_crash_events":duplicate_crashes,
        "median_start_to_crash_seconds":sorted(start_to_crash_seconds)[len(start_to_crash_seconds)//2] if start_to_crash_seconds else None,
        "warning":"Receipt times may reflect buffering/reordering. An anomaly alone is NOT advance knowledge of a multiplier."
    }

def main():
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument("--input",required=True)
    args=parser.parse_args()
    print(json.dumps(audit_events(args.input),indent=2))

if __name__=="__main__":
    main()
