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
