"""Expanding-window walk-forward evaluation for volatility-managed trend.

Each fold calibrates target only using prior data; the following period is held out.
Every fold resets the hypothetical paper wallet to 1000, not a chained live result.
"""
from __future__ import annotations
from .voltrend import run
from .market import validate
from .vol_research import TARGETS

def walk_forward(candles:list[dict], *, initial_train=900, test_size=180,
                 step=180, fee=.001, slippage=.0005) -> dict:
    validate(candles)
    if initial_train<450 or test_size<60 or step<1:
        raise ValueError("Insufficient walk-forward windows")
    folds=[]
    for cut in range(initial_train,len(candles)-test_size+1,step):
        train=candles[:cut]
        ranked=[]
        for target in TARGETS:
            r=run(train,vol_target=target,fee=fee,slippage=slippage)
            ranked.append((r["return_pct"]+r["max_drawdown_pct"],target))
        selected=max(ranked)[1]
        # Restrict the test to its future window but retain pre-test history for indicators.
        holdout=candles[:cut+test_size]
        # Returns from run(start_at=cut) must mark-to-market only the out-of-sample trades.
        result=run(holdout,vol_target=selected,initial=1000.,
                   fee=fee,slippage=slippage,start_at=cut)
        entry=holdout[cut]["open"]
        end=holdout[-1]["close"]
        passive=100*((1-fee)/(entry*(1+slippage))*end*(1-fee)*(1-slippage)-1)
        folds.append({"train_end_index":cut-1,"test_start_index":cut,
                      "test_end_index":cut+test_size-1,
                      "vol_target":selected,
                      "strategy_return_pct":result["return_pct"],
                      "buy_hold_return_pct":passive,
                      "strategy_max_drawdown_pct":result["max_drawdown_pct"],
                      "strategy_trades":result["trades"]})
    if not folds:
        raise ValueError("Not enough data for any complete fold")
    return {
        "folds":folds,"fold_count":len(folds),
        "beats_buy_hold":sum(f["strategy_return_pct"]>f["buy_hold_return_pct"] for f in folds),
        "mean_excess_return_pp":sum(f["strategy_return_pct"]-f["buy_hold_return_pct"] for f in folds)/len(folds),
        "caveat":"Exploratory; overlapping tests or repeated research decisions can bias inference."
    }
