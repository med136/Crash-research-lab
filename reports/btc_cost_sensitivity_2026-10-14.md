# Cost sensitivity and risk-matched BTC screen — 2026-10-14

## Frozen data provenance
- Public third-party repository: https://github.com/jptrustlearning/btc/blob/37f72830f8267e05b651515e8c3c263ef057d8e7/btc_prices.csv
- Fetched Git blob SHA: `e633106c023e80f48e404574952ed7b1f8bfe650`.
- 3343 daily observations, 2017-08-17 through 2026-10-11.
- **Caution:** archive is not exchange-audited execution-grade OHLCV and may reflect mixed external sourcing.

## Method
Spot long/cash. 200-day trailing close SMA, 30-day positive momentum, 30-day annualized realized volatility; 60% target volatility; 100% capped position.
Signals based strictly on previous completed daily data; simulated next-bar open fills.
13 sequential, non-overlapping 180-day evaluation windows from 2020-02-03 through 2026-06-30, each starting again with 1000 virtual cash.
Buy-and-hold buys once at first bar's open and liquidates once at final bar's close.
Numbers computed by a JS reproduction of the project's Python algorithm using the pinned public CSV. They remain **exploratory** because the strategy was earlier selected using overlapping history.

## Cost stress matrix

| Scenario | Buy/sell fee | Slippage | Trend mean 180d return | Passive mean 180d return | Excess mean | Excess median | Trend better windows | Mean maximum drawdown improvement |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Base | 0.10% | 0.05% | +24.321% | +23.798% | +0.523 pp | -3.277 pp | 6/13 | +23.520 pp |
| Double trading costs | 0.20% | 0.10% | +22.678% | +23.427% | -0.749 pp | -4.351 pp | 5/13 | +23.184 pp |
| Adverse slippage | 0.10% | 0.30% | +21.599% | +23.180% | -1.582 pp | -4.887 pp | 5/13 | +22.936 pp |

The return edge fails reasonable cost stresses, and the median paired excess return is negative in every case. The risk reduction is directionally interesting but it does not prove predictive skill; reduced time-in-market likely contributes.

## Decision
- **REJECT** any claim of robust return alpha or automatic profitability.
- **RETAIN** volatility-managed trend as a provisional lower-drawdown benchmark.
- **NO REAL ORDERS**, leverage, API secrets, or deposits.
- Next evidence requirements: official independent ETH and BTC venue data; prospective holdout after strategy freeze; GitHub CI results on the exact final SHA; forward paper quotes with realistic execution delay; exchange constraints and legal review.
- CI workflow `.github/workflows/research.yml` pins the source commit, checks Git blob hash, and archives JSON outcomes. Until the workflow run is confirmed, treat pipeline execution as unverified.
