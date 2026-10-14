# Independent 13-fold BTC stress screen — 2026-10-14

## Scope and provenance

- Third-party BTC daily OHLC archive: https://github.com/jptrustlearning/btc/blob/main/btc_prices.csv
- Fetched content blob SHA: `e633106c023e80f48e404574952ed7b1f8bfe650`
- 3,343 daily bars between 2017-08-17 and 2026-10-11. Not independently validated as an execution-grade, single-venue Binance dataset.
- 13 sequential non-overlapping test windows of 180 days, starting 2020-02-03, ending 2026-06-30.
- Signals derived from earlier daily closes; next open executions; virtual fee .1%, slippage .05% per side.
- Compared SMA crossover 10/30, SMA200 trend filter, volatility-targeted SMA200 + 30-day momentum and passive BTC.

## Experimental screen

The JS research harness returned the following rounded **per-fold descriptive** summaries:

| Candidate | Mean window return | Positive windows | Mean window max drawdown | Worst window drawdown |
|---|---:|---:|---:|---:|
| SMA 10/30 | +23.12% | 7/13 | -23.47% | -44.20% |
| SMA200 long/cash | +21.91% | 8/13 | -19.94% | -46.98% |
| SMA200 + momentum + 60%-target volatility | +24.32% | 9/13 | -11.39% | -20.25% |

**Important: these are not annualized or compound returns.** Each window starts afresh with virtual capital. Data quality and execution assumptions are unconfirmed. These configurations were researched in prior iterations on overlapping data, so these 13 windows must NOT be presented as pristine holdout statistical evidence.

Passive buy-and-hold should use one buy and one final liquidation, **not tiny near-zero rebalances caused by floating-point precision**. The corrected passive baseline, with only entry/exit costs, has mean 180-day return **23.80%**, positive in 8/13 windows. This audit supersedes the earlier passive mean that incorrectly counted additional trades.

## Scientific conclusion

Volatility management had lower observed drawdown in these windows. It is the **preferred candidate for additional safety-first research**, not established best-return strategy and not deployable trading advice. A genuine deploy/no-deploy decision requires fully reproducible Python runs, independent price venues/assets, costs under multiple schedules, untouched later observations, and ongoing prospective paper trading. Freqtrade lookahead-analysis and an independent LEAN/Freqtrade comparator would be useful.

**Go/no-go: NO-GO for real orders.**
