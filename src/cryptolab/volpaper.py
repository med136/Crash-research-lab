"""Forward-only DAILY volatility-trend virtual portfolio.

This is a ledger for research only: fills are *hypothetical* at the newly
observed completed candle's close. That close was not necessarily executable
when the candle became available. No exchange orders or private credentials.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path

from .market import download, load, validate

DAY_MS = 86_400_000
HISTORY_LENGTH = 201
STATE_VERSION = 2
MODEL = "volatility_trend_daily_v1"


def target_from_history(closes: list[float], *, vol_target: float = .60) -> float:
    """Match voltrend.run indicators, calculated only after bar completion."""
    if len(closes) < HISTORY_LENGTH or not 0 < vol_target <= 1:
        raise ValueError("Need 201 valid daily closes and a capped vol target")
    seq = closes[-HISTORY_LENGTH:]
    if not all(math.isfinite(v) and v > 0 for v in seq):
        raise ValueError("Non-finite or non-positive closing price")
    trend = sum(seq[-200:]) / 200
    momentum = seq[-1] / seq[-31] - 1
    recent = [math.log(seq[i] / seq[i - 1]) for i in range(171, 201)]
    avg = sum(recent) / 30
    annual_vol = math.sqrt(365 * sum((r - avg) ** 2 for r in recent) / 30)
    if seq[-1] <= trend or momentum <= 0:
        return 0.
    return min(1., vol_target / max(annual_vol, .05))


def _contiguous(candles: list[dict]) -> None:
    validate(candles)
    if any(b["time"] - a["time"] != DAY_MS for a, b in zip(candles, candles[1:])):
        raise ValueError("Missing/duplicate daily candles: refusing simulation")


def initialize(candles: list[dict], *, symbol: str, initial: float = 1000.,
               fee: float = .001, slippage: float = .0005,
               vol_target: float = .60, source: str = "public_api") -> dict:
    if symbol not in ("BTCUSDT", "ETHUSDT") or source not in ("public_api", "csv_replay"):
        raise ValueError("Invalid symbol or source")
    _contiguous(candles)
    if len(candles) < HISTORY_LENGTH or not math.isfinite(initial) or initial <= 0:
        raise ValueError("Need at least 201 consecutive candles and positive capital")
    if not (0 <= fee < .1 and 0 <= slippage < .1):
        raise ValueError("Unacceptable fee or slippage")
    history = [c["close"] for c in candles[-HISTORY_LENGTH:]]
    return {
        "version": STATE_VERSION, "model": MODEL, "symbol": symbol,
        "interval": "1d", "source": source, "initial": float(initial),
        "cash": float(initial), "units": 0., "fee":fee, "slippage":slippage,
        "vol_target":vol_target, "last_time":candles[-1]["time"],
        "last_close":candles[-1]["close"], "history": history,
        "pending_target":target_from_history(history,vol_target=vol_target),
        "trades":[], "equity": [float(initial)],
    }


def _validate_state(s: dict) -> None:
    if s.get("version") != STATE_VERSION or s.get("model") != MODEL:
        raise ValueError("State incompatible: do not reuse old SMA paper ledger")
    if s.get("symbol") not in ("BTCUSDT", "ETHUSDT") or s.get("interval") != "1d":
        raise ValueError("State symbol or interval invalid")
    if s.get("source") not in ("public_api", "csv_replay"):
        raise ValueError("Invalid ledger source")
    for name in ("cash", "units", "initial", "fee", "slippage", "vol_target", "last_close", "pending_target"):
        x = s.get(name)
        if not isinstance(x, (int,float)) or not math.isfinite(x):
            raise ValueError("Corrupt ledger number: " + name)
    if s["cash"] < 0 or s["units"] < 0 or s["initial"] <= 0 or s["last_close"] <= 0:
        raise ValueError("Invalid ledger balances")
    if not 0 <= s["pending_target"] <= 1 or not 0 < s["vol_target"] <= 1:
        raise ValueError("Invalid leverage/exposure target")
    if not 0 <= s["fee"] < .1 or not 0 <= s["slippage"] < .1:
        raise ValueError("Invalid ledger transaction cost")
    if not isinstance(s.get("last_time"), int) or not isinstance(s.get("history"),list):
        raise ValueError("Corrupt state chronology")
    if len(s["history"]) != HISTORY_LENGTH or not isinstance(s.get("trades"),list) or not isinstance(s.get("equity"),list):
        raise ValueError("Corrupt state history")


def step(state: dict, candle: dict) -> dict:
    _validate_state(state)
    t = candle["time"]
    if not isinstance(t, int):
        raise ValueError("Invalid candle timestamp")
    if t == state["last_time"]:
        if candle["close"] != state["last_close"]:
            raise ValueError("Conflicting candle revision: refusing stale data")
        return state
    if t != state["last_time"] + DAY_MS:
        raise ValueError("Out-of-order or missing daily candle")
    close = float(candle["close"])
    if not math.isfinite(close) or close <= 0:
        raise ValueError("Invalid completed daily close")
    # Work on a copy; reject invalid states without partially altering the ledger.
    updated = deepcopy(state)
    eq = updated["cash"] + updated["units"] * close
    target = updated["pending_target"]
    delta = (eq * target / close) - updated["units"]
    notional = abs(delta) * close
    # Ignore < 0.1% notional rebalance to avoid excessive dust trades.
    if notional > eq * .001:
        if delta > 0:
            spent = min(updated["cash"], notional * (1 + updated["fee"] + updated["slippage"]))
            bought = spent / (close * (1 + updated["fee"] + updated["slippage"]))
            updated["cash"] -= spent
            updated["units"] += bought
            side, quantity = "BUY", bought
        else:
            quantity = min(updated["units"], -delta)
            updated["cash"] += quantity * close * (1 - updated["fee"] - updated["slippage"])
            updated["units"] -= quantity
            side = "SELL"
        updated["trades"].append({
            "time": t, "side": side, "observed_close": close, "quantity":quantity,
            "target_from_previous_candle":target,
            "fill_assumption":"hypothetical_at_observed_close",
        })
    updated["last_time"] = t
    updated["last_close"] = close
    updated["history"] = (updated["history"] + [close])[-HISTORY_LENGTH:]
    updated["pending_target"] = target_from_history(updated["history"],vol_target=updated["vol_target"])
    updated["equity"].append(updated["cash"] + updated["units"] * close)
    _validate_state(updated)
    return updated


def advance(state: dict, candles: list[dict]) -> dict:
    _validate_state(state)
    _contiguous(candles)
    current = deepcopy(state)
    newer = [c for c in candles if c["time"] > current["last_time"]]
    for candle in newer:
        current = step(current, candle)
    # If no newer candle, an inconsistent copy of the last candle must still fail.
    matched = [c for c in candles if c["time"] == current["last_time"]]
    if matched and matched[0]["close"] != current["last_close"]:
        raise ValueError("Last completed candle changed: refusing to continue")
    return current


def report(state: dict) -> dict:
    _validate_state(state)
    equity = state["cash"] + state["units"] * state["last_close"]
    return {
        "paper_only":True, "model":MODEL, "symbol":state["symbol"],
        "source":state["source"], "last_candle":state["last_time"],
        "cash":round(state["cash"],6), "units":round(state["units"],10),
        "equity":round(equity,4), "pnl_pct":round(100*(equity/state["initial"]-1),4),
        "executions":len(state["trades"]), "next_target":round(state["pending_target"],5),
        "execution_note":"Hypothetical fill at observed completed candle close, not a market executable quote",
    }


@contextmanager
def state_lock(path: Path):
    lock = Path(str(path) + ".lock")
    path.parent.mkdir(parents=True,exist_ok=True)
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise RuntimeError(f"Another paper run may be active: {lock}") from exc
    try:
        with os.fdopen(fd, "w") as f:
            f.write(f"pid={os.getpid()}\n")
        yield
    finally:
        lock.unlink(missing_ok=True)


def persist(state: dict, path: Path) -> None:
    _validate_state(state)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = Path(str(path) + ".tmp")
    with temp.open("w",encoding="utf-8") as stream:
        json.dump(state,stream,indent=2,allow_nan=False)
        stream.flush()
        os.fsync(stream.fileno())
    temp.replace(path)


def once(*, symbol: str, path: str, capital: float = 1000.,
         input_csv: str | None = None) -> dict:
    if symbol not in ("BTCUSDT","ETHUSDT"):
        raise ValueError("Unsupported market pair")
    source = "csv_replay" if input_csv else "public_api"
    candles = load(input_csv) if input_csv else download(symbol=symbol,interval="1d",n=1000)
    _contiguous(candles)
    if source == "public_api":
        today = datetime.now(timezone.utc).date()
        expected = int(datetime(today.year,today.month,today.day,tzinfo=timezone.utc).timestamp()*1000)-DAY_MS
        if candles[-1]["time"] != expected:
            raise ValueError("Stale/incomplete public daily feed; refusing state changes")
    location = Path(path)
    with state_lock(location):
        if location.exists():
            state = json.loads(location.read_text(encoding="utf-8"))
            _validate_state(state)
            if state["symbol"] != symbol or state["source"] != source:
                raise ValueError("Cannot reuse wallet for a different symbol/feed")
            updated = advance(state, candles)
        else:
            updated = initialize(candles,symbol=symbol,initial=capital,source=source)
        persist(updated,location)
    return report(updated)


def main() -> None:
    parser=argparse.ArgumentParser(description="Forward-only crypto virtual portfolio; no orders")
    parser.add_argument("--symbol",choices=["BTCUSDT","ETHUSDT"],required=True)
    parser.add_argument("--state",required=True)
    parser.add_argument("--capital",type=float,default=1000.)
    parser.add_argument("--input",default=None,help="Offline CSV replay, never a live quote")
    args=parser.parse_args()
    print(json.dumps(once(symbol=args.symbol,path=args.state,capital=args.capital,input_csv=args.input),indent=2))


if __name__ == "__main__":
    main()
