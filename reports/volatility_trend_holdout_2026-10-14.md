# Volatility-managed BTC research — 2026-10-14

## Evidence and dataset
Third-party BTC daily CSV at https://github.com/jptrustlearning/btc/blob/main/btc_prices.csv; fetched blob SHA `e633106c023e80f48e404574952ed7b1f8bfe650`. 3343 daily bars, 2017-08-17 to 2026-10-11. Data is not independently established as continuous Binance spot executions.

### Frozen methodology
- First 2340 bars (70%) calibration, last 1003 bars (from 2024-01-13) untouched test.
- 200-day trailing SMA uptrend + 30-day positive momentum.
- 30-day historical volatility, annualized sqrt(365). Spot allocation `min(1, target/realized_vol)` in a positive trend, cash otherwise.
- Targets evaluated on training only: 20%, 30%, 40%, 60%.
- Selection criterion training return + (negative) maximum drawdown; selected target **60%**.
- Next-bar open hypothetical fills, 0.1% fee and 0.05% slippage per rebalance, no leverage.

| Vol target | Calibration return | Calibration maximum drawdown | Transactions |
|---|---:|---:|---:|
| 20% | +189.75% | -16.13% | 662 |
| 30% | +348.58% | -23.52% | 690 |
| 40% | +494.38% | -30.26% | 641 |
| 60% | +752.99% | -40.19% | 396 |

### Unseen test (2024-01-13 to 2026-10-11)
- Chosen volatility-managed trend: **+97.83%** net hypothetical return; **-26.15%** maximum drawdown; 78 transactions.
- Same-period buy-and-hold: **+94.93%** hypothetical return at matching basic execution assumptions.
- Difference: ~**2.90 percentage points** over nearly 2.75 years, not evidence of significant predictive alpha.

## Verdict
**Promising research candidate, NOT approved for real-money deployment**. It narrowly exceeds BTC buy-and-hold in one test, but is sensitive to dataset quality, exchange fees and assumed slippage. Additional independent ETH/BTC exchange-verified datasets, walk-forward regimes, parameter stability, error checks, downside-tail stress and prospective paper-trading are required. This implementation is a rules-based volatility strategy, **not an AI model**. Earlier custom ATR breakout (same historical source) underperformed buy-and-hold.

## Scientific sources
- https://www.sciencedirect.com/science/article/pii/S1544612325011377 (risk-managed momentum, 2025)
- https://link.springer.com/article/10.1007/s11408-025-00474-9 (crash/tail-risk caution, 2025)
- https://github.com/binance/binance-public-data (official free historical data)
