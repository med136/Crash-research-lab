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
curl -fL https://raw.githubusercontent.com/jptrustlearning/btc/e633106c023e80f48e404574952ed7b1f8bfe650/btc_prices.csv -o data/btc_source.csv
python -c "from cryptolab.import_daily import import_daily; print(import_daily('data/btc_source.csv','data/btc_daily.csv'))"
cryptolab evaluate --input data/btc_daily.csv --capital 1000
```

The pinned URL above uses a Git blob SHA, which may not be directly fetchable as a Git revision on every Git hosting route; if GitHub returns 404, fetch `main/btc_prices.csv` and verify content against the recorded source blob SHA before comparing results. This is a third-party historical archive, not a live market stream. Use the close-of-day data only after the daily bar has completed.

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
