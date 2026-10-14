"""Reproducible multi-crypto public market comparison, never real orders.

All pairs share the same frozen UTC end date, bar count, fee assumptions,
history length, chronological folds, and baseline. The chosen universe is a
convenience sample of surviving pairs: results have survivorship/selection bias.
"""
from __future__ import annotations

import argparse
from datetime import date, datetime, timedelta, timezone
import hashlib
import json
import math
from pathlib import Path
import urllib.parse
import urllib.request

from .advisor import evaluate_closes
from .audit_stats import paired_audit
from .market import API, validate
from .paired import paired_windows

UNIVERSE = (
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT",
    "ADAUSDT", "DOGEUSDT", "LINKUSDT", "AVAXUSDT", "DOTUSDT",
    "LTCUSDT", "TRXUSDT", "BCHUSDT", "ATOMUSDT", "NEARUSDT",
)
DAY_MS = 86_400_000
COSTS = {
    "base": (.001, .0005),
    "double_cost": (.002, .001),
    "high_slippage": (.001, .003),
}


def _read_public(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "CryptoLab-PaperResearch/1.0"})
    with urllib.request.urlopen(request, timeout=35) as response:
        body = response.read(1_800_001)
    if len(body) > 1_800_000:
        raise ValueError("Public data response exceeds cap")
    return body


def fetch_daily(symbol: str, *, end: str, bars: int = 1000,
                fetch=_read_public) -> tuple[list[dict], dict]:
    if symbol not in UNIVERSE or not 600 <= bars <= 1000:
        raise ValueError("Unsupported symbol or number of daily bars")
    end_date = date.fromisoformat(end)
    if end_date >= datetime.now(timezone.utc).date():
        raise ValueError("Choose a completed UTC date, never the current daily candle")
    last_closed_ms = int(datetime(end_date.year,end_date.month,end_date.day,tzinfo=timezone.utc).timestamp()*1000)
    end_ms = last_closed_ms + DAY_MS - 1
    query = urllib.parse.urlencode({"symbol":symbol,"interval":"1d","limit":bars,"endTime":end_ms})
    url = API + "?" + query
    raw = fetch(url)
    try:
        arrays = json.loads(raw)
    except (ValueError, UnicodeDecodeError) as exc:
        raise ValueError("Invalid JSON from public Binance endpoint") from exc
    if not isinstance(arrays,list) or len(arrays)!=bars:
        raise ValueError(f"{symbol}: expected {bars} bars, received {len(arrays) if isinstance(arrays,list) else 'invalid'}")
    candles=[]
    for item in arrays:
        if not isinstance(item,list) or len(item)<7:
            raise ValueError("Malformed exchange kline")
        t=int(item[0]); end_t=int(item[6])
        if end_t != t + DAY_MS - 1:
            raise ValueError("Incorrect daily candle end timestamp")
        candles.append({"time":t,"open":float(item[1]),"high":float(item[2]),
                        "low":float(item[3]),"close":float(item[4]),"volume":float(item[5])})
    validate(candles)
    if candles[-1]["time"] != last_closed_ms:
        raise ValueError(f"{symbol}: stale feed, missing expected final candle")
    if any(b["time"] - a["time"] != DAY_MS for a,b in zip(candles,candles[1:])):
        raise ValueError(f"{symbol}: missing daily bars")
    if candles[0]["time"] != last_closed_ms - (bars-1)*DAY_MS:
        raise ValueError(f"{symbol}: inconsistent requested history")
    manifest = {
        "symbol":symbol,"end":end,"bars":bars,
        "first_utc":datetime.fromtimestamp(candles[0]["time"]/1000,timezone.utc).date().isoformat(),
        "last_utc":end,
        "raw_json_sha256":hashlib.sha256(raw).hexdigest(),
        "source":"Binance public SPOT market-only API",
    }
    return candles,manifest


def _condense(folds: list[dict]) -> dict:
    r=paired_audit(folds,bootstrap_samples=1000)
    return {
        "mean_excess_pp":r["mean_excess_return_pp"],
        "median_excess_pp":r["median_excess_return_pp"],
        "beats_hold_windows":r["wins"],
        "loses_to_hold_windows":r["losses"],
        "mean_drawdown_improvement_pp":r["average_max_drawdown_improvement_pp"],
        "sign_test_p":r["exact_two_sided_sign_p"],
        "is_prospective_evidence":False,
    }


