# External historical Crash data — initial audit (2026-10-14)

## Source and reproducibility

Source repository: https://github.com/AhmedSakrr/1XBetCrash-Prediction
Source file: `1XBetCrash.csv`
Observed blob SHA: `05ecd55b54f7a8b52f9e2dbd8de9154d332dc9f8`
Header: `Time,Number of players,Total bets,Multiplier`.

A GitHub connector read of the public file contained **43 rows**. The dataset is third-party and its provenance, game identity, original capture order and timestamps are **not independently verified**. Time values have hours and minutes but no date; rows go from `12:31` to `4:20`, so chronological continuity cannot be established.

Other sources examined:
- https://github.com/davidadriel64/Save_data_crash_1xbet — `data.csv` had only the header `cf,mfs,ts` as fetched.
- https://github.com/mdomorffaruk/CrashGameDataAnalysis — analysis scripts, no validated ready-to-test series identified.

## Exploratory findings (unverified chronology)

- 43 parseable rows, multipliers 1.00x to 29.02x.
- At least 2x: 22/43 = 51.16%.
- At least 5x: 13/43 = 30.23%.
- At least 10x: 5/43 = 11.63%.
- Binary lag-1 sample correlation for 2x event: ~0.286 (descriptive only).

Treat the source row order as *provisional*, not confirmed chronological order.

## Small-sample holdout illustration

For the outcome `multiplier >= 2`:
- First 30 rows designated training, last 13 test (unverified chronological order).
- Fixed training event rate = 19/30 = 0.633333.
- Constant-rate baseline Brier score: 0.339573.
- Naive model forecasting the previous row's binary result: Brier 0.307692.

**Interpretation**: A difference on 13 test rows, with unverified timestamps and game provenance, is not evidence of genuine out-of-sample predictive ability. Do not trade or bet on these findings.

## Next decision

Acquire a lawful, continuous, timestamped and independently verifiable export of rounds from the *same specified Crash game*. At least thousands of prospective rounds are preferable for a meaningful audit. Check exact event arrival chronology, leakage and collection gaps; then run strictly forward prequential experiments and uncertainty estimation. No live-next-multiplier claim is supported.
