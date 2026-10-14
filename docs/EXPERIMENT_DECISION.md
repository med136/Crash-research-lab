# Research decision: prediction hypothesis (2026-10-14)

## Evidence levels
1. Verified: local parser, reproducible offline tests and synthetic generator (subject to CI verification).
2. Not verified: whether the third-party WebSocket address and SignalR schema are currently supported by the specific 1xBet page.
3. Not observed: independently logged real event sequences or official algorithm specifications.
4. Unsupported: claims of reliable knowledge of the next final multiplier.

## Falsifiable experiment
- Collect only user-authorized *redacted* local exports as JSONL (schema documented in import_frames.py).
- Keep receipt timestamps and round identifiers, audit duplicates and gaps.
- Do not use outcome data which became available after the prediction timestamp.
- Compare pre-registered chronological holdouts and prospective sequential forecasts against the fixed event-rate baseline.
- Report proper scoring rules (Brier score), uncertainty, effect sizes, and all negative results.
- One good holdout or predictive-looking history plot cannot establish a profitable or replicable signal.

## Decision
Do not claim a live prediction or train more complex AI systems until an independent,
complete, lawful dataset and chronological timing audit exist. The research
may conclude that no exploitable signal exists.

## Security
No credentials, cookies, session tokens, signed URLs or personal information
should be committed. The importer is deliberately offline; no login, network
client, or automatic betting is implemented.
