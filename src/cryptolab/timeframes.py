"""Completed-candle multi-timeframe crypto research. Public spot market data only.

Timeframe horizons are *not* equal: 90 five-minute bars span 7.5 hours while
90 four-hour bars span fifteen days. Never rank raw returns between frames.
"""
from __future__ import annotations
import argparse
from datetime import date, datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import urllib.parse

from .audit_stats import paired_audit
from .market import API, validate
from .paired import paired_windows
from .universe import UNIVERSE, COSTS, _read_public

INTERVAL_MS = {"5m":300_000, "15m":900_000, "1h":3_600_000,
               "4h":14_400_000, "1d":86_400_000}
DEFAULT_SYMBOLS = ("BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","XRPUSDT","DOGEUSDT")
DEFAULT_FRAMES = ("5m","15m","1h","4h")
MIN_BARS = 630
MAX_BARS = 1000


def fetch_bars(symbol: str, interval: str, *, end: str, bars: int = 1000,
               fetch=_read_public) -> tuple[list[dict],dict]:
    """Fetch strict fixed-width UTC klines ending at a *completed* UTC date."""
    if symbol not in UNIVERSE or interval not in INTERVAL_MS:
        raise ValueError("Unsupported symbol/timeframe")
    if not MIN_BARS <= bars <= MAX_BARS:
        raise ValueError("Need 630 to 1000 bars for chronological research")
    cutoff = date.fromisoformat(end)
    if cutoff >= datetime.now(timezone.utc).date():
        raise ValueError("End date must precede current UTC date")
    step = INTERVAL_MS[interval]
    next_midnight = datetime(cutoff.year,cutoff.month,cutoff.day,tzinfo=timezone.utc)+timedelta(days=1)
    midnight_ms = int(next_midnight.timestamp()*1000)
    end_time = midnight_ms - 1
    last_open = midnight_ms - step
    params = urllib.parse.urlencode({"symbol":symbol,"interval":interval,"limit":bars,"endTime":end_time})
    raw = fetch(API+"?"+params)
    try:
        response=json.loads(raw)
    except (ValueError,UnicodeDecodeError) as exc:
        raise ValueError("Invalid public market response JSON") from exc
    if not isinstance(response,list) or len(response)!=bars:
        raise ValueError("Missing history bars from public market source")
    candles=[]
    for item in response:
        if not isinstance(item,list) or len(item)<7:
            raise ValueError("Malformed exchange kline")
        t=int(item[0])
        if t % step != 0 or int(item[6]) != t + step - 1:
            raise ValueError("Open/close timestamps do not match requested frame")
        candles.append({"time":t,"open":float(item[1]),"high":float(item[2]),
                        "low":float(item[3]),"close":float(item[4]),"volume":float(item[5])})
    validate(candles)
    if candles[-1]["time"] != last_open or candles[0]["time"] != last_open - (bars-1)*step:
        raise ValueError("Stale, incomplete, or missing candles in requested period")
    if any(b["time"]-a["time"] != step for a,b in zip(candles,candles[1:])):
        raise ValueError("Gap or duplicate detected in historical candles")
    return candles, {
        "symbol":symbol,"timeframe":interval,"bars":bars,"end_utc":end,
        "first_open_utc":datetime.fromtimestamp(candles[0]["time"]/1000,timezone.utc).isoformat(),
        "last_open_utc":datetime.fromtimestamp(candles[-1]["time"]/1000,timezone.utc).isoformat(),
        "raw_json_sha256":hashlib.sha256(raw).hexdigest(),
        "source":"Binance public SPOT klines (no API key, no live orders)",
    }


def evaluate_bars(candles: list[dict], *, interval: str,
                  first: int = 450, window: int = 90) -> dict:
    if interval not in INTERVAL_MS or first<450 or window<90 or first+2*window>len(candles):
        raise ValueError("Insufficient distinct forward windows")
    bars_per_year = (365*86_400_000)/INTERVAL_MS[interval]
    scenarios={}
    for label,(fee,slip) in COSTS.items():
        paired=paired_windows(candles,first=first,days=window,fee=fee,
                              slippage=slip,target=.60,bars_per_year=bars_per_year)
        audit=paired_audit(paired["folds"],bootstrap_samples=1000)
        scenarios[label]={
            "strategy_mean_pct":round(paired["summary"]["voltrend"]["mean_return_pct"],5),
            "passive_mean_pct":round(paired["summary"]["passive"]["mean_return_pct"],5),
            "excess_mean_pp":audit["mean_excess_return_pp"],
            "excess_median_pp":audit["median_excess_return_pp"],
            "drawdown_improvement_pp":audit["average_max_drawdown_improvement_pp"],
            "beats_passive_windows":audit["wins"],
            "fold_count":audit["folds"],
            "sign_test_p":audit["exact_two_sided_sign_p"],
            "trades":sum(f["voltrend"]["trades"] for f in paired["folds"]),
        }
    return {
        "timeframe":interval,
        "bars_per_year_for_volatility":bars_per_year,
        "indicator_lookback_bars":{"sma":200,"momentum":30,"realized_volatility":30},
        "window_bars":window,"window_hours":round(window*INTERVAL_MS[interval]/3_600_000,4),
        "folds":paired["fold_count"],
        "scenarios":scenarios,
        "warning":"Indicator horizons and test horizons differ by timeframe; never compare raw cross-timeframe returns.",
    }


