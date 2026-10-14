# Crypto AI Trading Lab — paper-only research

The former Crash Research Lab has been replaced by this independent cryptocurrency trading **research** project. This is not a profitable AI trading bot yet: v0.2 evaluates transparent moving-average benchmarks, with no real-money orders.

## Install and test

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
python -m unittest discover -s tests -v
```

## Genuine data, chronological comparison and backtest

```bash
cryptolab download --symbol BTCUSDT --interval 1h --output data/btc.csv
cryptolab evaluate --input data/btc.csv --capital 1000
cryptolab backtest --input data/btc.csv --fast 10 --slow 30
```

Market-only Binance API: https://data-api.binance.vision/api/v3/klines (no API key). Historical bulk archive: https://data.binance.vision/. Source availability varies by region; download was not verified in this runtime.

The evaluation tests **four** SMA configurations, chooses parameters using the first 65% of completed candles, and reports performance on the untouched last 35% after simulated fees (0.1%) and slippage (0.05%). Metrics include maximum drawdown and buy-and-hold comparison. A single good holdout does **not** prove profitability.

## Stateful paper portfolio

```bash
cryptolab paper --symbol BTCUSDT --interval 1h --state data/btc_paper.json --capital 1000
```

Run once after each hourly candle closes. First invocation initializes a wallet (no imaginary historical trades); later invocations only consume newly completed observations, with missing-bar detection and an atomically persisted local snapshot. Only one writer per state file. Hypothetical fills at subsequent observed completed closes are deliberately distinguished from next-open historical fills.

No leverage, exchange secrets, real orders or deposits. Only run with money-free simulations. Before any actual crypto transactions, consult applicable Moroccan financial rules.

## Release status

Local unit tests: 13 tests passed in the development environment. GitHub CI and live exchange data availability need independent verification. No validated profitable strategy and no AI model have been delivered.


## Reproducing the 2026-10-14 BTC history audit

A publicly published third-party CSV has 3,343 BTC daily candles (2017-08-17 to 2026-10-11); record and SHA in `reports/btc_daily_holdout_2026-10-14.md`.

```bash
curl -fL https://raw.githubusercontent.com/jptrustlearning/btc/37f72830f8267e05b651515e8c3c263ef057d8e7/btc_prices.csv -o data/btc_source.csv
python -c "from cryptolab.import_daily import import_daily; print(import_daily('data/btc_source.csv','data/btc_daily.csv'))"
cryptolab evaluate --input data/btc_daily.csv --capital 1000
```

The pinned URL uses a **source commit SHA**. Verify the downloaded bytes using `git hash-object data/btc_source.csv`, which must equal `e633106c023e80f48e404574952ed7b1f8bfe650`; refuse to continue if it differs. This is a third-party historical archive, not a live market stream. Use the close-of-day data only after the daily bar has completed.

## Acceptance gates (not yet passed)

- All GitHub Actions jobs green on the final commit.
- Independent verification of real market downloads and deterministic source provenance.
- Validated forward-only paper trading on a VPS with daily monitoring and a loss/incident log.
- Multiple untouched rolling test periods and different market regimes.
- Net performance versus buy-and-hold, cash, and fees/slippage stress tests.
- No real trading until local legal requirements are verified and the user explicitly authorizes it.

A numeric `10/10` or a `profitable bot` designation is inappropriate until all relevant gates have real evidence.


## Expanding-window walk-forward validation

```bash
cryptolab walk-forward --input data/btc_daily.csv --initial-train 900 --test-size 180 --step 180
```

For each fold, select volatility target only from earlier historical bars and test it on the next 180 completed daily candles. No portfolio state is carried between folds; both the strategy and passive baseline restart with the same virtual capital. Inspect individual fold results, not just average performance.

**Release blocker:** GitHub Actions status for this change has not been verified; public-data ingestion and live paper execution still need end-to-end checking. Historical returns are hypothetical and not guarantees.


## Risk-matched paired strategy evaluation

```bash
cryptolab paired --input data/btc_daily.csv --first 900 --days 180
```

This evaluates the volatility trend model and **signal-free constant BTC allocations (25%, 50%, 75%)**, plus one-entry/one-exit passive BTC in identical chronological 180-bar windows. Costs are applied to all simulated fills. This is a more defensible test of whether trend timing adds more than reduced BTC exposure. The numerical output still requires verification on a clean local checkout and independently sourced prices. Do not call it proof of a profitable edge.

See `reports/exposure_controls_2026-10-14.md` for a historical exploratory comparison and caveats.


## Audited costs and historical validation CI (2026-10-14)

```bash
cryptolab audit --input data/btc_daily.csv --first 900 --days 180
```

The `audit` command compares the frozen Volatility Trend benchmark to passive BTC across identical 180-day windows in three cost scenarios (base, doubled costs, high slippage); outputs a deterministic JSON report with medians, sign-test diagnostics, bootstrap intervals, exposure controls and a strict `NO_REAL_ORDERS` decision.

- `.github/workflows/research.yml` runs Python tests and downloads the pinned 3343-bar BTC CSV, checks its Git blob fingerprint, imports validated daily bars, then runs `paired`, `audit`, and `walk-forward`.
- PR #2 verified the **historical-validation** job and **Python tests** as successful on the proposed commit (2026-10-14), before merge. Reports are available as the GitHub Actions artifact `btc-research-no-orders`.
- Full workflow execution verifies computational reproducibility, **not profitability, statistical significance, exchange fill realism, or legal permission for live orders**.
- Research report: `reports/btc_cost_sensitivity_2026-10-14.md`. Under doubled costs/high slippage the small historical return advantage disappears; real-money deployment remains **NO-GO**.


## Verified official Binance SPOT archives (BTC and ETH)

Binance provides free public monthly SPOT 1d ZIP archives and companion `.CHECKSUM` files. A tested importer validates SHA-256, exact UTC daily timestamps, full month completeness, OHLCV values, and the January 2025 switch from milliseconds to microseconds.

```bash
# Research only; no private API credentials or live orders.
python -m cryptolab.binance_bulk --symbol BTCUSDT --start 2024-01 --end 2025-12 --output data/binance_btc.csv
python -m cryptolab.binance_bulk --symbol ETHUSDT --start 2024-01 --end 2025-12 --output data/binance_eth.csv

