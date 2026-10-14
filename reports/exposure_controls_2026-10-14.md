# Exposure-matched BTC research audit — 2026-10-14

## Question

Is apparent improved drawdown in the selected volatility-managed trend strategy merely the trivial effect of holding a lower BTC exposure?

## Data and method
- Third-party public BTC daily CSV: https://github.com/jptrustlearning/btc/blob/main/btc_prices.csv
- Retrieved blob SHA: `e633106c023e80f48e404574952ed7b1f8bfe650`
- 13 disjoint 180-calendar-day forward windows (2020-02-03 through 2026-06-30).
- Each window starts with virtual 1000 cash; BTC spot fractional weight, +/-2 percentage point rebalance threshold.
- Executions at next observed daily open, simple fee 0.1% and slippage 0.05% per execution.
- The constant-weight benchmarks are intentionally *signal-free*: their target weight is fixed.

| Constant BTC target | Mean 180d return | Mean 180d maximum drawdown | Positive windows |
|---|---:|---:|---:|
| 25% | +5.68% | -9.97% | 9/13 |
| 50% | +11.80% | -18.93% | 8/13 |
| 75% | +17.60% | -27.36% | 8/13 |
| 100% | +23.80% | -34.91% | 8/13 |

Earlier experimental volatility-managed trend (not computed in this exact same code path) reported mean +24.32%, mean -11.39% drawdown, 9/13 positive windows. This suggests momentum/timing could be adding value beyond scaling down exposure. It does NOT prove it because the compared workflows differ and strategy development already used overlapping historical data. A proper paired evaluation must run all algorithms through the same engine and identical fee/slippage and compare exposure distribution and turn-over.

## Caveats and required next checks

1. The 100% weight rebalancing engine may create epsilon-size trades due to floating-point variation. It uses a 2% threshold, mitigating unwanted dust trading; passive buy-hold reference is also implemented separately.
2. The target-weight model may invest almost all capital, but cash funding caps to available balance. Actual market impact, venue liquidity and execution fills not included.
3. Multiple datasets and repeated strategy iteration create multiple-comparison bias.
4. The bar data is not independently verified to be from one tradeable venue.
5. Real-time operational performance and CI must be separately evidenced.

## Decision

Favor volatility-managed trend as a **candidate for further research** on capital preservation. Reject the statement that any strategy here has been established as persistently profitable. Do not deploy real capital.
