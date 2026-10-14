# 15-market cryptocurrency research screen — 14 October 2026

## Verified run

- PR #5: https://github.com/med136/Crash-research-lab/pull/5
- Historical research GitHub Actions run: https://github.com/med136/Crash-research-lab/actions/runs/38514698693
- Other Python tests run: https://github.com/med136/Crash-research-lab/actions/runs/38514698706
- Both jobs completed successfully, including the 15-crypto import, strategy comparison and dashboard generation.
- GitHub Actions uploaded `universe_15.json` and `universe_panel.html` in `btc-research-no-orders` artifact (retained for 14 days).

## Design

- Fifteen currently listed Binance Spot USDT assets, frozen UTC cutoff **2026-09-30**, **1000 complete 1d OHLCV bars per asset**, all 15 fetched, zero failed.
- All assets use identical **first 450 bars for warm-up** then **six non-overlapping 90-day hypothetical backtest windows**. No compounding between windows.
- Volatility-managed trend (200-day SMA, 30-day momentum, 30-day inverse volatility with cap 100%) compared to one-entry/one-exit Buy and Hold. Next-bar open model with 0.10% fee and 0.05% slippage in base scenario.
- Same strategy compared under doubled fee/slippage and adverse slippage. Public API raw response SHA-256 manifests in the full JSON artifact.
- The `advisor` is a transparent causal rule-based vote diagnostic, **not** a machine-learned model, a calibrated probability, or a demonstrated profitable signal.

## Descriptive results (mean return per 90-day window; percentage points for difference)

| Market | Trend mean | Passive mean | Excess pp | Median excess pp | Drawdown improvement pp |
|---|---:|---:|---:|---:|---:|
| BTCUSDT | +4.99% | +1.33% | +3.66 | +5.60 | +14.50 |
| ETHUSDT | +11.97% | +12.14% | -0.17 | +11.35 | +21.87 |
| BNBUSDT | +11.89% | +6.65% | +5.24 | +1.46 | +12.07 |
| SOLUSDT | +1.48% | +3.21% | -1.73 | +1.56 | +23.10 |
| XRPUSDT | +1.02% | -4.13% | +5.15 | +8.67 | +20.43 |
| ADAUSDT | -4.64% | -9.56% | +4.92 | +17.32 | +29.59 |
| DOGEUSDT | -6.88% | -7.35% | +0.47 | +9.44 | +24.56 |
| LINKUSDT | +9.27% | +4.86% | +4.41 | +9.59 | +26.48 |
| AVAXUSDT | +0.18% | +3.09% | -2.91 | +15.69 | +28.01 |
| DOTUSDT | -3.49% | -15.16% | +11.67 | +18.47 | +33.55 |
| LTCUSDT | -3.89% | -3.76% | -0.13 | +0.70 | +16.39 |
| TRXUSDT | +4.00% | +7.15% | -3.14 | -4.42 | +5.38 |
| BCHUSDT | -0.12% | +5.01% | -5.13 | -3.65 | +17.17 |
| ATOMUSDT | -7.66% | -11.42% | +3.76 | +1.82 | +24.74 |
| NEARUSDT | +3.29% | +18.84% | -15.55 | -12.11 | +23.50 |

- 15/15 valid data series; **8/15** show positive mean excess return, **12/15** positive median excess return; **9/15** positive outright mean trend strategy return; **15/15** experienced reduced average maximum drawdown versus fully invested passive.
- Under double-cost and adverse-slippage cases, **8/15** pairs retain a positive mean excess return. This does not establish an edge; outcomes are highly regime-dependent.
- **90 fold results are NOT 90 independent tests.** Crypto markets are strongly correlated and current-listed markets have survivorship bias. Prior BTC strategy research used portions of overlapping dates. Six windows per coin give low statistical power. There is no untested future performance sample.
- Choosing an apparent winner after reading this cross-asset ranking would incur multiple-testing bias. **Do not use these ranks to select real-money trades.**

## Decision

**Research evidence: cross-asset performance and drawdown characteristics are mixed.** Trend timing reduced historical drawdowns on the sampled assets, but no universal outperformance or robust profitable machine-learning signal has been demonstrated.

**Real-money deployment: NO-GO.** No exchange account connection, live orders, or leverage are enabled. Next priorities: genuinely unseen future samples, careful risk-matched allocation comparisons across all coins, and optional scheduled *virtual* portfolio monitoring once execution assumptions and data recovery are proven.
