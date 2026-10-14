# Prior open-source projects: technical decision (2026-10-14)

## Reviewed
- https://github.com/Zakaria-laktati/crash-1xbet-monitoring: Dockerized scraper, PostgreSQL, Streamlit, token-monitor; code documents real-time OnCrash **final** event collection. Live connectivity not verified.
- https://github.com/mdomorffaruk/CrashGameDataAnalysis: HAR file processing and statistics; useful for lawful exported network archives.
- https://github.com/aa-sikkkk/FortuneTeller: archived July 2025; code uses StandardScaler.fit_transform before train_test_split; random holdout for potentially ordered data; predicts by applying regressors to existing feature rows, not independently observed future inputs. Do not adopt as evidence of future multiplier prediction.
- https://github.com/itsleeevi/provably-fair-crash-game: illustrative HMAC/hash fairness mechanism, NOT the verified proprietary game implementation.

## Decision
1. Keep data acquisition and analysis separate. Adopt the *architecture ideas*, not third-party secret handling.
2. Prioritize redacted offline HAR/SignalR import for lawfully obtained data; preserve local receipt timestamps, event types, and provenance.
3. Verify ordering, duplicates, completeness, and the precise difference between OnCrash post-outcome announcements and prior-round inputs.
4. For modeling, forbid train/test random shuffles and preprocessing fitted to holdout, and demand future genuinely unobserved rounds.
5. Do not offer precise upcoming multipliers or wagering automation absent extraordinary independently replicated prospective evidence.

## Evidence limits
No direct live WebSocket connection or official game algorithm verification was achieved during this review. No verified advance-final-multiplier data source was identified.
