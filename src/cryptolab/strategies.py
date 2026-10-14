"""Experimental risk-managed trend/breakout strategies.

All decisions for index i are computed from candles[:i]; trades fill at
candle[i].open. Spot only, no leverage, fees and slippage included.
"""
from __future__ import annotations
from dataclasses import dataclass
import math

@dataclass(frozen=True)
class Strategy:
    name: str
    trend: int = 100
    breakout: int = 20
    stop_atr: float = 3.0
    risk_fraction: float = 0.5

CANDIDATES = [
    Strategy("breakout_20_trend100",100,20,3.0,0.5),
    Strategy("breakout_50_trend200",200,50,3.0,0.5),
    Strategy("breakout_20_trend200",200,20,4.0,0.75),
    Strategy("breakout_40_trend100",100,40,4.0,0.75),
]

def run(candles: list[dict], strategy: Strategy, *, initial=1000.0,
        fee=.001, slippage=.0005, begin_at: int | None=None) -> dict:
    warmup=max(strategy.trend,strategy.breakout,15)+1
    start=max(warmup,begin_at or warmup)
    if len(candles) <= start or initial<=0 or not (0<=fee<.1 and 0<=slippage<.1):
        raise ValueError("Not enough candles or invalid costs")
    cash=initial; qty=0.; peak=initial; dd=0.; trades=0
    stop=None; trail_high=0.; curve=[]
    for i in range(start,len(candles)):
        historical=candles[:i]
        current=candles[i]
        prev=historical[-1]
        past_closes=[x["close"] for x in historical[-strategy.trend:]]
        avg=sum(past_closes)/len(past_closes)
        prior_high=max(x["high"] for x in historical[-strategy.breakout-1:-1])
        # ATR computed exclusively from previously completed bars
        atr_changes=[]
        for j in range(max(1,i-14),i):
            bar=candles[j]; earlier=candles[j-1]["close"]
            atr_changes.append(max(bar["high"]-bar["low"],abs(bar["high"]-earlier),abs(bar["low"]-earlier)))
        atr=sum(atr_changes)/len(atr_changes)
        enter=prev["close"]>avg and prev["close"]>prior_high
        exit_trend=prev["close"]<avg
        # Protective stop is assessed on previous complete candle;
        # next-bar open fills avoid pretending intrabar execution certainty.
        exit_stop=bool(qty and stop is not None and prev["close"]<stop)
        px=current["open"]
        if qty and (exit_stop or exit_trend):
            cash+=qty*px*(1-fee)*(1-slippage)
            qty=0.;stop=None;trail_high=0.;trades+=1
        if not qty and enter:
            allocation=cash*strategy.risk_fraction
            qty=allocation*(1-fee)/(px*(1+slippage))
            cash-=allocation
            trail_high=prev["close"]
            stop=prev["close"]-strategy.stop_atr*atr
            trades+=1
        if qty:
            trail_high=max(trail_high,prev["close"])
            stop=max(stop,trail_high-strategy.stop_atr*atr)
        equity=cash+qty*current["close"]
        peak=max(peak,equity)
        dd=min(dd,equity/peak-1)
        curve.append(equity)
    final=cash+qty*candles[-1]["close"]*(1-fee)*(1-slippage)
    return {"strategy":strategy.name,"return_pct":100*(final/initial-1),
            "max_drawdown_pct":100*dd,"trades":trades,
            "equity":final,"curve":curve,"start_index":start}

def select_and_test(candles: list[dict], *, split=.7, initial=1000.,
                    fee=.001, slippage=.0005) -> dict:
    if len(candles)<500 or not .6<=split<=.8:
        raise ValueError("Need >=500 rows and .6<=split<=.8")
    cut=int(len(candles)*split)
    results=[]
    for config in CANDIDATES:
        train=run(candles[:cut],config,initial=initial,fee=fee,slippage=slippage)
        results.append({"name":config.name,"train_return_pct":train["return_pct"],
                        "train_drawdown_pct":train["max_drawdown_pct"],
                        "score":train["return_pct"] + train["max_drawdown_pct"]})
    best=max(results,key=lambda d:d["score"])
    chosen=next(s for s in CANDIDATES if s.name==best["name"])
    # Keep prior bars as indicator warmup, but reset capital at holdout boundary.
    test=run(candles,chosen,initial=initial,fee=fee,slippage=slippage,begin_at=cut)
    test.pop("curve")
    return {"training_size":cut,"test_size":len(candles)-cut,
            "train_candidates":results,"chosen":chosen.name,"holdout":test,
            "disclaimer":"Exploratory, not proof of future profitability"}
