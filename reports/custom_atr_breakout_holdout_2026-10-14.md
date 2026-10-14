# Experimental custom strategy: ATR breakout with trend filter (2026-10-14)

## Source
Third-party BTC daily CSV: https://github.com/jptrustlearning/btc/blob/main/btc_prices.csv
Blob SHA `e633106c023e80f48e404574952ed7b1f8bfe650`. 3343 calendar-day bars from 2017-08-17 to 2026-10-11.

## Method
- 70% training: 2340 days; 30% forward chronological holdout: 1003 days, beginning 2024-01-13.
- Four pre-specified ATR/trend/breakout combinations from `src/cryptolab/strategies.py`.
- Signals only from prior fully completed bars; hypothetical fill at next open.
- Spot long/cash, fractional position size; fees 0.1%, slippage 0.05% per side.
- Training candidate chosen on `return_pct + max_drawdown_pct` (drawdown is negative).
- Approximate backtest performed by an independent JS reproduction of the Python algorithm on the fetched CSV; Python GitHub CI has NOT been confirmed yet.

| Config | Training return | Training max drawdown | Transactions |
|---|---:|---:|---:|
| Breakout20 + Trend100, 50% | +344.40% | -33.76% | 55 |
| Breakout50 + Trend200, 50% | +154.76% | -29.55% | 35 |
| Breakout20 + Trend200, 75% | +857.38% | -33.36% | 29 |
| Breakout40 + Trend100, 75% | +863.84% | -46.02% | 39 |

Chosen from train: **Breakout20 + Trend200, 75% fraction**.

## Independent holdout
- Strategy return: **+46.21%**
- Strategy maximum drawdown: **-23.78%**
- Strategy transactions: **23**
- Same-period buy-and-hold return: **+94.93%**

## Verdict: REJECT as best-return strategy
The model made a hypothetical profit, but materially underperformed a simple passive benchmark. Lower exposure can be desirable for some risk preferences, but is not equivalent to superior risk-adjusted returns; more extensive tests and multiple independent assets/regimes are needed.

## Important issues still to resolve
- Historical source provenance: CSV may aggregate or fall back to another provider; not independently audited as a single exchange feed.
- Intra-candle stop execution is NOT simulated; stops are based on prior close and executed next open.
- No funding, borrowing, leverage, or real order execution.
- No statistical significance or prospective paper trading demonstrated.
- No evidence that an ML/AI predictor can reliably forecast market direction.

**Decision: research candidate only, not live deployment or a promise of profit.**
