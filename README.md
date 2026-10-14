# Crypto AI Trading Lab — Paper Trading MVP

This repository has been **repurposed** from Crash Research Lab to a completely separate **crypto market research** project. The repository name remains unchanged until its owner renames it in GitHub Settings.

Python tool for public completed BTC/ETH OHLCV candles and deterministic **paper-only backtests**. v0.1 uses a transparent moving-average benchmark, not yet an AI model.

## Install & test

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
python -m unittest discover -s tests -v

# Requires outbound Internet access:
cryptolab download --symbol BTCUSDT --interval 1h --output data/btc_1h.csv
cryptolab backtest --input data/btc_1h.csv --capital 1000
```

Uses the public Binance market-data endpoint and omits unfinished candles. Chronological signal on closed candles, next-bar-open hypothetical execution, 0.1% modeled trading fee and 0.05% slippage. Includes comparison to buy-and-hold and maximum drawdown. No exchange accounts, API secrets, live orders, leverage or real money.

**Research limitations:** Data retrieval is not yet verified from VPS; models have not been validated prospectively. Backtests are not reliable promises of future returns. Review applicable Moroccan regulations before any real financial activity.