# The importer generates sidecar manifests containing each archive's verified SHA-256.
cryptolab paired --input data/binance_btc.csv --first 450 --days 90
cryptolab audit --input data/binance_eth.csv --first 450 --days 90
```

Note: the commands above **do not run automatically on any user's machine**. GitHub Actions on PR #3 verified real January 2025 public Binance BTC and ETH archive downloads and all Python/historical research checks, on 2026-10-14. A 90-day evaluation is exploratory; no live trading.


## Daily volatility-trend virtual wallet (paper only, experimental)

The legacy `cryptolab paper` command uses a basic SMA strategy on hourly data.
**The candidate researched on daily data is implemented separately** as `paper-vol`, to prevent silently substituting one model for the other.

```bash
# 1. Offline simulation from a verified CSV: creates a state but no historical trades.
cryptolab paper-vol --symbol BTCUSDT --input data/binance_btc.csv --state data/btc_offline_wallet.json

# 2. Re-run after appending the next completed day in the CSV. Only that new
# day can change holdings; rerunning identical data never duplicates trades.
cryptolab paper-vol --symbol BTCUSDT --input data/binance_btc.csv --state data/btc_offline_wallet.json

# 3. Optional public API observation, NO REAL ORDERS. Invoke once daily
# after the UTC daily candle is closed and published; first run only initializes.
cryptolab paper-vol --symbol BTCUSDT --state data/btc_daily_wallet.json
```

### Safety and practical limitations

- **No real crypto trades, private exchange endpoints, exchange API keys, real deposits, leverage, or automated real orders.**
- First run only initializes from 201+ consecutive completed 1d candles. No retroactive entry is invented.
- Each later run processes only strictly consecutive, newly completed candles. A missing bar, stale public feed, modified last bar, wrong market, corrupted state, or duplicate active process fails closed.
- Portfolio snapshots are JSON, written atomically with a lock. A stale `.lock` after a process crash requires human inspection before removal. Use separate state filenames for BTC and ETH; keep this state outside source control.
- Each next-candle decision is based exclusively on prior completed closes. **Virtual fills at a newly observed daily close are a simplifying assumption, not an executable next-bar-open fill or a real exchange quote.** Do not compare its result directly with the earlier `voltrend.run` backtest without aligning fills and data timestamps.
- The `--input` mode is an **offline historical replay**, not live paper trading. The API mode fetches public latest 1d data but is NOT deployed as a daemon or scheduled on any VPS.
- The volatility target is frozen to 60% as an exploratory research assumption, not proof that it improves risk-adjusted returns; historical return advantages disappear under adverse costs.
- GitHub CI verifies cold start/idempotent rerun on historical CSV; longer prospective operations, exchange feasibility, and legal review remain release blockers.


## 15-crypto comparative research dashboard (paper only)

```bash
python -m cryptolab.universe \
  --symbols BTCUSDT,ETHUSDT,BNBUSDT,SOLUSDT,XRPUSDT,ADAUSDT,DOGEUSDT,LINKUSDT,AVAXUSDT,DOTUSDT,LTCUSDT,TRXUSDT,BCHUSDT,ATOMUSDT,NEARUSDT \
  --end 2026-09-30 --bars 1000 --first 450 --days 90 --min-success 12 \
  --output reports/universe_15.json --panel reports/universe_panel.html
