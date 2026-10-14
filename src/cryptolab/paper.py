"""Stateful forward-only paper trading on COMPLETED candles.

Execute pending target only when a new completed candle becomes available,
using its close (not its earlier open). This is hypothetical and sends no orders.
"""
from __future__ import annotations
import json
import math
from pathlib import Path
from .engine import signal

def new_state(history: list[dict], *, initial: float = 1000.0, fast: int = 10,
              slow: int = 30, fee: float = 0.001, slippage: float = 0.0005) -> dict:
    if len(history) < slow or not 1 < fast < slow or initial <= 0:
        raise ValueError("Insufficient starting history or invalid parameters")
    if not (0 <= fee < .1 and 0 <= slippage < .1):
        raise ValueError("Invalid execution costs")
    return {"version":1, "cash":float(initial), "asset":0.,
            "last_time":history[-1]["time"],"last_close":history[-1]["close"],
            "pending_target":signal([x["close"] for x in history],fast,slow),
            "closes":[x["close"] for x in history[-slow:]],
            "fast":fast,"slow":slow,"fee":fee,"slippage":slippage,
            "initial":float(initial),"trades":[],"equity":[float(initial)]}

def step(state: dict, candle: dict) -> dict:
    t = candle["time"]
    if t < state["last_time"]:
        raise ValueError("Out-of-order candle: refuse backfill in live state")
    if t == state["last_time"]:
        return state
    price=float(candle["close"])
    if not math.isfinite(price) or price <= 0:
        raise ValueError("Invalid close price")
    cash,asset=state["cash"],state["asset"]
    if state["pending_target"] and asset == 0:
        asset=cash*(1-state["fee"])/(price*(1+state["slippage"]))
        cash=0.
        state["trades"].append({"time":t,"side":"BUY","price":price})
    elif not state["pending_target"] and asset>0:
        cash=asset*price*(1-state["fee"])*(1-state["slippage"])
        asset=0.
        state["trades"].append({"time":t,"side":"SELL","price":price})
    state["cash"],state["asset"]=cash,asset
    closes=(state["closes"]+[price])[-state["slow"]:]
    state["closes"]=closes
    state["pending_target"]=signal(closes,state["fast"],state["slow"])
    state["last_time"],state["last_close"]=t,price
    state["equity"].append(cash+asset*price)
    return state

def apply_new_candles(state: dict, candles: list[dict]) -> dict:
    for candle in sorted(candles,key=lambda x:x["time"]):
        step(state,candle)
    return state

def save_state(state:dict,filename:str)->None:
    path=Path(filename)
    path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_suffix(path.suffix+".tmp")
    temp.write_text(json.dumps(state,indent=2),encoding="utf-8")
    temp.replace(path)

def load_state(filename:str)->dict:
    state=json.loads(Path(filename).read_text(encoding="utf-8"))
    if state.get("version") != 1:
        raise ValueError("Unsupported paper state version")
    return state

def summary(state:dict)->dict:
    net=state["cash"]+state["asset"]*state["last_close"]
    return {"initial":state["initial"],"equity":round(net,4),
            "pnl_pct":round(100*(net/state["initial"]-1),4),
            "trades":len(state["trades"]),"last_candle":state["last_time"],
            "next_target":"LONG" if state["pending_target"] else "CASH"}
