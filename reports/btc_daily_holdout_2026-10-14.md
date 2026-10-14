# BTC daily historical out-of-sample evaluation — 2026-10-14

## Dataset provenance
- https://github.com/jptrustlearning/btc/blob/main/btc_prices.csv
- Fetched blob SHA: `e633106c023e80f48e404574952ed7b1f8bfe650`
- 3,343 BTC daily bars spanning 2017-08-17 through 2026-10-11.
- Simple checks: 0 missing day gaps, 0 OHLC envelope violations.
- WARNING: This third-party dataset may fall back to yfinance and cannot be assumed to be a continuous single-exchange tradeable BTCUSDT series. Its volume numbers are not used.

## Method
- First 2,172 bars (65%) for model selection; final 1,171 bars held out.
- Four SMA crossover candidates, fast/slow: 5/20, 10/30, 20/60, 30/90.
- Spot long/cash, next-bar open fill, fee 0.1% per transaction, assumed 0.05% slippage, starting virtual capital 1,000 USD.
- Choose training candidate with maximum (train_return_pct + 0.5 * train_drawdown_pct), no holdout refit.

## Training performance (not predictive evidence)
| SMA | Return | Max drawdown | Trades |
|---|---:|---:|---:|
| 5/20 | +682.67% | -67.93% | 126 |
| 10/30 | +1112.59% | -64.46% | 82 |
| 20/60 | +1008.34% | -72.12% | 39 |
| 30/90 | +479.31% | -68.14% | 23 |

Chosen: **10/30**.

## Untouched holdout performance
| Metric | Value |
|---|---:|
| SMA 10/30 return | +91.99% |
| Buy-and-hold same period return | +184.55% |
| SMA max drawdown | -38.57% |
| Executions | 43 |

## Decision
**REJECT** the tested SMA 10/30 as a superior return strategy: it materially underperformed buy-and-hold on the holdout. A large positive historical return alone is not a sufficient criterion. Data provenance and slippage assumptions remain limitations, and this is not live paper trading.

## Reproduce on a pinned source CSV
The source CSV has a Thai header and daily date strings; our generic downloader/CSV loader uses a different schema. Implement a validated import adapter before treating these numbers as an automated regression artifact.