```

Open `reports/universe_panel.html` in a browser. No hosting or JavaScript dependencies required; the panel is an interactive static offline research report (table sorting, search, per-asset chronological folds, transparent advisor regime, cost stress).

- Uses public Binance market-only REST API: fixed common UTC last candle and 1000 completed 1-day bars, with exact chronology checks, SHA-256 for each raw response, and explicit errors for unavailable pairs.
- Each asset runs the same Volatility Trend model vs spot buy-and-hold with *three* fee/slippage scenarios; never omit failures or equate its advisor's interpretable rule votes with ML probabilities.
- 15 currently listed assets are **not** 15 statistically independent samples (strong return correlations), and historical selection introduces survivorship bias.
- Returns are mean per non-overlapping 90-day virtual reset window, not annualized returns. The initial 450 days support indicators; all folds are chronological.
- The static HTML and JSON are stored as GitHub Actions artifacts. They are **not live dashboards** and do not update until a new research run executes. They do not execute orders.
- `NO_REAL_ORDERS` remains mandatory; neither spot profitability nor a machine-learned predictive model has been established.


## FR / EN Dashboard and smaller timeframes (5m / 15m / 1h / 4h)

Both the original 15-crypto 1d panel and the new intraday panel provide a **FR / EN** language switch. **French is the default**; English remains available without network translation or external JavaScript.

The smaller-timeframe research protocol compares six public Binance Spot USDT markets (BTC, ETH, BNB, SOL, XRP, DOGE) over the same *completed UTC cutoff* and 1,000 chronological OHLCV bars **per pair and timeframe**:

```bash
python -m cryptolab.timeframes \
  --symbols BTCUSDT,ETHUSDT,BNBUSDT,SOLUSDT,XRPUSDT,DOGEUSDT \
  --frames 5m,15m,1h,4h --end 2026-09-30 \
  --bars 1000 --first 450 --window 90 --min-success 20 \
  --output reports/timeframes_24.json --panel reports/timeframes_panel.html
```

Open `reports/timeframes_panel.html` to filter pairs and frames in French or English. The JSON lists every failed / excluded market.

**Important methodology:** 90 x 5-minute candles cover **7.5 hours**, whereas 90 x 4-hour candles cover **15 days**. Raw per-window returns must **never** be ranked between these different timeframes; only compare each strategy with its same-window benchmark. The technical strategy uses *200/30/30 bars*, not calendar days, for each frame. Its 30-bar log-return volatility is annualized with the correct frequency (5m = 105120 bars/year, 15m = 35040, 1h = 8760, 4h = 2190; 1d = 365).

The test is not a high-frequency live execution simulator: it omits realistic spread dynamics, depth, market impact and partial fills. Small intervals may generate frequent transactions and are sensitive to underestimated fees. Research remains paper-only, without exchange credentials, real orders, or a claim that any algorithm is profitable.


## User-funded $100 research: 1, 3, 6, and 12 months

The user's **proposed $100** is not transferred to us or deployed. This offline tool shows *what past independent $100 wallets would have become*, under fixed public-market assumptions; it **does not predict** how much an actual $100 investment will be worth.

```bash
python -m cryptolab.capital100 \
  --symbols BTCUSDT,ETHUSDT,BNBUSDT,SOLUSDT,XRPUSDT,ADAUSDT,DOGEUSDT,LINKUSDT,AVAXUSDT,DOTUSDT,LTCUSDT,TRXUSDT,BCHUSDT,ATOMUSDT,NEARUSDT \
  --end 2026-09-30 --bars 1000 --min-success 12 \
  --output reports/100usd_horizons.json --panel reports/100usd_horizons_panel.html
```

Open the FR-first/EN-switch `reports/100usd_horizons_panel.html` dashboard and select asset, 30/90/180/365-day approximate horizon, strategy, and base/doubled/adverse costs.

Fixed, non-optimized, research-only candidates: all cash, spot buy-and-hold, SMA20/60, SMA50/200, Donchian-like 55/20 breakout, capped 60%-family volatility trend with 45% volatility target, and a defensive rule-based ensemble. These are **heuristics, not trained models**. Every candle's entry uses completed previous-close indicators and hypothetical next-open fills; no leverage; transaction fees, slippage, a modeled $5 minimum notional and terminal exit costs are charged. Each chronological nonoverlapping historical window restarts with **one $100 virtual wallet per tested asset** — NOT a single $100 portfolio invested simultaneously in 15 coins.

For each horizon, report mean/median/worst/best/p10/p90 final USD balances, count of positive windows, paired excess over buy-and-hold, drawdown, and turnover. **There are only 2 independent annual windows per asset in 1000 daily bars**, so annual forecasts or win probabilities are not justified. Multiple testing across 15 correlated assets and 7 strategies would overstate statistical evidence if one simply selected the historic winner.

No crypto funds, wallet keys, real orders, or deployments occur. A strategy must undergo genuinely prospective paper evaluation and exchange-filter checks before any further consideration.
