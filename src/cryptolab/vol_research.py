"""Choose volatility target exclusively on training data; test untouched future bars."""
from .voltrend import run
from .market import validate

TARGETS=(.20,.30,.40,.60)

def select_vol_target(candles,split=.70,initial=1000.0,fee=.001,slippage=.0005):
    validate(candles)
    if len(candles)<500 or not .6<=split<=.8:
        raise ValueError("Insufficient data")
    cut=int(len(candles)*split)
    training=[]
    for target in TARGETS:
        r=run(candles[:cut],vol_target=target,initial=initial,fee=fee,slippage=slippage)
        training.append({"target":target,"return_pct":r["return_pct"],
                         "max_drawdown_pct":r["max_drawdown_pct"],"trades":r["trades"]})
    best=max(training,key=lambda x:x["return_pct"]+x["max_drawdown_pct"])
    held=run(candles,vol_target=best["target"],initial=initial,fee=fee,
             slippage=slippage,start_at=cut)
    return {"training":training,"chosen_volatility_target":best["target"],
            "test_rows":len(candles)-cut,
            "holdout":{"return_pct":held["return_pct"],
                       "max_drawdown_pct":held["max_drawdown_pct"],"trades":held["trades"]},
            "note":"Exploratory; validate on different venues and later prospective periods."}
