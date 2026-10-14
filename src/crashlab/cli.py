import argparse
import csv
import json
from pathlib import Path
from .core import analyze, read_csv, simulate

def main():
    parser = argparse.ArgumentParser(description="Crash research lab (no wagering)")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("simulate", help="Generate illustrative independent toy data")
    p.add_argument("--rows", type=int, default=2000)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--output", required=True)
    p = sub.add_parser("analyze", help="Analyze chronological CSV")
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--threshold", type=float, default=2.0)
    args = parser.parse_args()
    if args.command == "simulate":
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["round_id", "multiplier"])
            writer.writerows((f"synthetic-{i+1}", f"{v:.8f}") for i,v in enumerate(simulate(args.rows,args.seed)))
        print(f"Wrote {args.rows} illustrative rounds to {path}")
    else:
        result = analyze(read_csv(args.input), threshold=args.threshold)
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
