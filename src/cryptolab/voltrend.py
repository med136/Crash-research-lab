"""Research-only volatility-targeted trend filter (spot / cash).

Signals are computed exclusively from completed previous candles. Fills occur at
next candle open. Position targets are capped at 100%, never leveraged.
"""
from __future__ import annotations
import math

def run(candles, *, trend_days=200, momentum_days=30, vol_days=30,
        vol_target=.40, initial=1000., fee=.001, slippage=.0005,
        start_at=None, bars_per_year=365.):
    warmup=max(trend_days,momentum_days,vol_days+1)+1
    start=max(warmup,start_at or warmup)
    if len(candles)<=start or initial<=0 or not 0<vol_target<=1 or not math.isfinite(bars_per_year) or bars_per_year<=0:
        raise ValueError("Invalid data or target")
    cash=initial; units=0.; peak=initial; max_dd=0.; trades=0
    equity_curve=[]
    for i in range(start,len(candles)):
        history=candles[:i]
        closes=[b["close"] for b in history]
        avg=sum(closes[-trend_days:])/trend_days
        momentum=closes[-1]/closes[-1-momentum_days]-1
        rets=[math.log(closes[j]/closes[j-1]) for j in range(len(closes)-vol_days,len(closes))]
        mu=sum(rets)/len(rets)
        annual_vol=math.sqrt(bars_per_year*sum((r-mu)**2 for r in rets)/len(rets))
        target=min(1.,vol_target/max(annual_vol,.05)) if closes[-1]>avg and momentum>0 else 0.
        price=candles[i]["open"]
        equity=cash+units*price
        desired_units=equity*target/price
        delta=desired_units-units
        # Fees and slippage paid on each rebalance; no borrowing
        if delta>0:
            spent=min(cash,delta*price*(1+fee+slippage))
            added=spent/(price*(1+fee+slippage))
            if added*price>equity*.001:
                cash-=spent;units+=added;trades+=1
        elif delta<0:
            sold=min(units,-delta)
            if sold*price>equity*.001:
                cash+=sold*price*(1-fee-slippage);units-=sold;trades+=1
        marked=cash+units*candles[i]["close"]
        equity_curve.append(marked);peak=max(peak,marked)
        max_dd=min(max_dd,marked/peak-1)
    final=cash+units*candles[-1]["close"]*(1-fee-slippage)
    return {"return_pct":100*(final/initial-1),"max_drawdown_pct":100*max_dd,
            "trades":trades,"final":final,"curve":equity_curve,
            "method":"trailing SMA + positive momentum + capped inverse volatility"}
