"""Fair spot buy-and-hold benchmark: exactly one entry and one exit."""
from __future__ import annotations
import math

def buy_and_hold(candles, start, end, *, initial=1000., fee=.001, slippage=.0005):
    if not (0<=start<end<=len(candles)) or end-start<2 or initial<=0:
        raise ValueError("Invalid window")
    if not (0<=fee<.1 and 0<=slippage<.1):
        raise ValueError("Invalid transaction costs")
    entry=float(candles[start]["open"])
    if not math.isfinite(entry) or entry<=0:
        raise ValueError("Invalid entry price")
    units=initial*(1-fee)/(entry*(1+slippage))
    marked=[units*float(candles[i]["close"]) for i in range(start,end)]
    if not all(math.isfinite(x) and x>0 for x in marked):
        raise ValueError("Invalid prices")
    final=marked[-1]*(1-fee)*(1-slippage)
    peak=initial
    dd=0.
    for equity in marked:
        peak=max(peak,equity)
        dd=min(dd,equity/peak-1)
    return {"return_pct":100*(final/initial-1),"max_drawdown_pct":100*dd,
            "trades":2,"final":final,"start_index":start,"end_index":end-1}