def study(*, symbols: tuple[str,...] = DEFAULT_SYMBOLS,
          frames: tuple[str,...] = DEFAULT_FRAMES, end: str = "2026-09-30",
          bars: int = 1000, first: int = 450, window: int = 90,
          fetch=_read_public, min_success: int = 18) -> dict:
    if not symbols or not frames or len(set(symbols))!=len(symbols) or len(set(frames))!=len(frames):
        raise ValueError("Duplicate or empty symbols/timeframes")
    if any(s not in UNIVERSE for s in symbols) or any(f not in INTERVAL_MS for f in frames):
        raise ValueError("Unsupported symbol or timeframe")
    if len(symbols)*len(frames)>75 or not 1<=min_success<=len(symbols)*len(frames):
        raise ValueError("Invalid sample universe or threshold")
    output={
        "study":"CRYPTO_LAB_MULTI_TIMEFRAME_V1",
        "cutoff_utc":end,"symbols_requested":list(symbols),"frames_requested":list(frames),
        "bars_per_market":bars,"fold_size_bars":window,
        "strategy":"SMA200 + momentum30 + capped volatility targeting (60% annual vol)",
        "results":{},"errors":{},
        "cost_assumptions":{name:{"fee":f,"slippage":s} for name,(f,s) in COSTS.items()},
        "deployment_gate":"NO_REAL_ORDERS",
        "limitations":[
            "Short 5m/15m histories are not multiple market cycles.",
            "90-bar test windows represent different wall-clock periods for each frame.",
            "Annualized 5m realized volatility uses 105120 bars/year versus 365 for 1d.",
            "This technical diagnostic is not independent historical evidence of profitability.",
            "Fees and slippage are modeled; spreads, book impact and partial fills are not.",
            "Asset selection and model development can bias results; assets are correlated.",
        ],
    }
    for symbol in symbols:
        for frame in frames:
            key=symbol+"@"+frame
            try:
                candles,manifest=fetch_bars(symbol,frame,end=end,bars=bars,fetch=fetch)
                output["results"][key]={"data":manifest,
                                         "analysis":evaluate_bars(candles,interval=frame,
                                                                  first=first,window=window)}
            except (ValueError,KeyError,OSError,TimeoutError) as exc:
                output["errors"][key]=str(exc)
    output["successful_markets"]=len(output["results"])
    output["failed_markets"]=len(output["errors"])
    output["complete"]=not output["errors"]
    output["min_success_met"]=len(output["results"])>=min_success
    return output


def main() -> None:
    ap=argparse.ArgumentParser(description="Intraday paper-only research on completed Binance spot candles")
    ap.add_argument("--symbols",default=",".join(DEFAULT_SYMBOLS))
    ap.add_argument("--frames",default=",".join(DEFAULT_FRAMES))
    ap.add_argument("--end",default="2026-09-30")
    ap.add_argument("--bars",type=int,default=1000)
    ap.add_argument("--first",type=int,default=450)
    ap.add_argument("--window",type=int,default=90)
    ap.add_argument("--min-success",type=int,default=18)
    ap.add_argument("--output",required=True)
    ap.add_argument("--panel",required=True)
    args=ap.parse_args()
    from .intraday_panel import render_timeframe_panel
    out=study(symbols=tuple(args.symbols.split(",")),frames=tuple(args.frames.split(",")),
              end=args.end,bars=args.bars,first=args.first,window=args.window,
              min_success=args.min_success)
    output=Path(args.output);output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(out,indent=2,allow_nan=False),encoding="utf-8")
    panel=Path(args.panel);panel.parent.mkdir(parents=True,exist_ok=True)
    panel.write_text(render_timeframe_panel(out),encoding="utf-8")
    print(json.dumps({"passed":out["successful_markets"],"failed":out["failed_markets"],
                      "output":str(output),"panel":str(panel),"no_real_orders":True},indent=2))
    if not out["min_success_met"]:
        raise SystemExit("Insufficient validated crypto/timeframe pairs")


if __name__=="__main__":
    main()
