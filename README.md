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
