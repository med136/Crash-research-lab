"""Stress-testing and auditable go/no-go criteria for research strategies.

A return above zero is not sufficient evidence for a deployable trading edge.
"""
from __future__ import annotations
import math
from .vol_research import select_vol_target
from .voltrend import run
from .market import validate

def stress_test(candles: list[dict], *, split: float = .70) -> dict:
    validate(candles)
    if len(candles) < 500:
        raise ValueError("At least 500 historical bars required")
    selected=select_vol_target(candles,split=split)
    target=selected["chosen_volatility_target"]
    cut=int(len(candles)*split)
    scenarios=[]
    for label,fee,slippage in [
        ("base",.001,.0005),("double_costs",.002,.001),
        ("high_slippage",.001,.003),("zero_cost",0.,0.)
    ]:
        result=run(candles,vol_target=target,start_at=cut,fee=fee,slippage=slippage)
        scenarios.append({"name":label,"fee":fee,"slippage":slippage,
                          "return_pct":round(result["return_pct"],4),
                          "max_drawdown_pct":round(result["max_drawdown_pct"],4),
                          "trades":result["trades"]})
    benchmark=100*((1-.001)/(candles[cut]["open"]*(1+.0005))*
                   candles[-1]["close"]*(1-.001)*(1-.0005)-1)
    base=scenarios[0]
    return {
        "selected_target":target,"train_size":cut,"test_size":len(candles)-cut,
        "buy_hold_return_pct":round(benchmark,4),
        "scenarios":scenarios,
        "checks":{
            "beats_passive_base":base["return_pct"]>benchmark,
            "positive_double_costs":scenarios[1]["return_pct"]>0,
            "drawdown_below_25pct":base["max_drawdown_pct"]>=-25,
            "minimum_holdout_bars":len(candles)-cut>=365
        },
        "verdict":"RESEARCH_ONLY",
        "reason":"Stress performance and one historical holdout never establish sustainable future profits."
    }
