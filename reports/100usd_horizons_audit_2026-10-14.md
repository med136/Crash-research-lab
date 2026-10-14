# Historical $100 spot-crypto strategy audit — 2026-10-14

## Status and reproducibility

**NO-GO for real money.** This report is purely historical. We do not have a proven profitable algorithm, a calibrated estimate of future balances, or a legally/operationally approved real-order deployment.

- Code reviewed on PR [#8](https://github.com/med136/Crash-research-lab/pull/8).
- Official public Binance Spot `1d` OHLCV endpoint; **15 of 15** listed USDT markets fetched successfully at a common **2026-09-30 UTC** cutoff.
- Each asset's raw response fingerprint is recorded in the accompanying GitHub Actions artifact `100usd_horizons.json`.
- **1000** completed daily candles per asset, first **201** available as historical indicator warmup.
- Non-overlapping, backward-aligned completed test windows per asset: 26 x 30d; 8 x 90d; 4 x 180d; **only 2 x 365d**.
- Seven models, including cash and buy-and-hold controls, were tested through the SAME causal execution engine; virtual **$100 for each asset/window independently**, with no compounding between windows.
- Base execution: fee 0.10% and slippage 0.05% per fill; doubles and adverse-slippage scenarios included; assumed $5 transaction minimum (exchange specific filters not verified); no leverage or futures.
- Includes terminal modeled liquidation, paper spot positions at the next candle open based on previous completed closes, max drawdown, and same-period buy-and-hold comparisons.
- PR #8 GitHub Actions **Python tests succeeded** and **Reproducible Historical Research (Paper Only)** succeeded including the historical $100 scenarios and FR/EN dashboard build.
- Interactive bilingual file: `100usd_horizons_panel.html` in the PR #8 research workflow artifact. Open in a browser, choose asset, strategy, period, and cost level.

## BTC / SMA20-60 historical distributions (NOT future projections)

| Approximate horizon | Nonoverlapping BTC windows | Historical median of final $100 wallet | Historical worst | Historical best |
|---|---:|---:|---:|---:|
| 1 month (30 days) | 26 | $100.00 | $89.26 | $126.48 |
| 3 months (90 days) | 8 | $104.74 | $89.26 | $151.54 |
| 6 months (180 days) | 4 | $121.92 | $86.19 | $138.86 |
| 1 year (365 days) | 2 | $130.84 | $115.78 | $145.90 |

**Do not interpret the annual $130.84 as a forecast, median future outcome, floor, or expected annual return.** Two historical annual samples cannot support a predictive annual distribution. A future $100 investment could lose most or all value.

## Why “the maximum historical winner” is the wrong CTO decision

Across all 15 tested assets, the mean of each asset's mean hypothetical **365-day** dollar balances was:

| Fixed candidate | Average of per-asset historical mean final balances | Mean historical max drawdown, averaged by asset | Number of assets beating passive mean (base fees) |
|---|---:|---:|---:|
| All cash | $100.00 | 0.00% | 4/15 |
| Spot buy and hold | $119.19 | -62.13% | control |
| SMA20/60 | $119.68 | -37.63% | 11/15 |
| 55/20 breakout | $117.58 | -33.75% | 7/15 |
| Volatility trend | $114.60 | -21.04% | 7/15 |
| Defensive ensemble | $109.29 | -10.27% | 5/15 |

These are **not forecasts, investable portfolios, or statistically independent asset returns**. The 15 markets are correlated and were selected from assets that survived to be currently listed. Repeating backtests over known dates introduces model-selection and multiple-testing bias.

On **SOL**, historical SMA20/60 annual median was **$88.50**, and the worst annual sample was **$81.21**. Across all 15 assets and two annual windows each, the SMA20/60 worst hypothetical balance was **$35.04**. On BTC, aggressive cash-vs-long results depended heavily on the chosen window.

The defensive ensemble showed smaller typical drawdowns *in this sample*, but sacrificed substantial upside and has no established predictive edge. It is a **risk-management research candidate**, not a purchase signal.

## Research priority before user funds $100

1. Freeze rule parameters before genuinely new incoming data; forward-only paper wallets on BTC and ETH, with transparent decision logs.
2. Validate executable execution timing and per-market Binance exchange filters, actual bid/ask spreads, and order-book slippage at small notionals.
3. Study diversified portfolio allocation from a *single* $100 wallet rather than treating 15 separate $100 experiments as one portfolio.
4. Demand strong independent and prospective net-of-cost evidence before considering any capital, and verify applicable Moroccan legal/regulatory requirements.
5. Do not activate real orders or accept credentials; seek separate explicit authorization only after all gates pass.

**Conclusion: historical BTC risk reduction is worth further paper research, but no strategy yet deserves a claim of guaranteed profitability.**
