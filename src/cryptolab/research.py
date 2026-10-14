"""Chronological strategy research, net of trading costs.

Selection only on calibration split, final evaluation on later untouched data.
"""
from __future__ import annotations
from dataclasses import asdict
from .engine import backtest
from .market import validate

CANDIDATES = ((5, 20), (10, 30), (20, 60), (30, 90))

def evaluate(candles: list[dict], *, split: float = .65, capital: float = 1000,
             fee: float = .001, slippage: float = .0005) -> dict:
    validate(candles)
    if len(candles) < 300 or not .5 <= split <= .8:
        raise ValueError("Need >=300 candles and split between .5 and .8")
    cut = int(len(candles) * split)
    training = candles[:cut]
    scores = []
    for fast, slow in CANDIDATES:
        result = backtest(training,initial=capital,fee=fee,slippage=slippage,fast=fast,slow=slow)
        scores.append({"fast":fast,"slow":slow,"train_return_pct":result.return_pct,
                       "train_drawdown_pct":result.max_drawdown_pct,"train_trades":result.trades})
    selected=max(scores,key=lambda x:(x["train_return_pct"]+.5*x["train_drawdown_pct"],-x["slow"]))
    fast,slow=selected["fast"],selected["slow"]
    holdout=candles[cut-slow:]
    result=backtest(holdout,initial=capital,fee=fee,slippage=slippage,fast=fast,slow=slow)
    return {"total_candles":len(candles),"calibration_candles":cut,
            "holdout_candles":len(candles)-cut,
            "selected":{"fast":fast,"slow":slow},"training_candidates":scores,
            "holdout":{k:v for k,v in asdict(result).items() if k!="curve"},
            "caveat":"One holdout is not evidence of profitable forward performance."}
