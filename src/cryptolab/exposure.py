"""Exposure-matched benchmark: constant-fraction BTC portfolio.

Separates benefits of market timing from benefits of simply holding less BTC.
Target is rebalanced only when deviation exceeds a threshold. Signal-free.
"""
from __future__ import annotations
import math

def constant_weight(candles, start, end, *, weight=.5, initial=1000.,
                    fee=.001, slippage=.0005, rebalance_threshold=.02):
    if not 0<=start<end<=len(candles) or end-start<2:
        raise ValueError("Invalid window")
    if not 0<=weight<=1 or initial<=0 or not 0<=rebalance_threshold<1:
        raise ValueError("Invalid allocation")
    cash=initial; units=0.; peak=initial; drawdown=0.; trades=0
    curve=[]
    for i in range(start,end):
        bar=candles[i]
        price=float(bar["open"])
        close=float(bar["close"])
        if not all(math.isfinite(x) and x>0 for x in (price,close)):
            raise ValueError("Invalid prices")
        value=cash+units*price
        current_weight=units*price/value
        if abs(current_weight-weight)>=rebalance_threshold:
            delta=(weight*value-units*price)/price
            if delta>0:
                spent=min(cash,delta*price*(1+fee+slippage))
                units+=spent/(price*(1+fee+slippage))
                cash-=spent
                trades+=1
            elif delta<0:
                sold=min(units,-delta)
                cash+=sold*price*(1-fee)*(1-slippage)
                units-=sold
                trades+=1
        equity=cash+units*close
        peak=max(peak,equity)
        drawdown=min(drawdown,equity/peak-1)
        curve.append(equity)
    final=cash+units*float(candles[end-1]["close"])*(1-fee)*(1-slippage)
    return {"return_pct":100*(final/initial-1),"max_drawdown_pct":100*drawdown,
            "trades":trades,"final":final,"curve":curve}
