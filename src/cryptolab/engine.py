"""Causal spot-only moving-average paper backtest.

Signal is calculated after bar i closes; transaction occurs at bar i+1 open.
No leverage, no shorts, no look-ahead; one asset with fractional sizing.
"""
from dataclasses import dataclass

@dataclass
class Result:
    initial:float
    final:float
    return_pct:float
    buy_hold_pct:float
    max_drawdown_pct:float
    trades:int
    curve:list

def signal(closes,fast=10,slow=30):
    if not 1<fast<slow<=len(closes):
        return 0
    return int(sum(closes[-fast:])/fast > sum(closes[-slow:])/slow)

def backtest(candles,initial=1000.0,fee=0.001,slippage=0.0005,fast=10,slow=30):
    if len(candles)<slow+2 or initial<=0 or not (0<=fee<0.1 and 0<=slippage<0.1) or not 1<fast<slow:
        raise ValueError("Invalid parameters")
    cash=initial; asset=0.0; trades=0; equities=[initial]
    for i in range(slow,len(candles)):
        desired=signal([c["close"] for c in candles[:i]],fast,slow)
        price=candles[i]["open"]
        if desired and asset==0:
            asset=(cash*(1-fee))/(price*(1+slippage))
            cash=0.0; trades+=1
        elif not desired and asset>0:
            cash=asset*price*(1-slippage)*(1-fee)
            asset=0.0;trades+=1
        equities.append(cash+asset*candles[i]["close"])
    final=cash+asset*candles[-1]["close"]*(1-fee)*(1-slippage)
    peak=equities[0];worst=0.0
    for v in equities:
        peak=max(peak,v)
        worst=min(worst,(v/peak-1))
    buyhold=initial*(1-fee)/(candles[slow]["open"]*(1+slippage))
    buyhold=buyhold*candles[-1]["close"]*(1-fee)*(1-slippage)
    return Result(initial,final,100*(final/initial-1),
                  100*(buyhold/initial-1),100*worst,trades,equities)