def compare_coin(candles: list[dict], *, first: int = 450, days: int = 90) -> dict:
    validate(candles)
    if first < 450 or days < 60 or first + days > len(candles):
        raise ValueError("Need enough history for chronological folds")
    scenarios = {}
    for label,(fee,slippage) in COSTS.items():
        paired = paired_windows(candles,first=first,days=days,target=.60,fee=fee,slippage=slippage)
        stat = _condense(paired["folds"])
        stat["voltrend_mean_return_pct"] = round(paired["summary"]["voltrend"]["mean_return_pct"],4)
        stat["hold_mean_return_pct"] = round(paired["summary"]["passive"]["mean_return_pct"],4)
        stat["mean_voltrend_max_drawdown_pct"] = round(paired["summary"]["voltrend"]["mean_max_drawdown_pct"],4)
        stat["folds"] = paired["fold_count"]
        scenarios[label] = stat
    base_folds = paired_windows(candles,first=first,days=days,target=.60,fee=.001,slippage=.0005)["folds"]
    trend = [f["voltrend"]["return_pct"] for f in base_folds]
    benchmark = [f["passive"]["return_pct"] for f in base_folds]
    return {
        "scenarios":scenarios,
        "advisor":evaluate_closes([x["close"] for x in candles]),
        "base_folds":[
            {"start_index":f["start_index"],"end_index":f["end_index"],
             "strategy_return_pct":round(t,4),"hold_return_pct":round(h,4),
             "strategy_drawdown_pct":round(f["voltrend"]["max_drawdown_pct"],4),
             "hold_drawdown_pct":round(f["passive"]["max_drawdown_pct"],4)}
            for f,t,h in zip(base_folds,trend,benchmark)
        ],
    }


def study(*, symbols: tuple[str,...] = UNIVERSE, end: str = "2026-09-30",
          bars: int = 1000, first: int = 450, days: int = 90,
          fetch=_read_public, min_success: int = 10) -> dict:
    if not symbols or len(symbols)>len(UNIVERSE) or len(set(symbols)) != len(symbols):
        raise ValueError("Empty, duplicate or excessively large crypto universe")
    if any(symbol not in UNIVERSE for symbol in symbols):
        raise ValueError("Unsupported asset in crypto universe")
    if not 1<=min_success<=len(symbols):
        raise ValueError("Invalid minimum successful symbols")
    result = {
        "study":"CRYPTO_LAB_CROSS_SECTIONAL_RESEARCH_V1",
        "data_cutoff_utc":end,"requested_bars":bars,"warmup_first_index":first,
        "fold_bars":days,"symbols_requested":list(symbols),
        "cost_assumptions":{k:{"fee":v[0],"slippage":v[1]} for k,v in COSTS.items()},
        "results":{},"errors":{},
        "deployment_gate":"NO_REAL_ORDERS",
        "limitations":[
            "Current listed pairs create survivorship bias; not a historical universe.",
            "Asset returns are correlated: 15 pairs are not 15 independent experiments.",
            "Earlier BTC model development reused part of this history; NOT pristine validation.",
            "All fills are hypothetical and depend on exchange costs and actual liquidity.",
            "The advisor's vote score is an interpretable heuristic, NOT ML or calibrated probability.",
        ],
    }
    for symbol in symbols:
        try:
            candles,provenance = fetch_daily(symbol,end=end,bars=bars,fetch=fetch)
            result["results"][symbol] = {"provenance":provenance,"research":compare_coin(candles,first=first,days=days)}
        except (ValueError, KeyError, OSError, TimeoutError, urllib.error.URLError) as exc:
            result["errors"][symbol] = str(exc)
    result["successful_symbols"] = len(result["results"])
    result["failed_symbols"] = len(result["errors"])
    result["complete"] = result["successful_symbols"] == len(symbols)
    result["min_success_met"] = result["successful_symbols"] >= min_success
    return result


def main() -> None:
    ap=argparse.ArgumentParser(description="15-public-pair crypto research; no real orders")
    ap.add_argument("--symbols",default=",".join(UNIVERSE))
    ap.add_argument("--end",default="2026-09-30")
    ap.add_argument("--bars",type=int,default=1000)
    ap.add_argument("--first",type=int,default=450)
    ap.add_argument("--days",type=int,default=90)
    ap.add_argument("--min-success",type=int,default=10)
    ap.add_argument("--output",required=True)
    ap.add_argument("--panel",required=True,help="Static HTML review panel output")
    args=ap.parse_args()
    selected=tuple(args.symbols.split(","))
    report=study(symbols=selected,end=args.end,bars=args.bars,first=args.first,
                 days=args.days,min_success=args.min_success)
    path=Path(args.output);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(report,indent=2,allow_nan=False),encoding="utf-8")
    from .panel import render_panel
    html=Path(args.panel);html.parent.mkdir(parents=True,exist_ok=True)
    html.write_text(render_panel(report),encoding="utf-8")
    print(json.dumps({"output":str(path),"panel":str(html),
                      "successful_symbols":report["successful_symbols"],
                      "failed_symbols":report["failed_symbols"],
                      "min_success_met":report["min_success_met"]},indent=2))
    if not report["min_success_met"]:
        raise SystemExit("Too few successfully validated market histories")


if __name__=="__main__":
    main()
