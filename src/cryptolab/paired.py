"""Paired 180-day window comparisons on identical bars and execution assumptions.

Each fold starts with a new hypothetical wallet. Reports descriptive performance;
it does not claim statistical independence from prior model selection.
"""
from __future__ import annotations
from .market import validate
from .voltrend import run as volatility_trend
from .exposure import constant_weight
from .benchmarks import buy_and_hold

def paired_windows(candles, *, first=900, days=180, fee=.001,
                   slippage=.0005, target=.60):
    validate(candles)
    if first<450 or days<90 or len(candles)<first+days or not 0<target<=1:
        raise ValueError("Insufficient bars or invalid window")
    out=[]
    for start in range(first,len(candles)-days+1,days):
        end=start+days
        history=candles[:end]
        v=volatility_trend(history,start_at=start,vol_target=target,
                           fee=fee,slippage=slippage)
        passive=buy_and_hold(candles,start,end,fee=fee,slippage=slippage)
        allocations={
            str(weight):constant_weight(candles,start,end,weight=weight,
                                        fee=fee,slippage=slippage)
            for weight in (.25,.5,.75)
        }
        out.append({
            "start_index":start,"end_index":end-1,
            "voltrend":{"return_pct":v["return_pct"],
                        "max_drawdown_pct":v["max_drawdown_pct"],"trades":v["trades"]},
            "passive":{"return_pct":passive["return_pct"],
                       "max_drawdown_pct":passive["max_drawdown_pct"],"trades":passive["trades"]},
            "fixed":{name:{"return_pct":r["return_pct"],
                            "max_drawdown_pct":r["max_drawdown_pct"],"trades":r["trades"]}
                     for name,r in allocations.items()}
        })
    def summarize(selector):
        results=[selector(fold) for fold in out]
        return {
            "mean_return_pct":sum(r["return_pct"] for r in results)/len(results),
            "mean_max_drawdown_pct":sum(r["max_drawdown_pct"] for r in results)/len(results),
            "positive_windows":sum(r["return_pct"]>0 for r in results),
            "worst_return_pct":min(r["return_pct"] for r in results)
        }
    summary={"voltrend":summarize(lambda f:f["voltrend"]),
             "passive":summarize(lambda f:f["passive"])}
    for weight in ("0.25","0.5","0.75"):
        summary["fixed_"+weight]=summarize(lambda f,w=weight:f["fixed"][w])
    return {"fold_count":len(out),"folds":out,"summary":summary,
            "limitations":"Exploratory repeated-window evaluation, not an untouched holdout."}
