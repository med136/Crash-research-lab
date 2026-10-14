"""Causal $100 spot portfolio backtesting across 30/90/180/365-day windows.

Exploratory historical simulations; does not predict profits, submit orders,
borrow, use leverage, or connect accounts. Each asset and fold resets to $100.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
from statistics import mean, median

STRATEGIES=("cash","buy_hold","sma20_60","sma50_200",
            "breakout55_20","volatility_trend","defensive_ensemble")
HORIZONS={"1_month_30d":30,"3_months_90d":90,
          "6_months_180d":180,"1_year_365d":365}
COSTS={"base":(.001,.0005),"double_cost":(.002,.001),
       "adverse_slippage":(.001,.003)}
CAPITAL=100.
WARMUP=201

def _ensure_history(bars):
    from .market import validate
    validate(bars)
    if len(bars)<WARMUP+365:raise ValueError("Too few candles for a 365-day test")
    if any(b["time"]-a["time"]!=86_400_000 for a,b in zip(bars,bars[1:])):
        raise ValueError("Gap or duplicate in daily history")

def signal_targets(bars):
    """At bar i open, decisions use closes <= i-1 only."""
    _ensure_history(bars)
    c=[float(b["close"]) for b in bars]
    result={name:[0.]*len(c) for name in STRATEGIES}
    breakout=False
    for i in range(WARMUP,len(c)):
        last=c[i-1]
        ma20=mean(c[i-20:i]);ma50=mean(c[i-50:i])
        ma60=mean(c[i-60:i]);ma200=mean(c[i-200:i])
        momentum=last/c[i-31]-1
        recent=[math.log(c[j]/c[j-1]) for j in range(i-30,i)]
        avg=mean(recent)
        volatility=math.sqrt(365*mean((x-avg)**2 for x in recent))
        if last>max(c[i-56:i-1]):breakout=True
        elif last<min(c[i-21:i-1]):breakout=False
        result["buy_hold"][i]=1.
        result["sma20_60"][i]=float(last>ma60 and ma20>ma60)
        result["sma50_200"][i]=float(last>ma200 and ma50>ma200)
        result["breakout55_20"][i]=float(breakout)
        result["volatility_trend"][i]=min(.75,.45/max(volatility,.05)) if last>ma200 and momentum>0 else 0.
        result["defensive_ensemble"][i]=min(.65,.30/max(volatility,.10)) if (
            last>ma200 and ma20>ma60 and momentum>0 and volatility<=.85) else 0.
    return result

def simulate(bars,targets,start,end,*,fee=.001,slippage=.0005,initial=CAPITAL,min_trade_usd=5.):
    """One-asset spot cash ledger; next-open fill; terminal close liquidation.

    A $5 transaction floor is assumed, not verified against per-pair exchange
    rules; modelled slippage excludes true order book depth and impact.
    """
    if not 0<=start<end<=len(bars) or start<WARMUP or len(targets)<end:
        raise ValueError("Invalid chronological window")
    if not math.isfinite(initial) or initial<=0 or not 0<=fee<.1 or not 0<=slippage<.1:
        raise ValueError("Invalid initial balance/transaction costs")
    if not math.isfinite(min_trade_usd) or min_trade_usd<0:raise ValueError("Invalid trade floor")
    cash=initial;units=0.;peak=initial;max_dd=0.;entries=0;exits=0;rebalance=0
    for i in range(start,end):
        op=float(bars[i]["open"]);cl=float(bars[i]["close"]);weight=float(targets[i])
        if not all(map(math.isfinite,(op,cl,weight))) or min(op,cl)<=0 or not 0<=weight<=1:
            raise ValueError("Invalid price or exposure")
        eq=cash+units*op
        delta=eq*weight/op-units
        value=abs(delta*op)
        if value>=min_trade_usd and value>eq*.001:
            if delta>0:
                spent=min(cash,value*(1+fee+slippage))
                added=spent/(op*(1+fee+slippage))
                if added*op>=min_trade_usd:
                    cash-=spent;units+=added;entries+=1;rebalance+=1
            else:
                sold=min(units,-delta)
                if sold*op>=min_trade_usd:
                    cash+=sold*op*(1-fee-slippage);units-=sold;exits+=1;rebalance+=1
        eq_close=cash+units*cl
        peak=max(peak,eq_close)
        max_dd=min(max_dd,eq_close/peak-1)
    if units:
        cash+=units*float(bars[end-1]["close"])*(1-fee-slippage)
        exits+=1
    max_dd=min(max_dd,cash/peak-1)
    if cash<0 or not math.isfinite(cash):raise ValueError("Invalid terminal balance")
    return {"final_usd":round(cash,6),"return_pct":100*(cash/initial-1),
            "max_drawdown_pct":max_dd*100,"entries":entries,"exits":exits,
            "rebalances":rebalance}

def windows(bars,signals,days,fee,slippage):
    if days not in HORIZONS.values():raise ValueError("Unsupported horizon")
    out=[]
    for start in range(WARMUP,len(bars)-days+1,days):
        end=start+days
        models={name:simulate(bars,signal,start,end,fee=fee,slippage=slippage)
                for name,signal in signals.items()}
        out.append({"start_index":start,"end_index":end-1,
                    "start_utc":bars[start]["time"],"end_utc":bars[end-1]["time"],
                    "models":models})
    return out

def aggregate(folds):
    if not folds:raise ValueError("No historical test folds")
    out={}
    for name in STRATEGIES:
        runs=[f["models"][name] for f in folds]
        finals=[r["final_usd"] for r in runs]
        excess=[r["return_pct"]-f["models"]["buy_hold"]["return_pct"] for r,f in zip(runs,folds)]
        sorted_final=sorted(finals)
        out[name]={
            "folds":len(folds),"mean_final_usd":round(mean(finals),2),
            "median_final_usd":round(median(finals),2),
            "worst_final_usd":round(min(finals),2),
            "best_final_usd":round(max(finals),2),
            "p10_final_usd":round(sorted_final[int((len(finals)-1)*.1)],2),
            "p90_final_usd":round(sorted_final[int((len(finals)-1)*.9)],2),
            "positive_windows":sum(x["return_pct"]>0 for x in runs),
            "beats_hold_windows":sum(x>0 for x in excess),
            "mean_excess_vs_hold_pp":round(mean(excess),3),
            "median_excess_vs_hold_pp":round(median(excess),3),
            "mean_max_drawdown_pct":round(mean(x["max_drawdown_pct"] for x in runs),3),
            "worst_max_drawdown_pct":round(min(x["max_drawdown_pct"] for x in runs),3),
            "mean_rebalances":round(mean(x["rebalances"] for x in runs),2),
        }
    return out

def analyze_market(bars):
    signals=signal_targets(bars)
    output={"initial_usd":CAPITAL,"horizons_approximately_days":HORIZONS,"scenarios":{},
            "nonoverlapping_folds_within_each_horizon":True,"future_forecast":False}
    for label,(fee,slip) in COSTS.items():
        output["scenarios"][label]={}
        for h,days in HORIZONS.items():
            folds=windows(bars,signals,days,fee,slip)
            output["scenarios"][label][h]={
                "window_count":len(folds),"models":aggregate(folds),
                "fold_results":folds if label=="base" else []}
    return output

def multi_asset_study(*,symbols,end,bars=1000,fetch=None):
    from .universe import UNIVERSE,fetch_daily
    if not symbols or len(set(symbols))!=len(symbols) or any(s not in UNIVERSE for s in symbols):
        raise ValueError("Invalid selection of research markets")
    result={"study":"CRYPTO_LAB_100_USD_EXPLORATORY_V1","capital_usd":CAPITAL,
            "historical_cutoff_utc":end,"bars_requested":bars,
            "assets_requested":list(symbols),"strategies":list(STRATEGIES),
            "horizons":HORIZONS,
            "cost_scenarios":{k:{"fee_fraction_per_fill":f,"slippage_fraction_per_fill":sl}
                              for k,(f,sl) in COSTS.items()},
            "assets":{},"errors":{},"deployment_gate":"NO_REAL_ORDERS",
            "limitations":[
                "These are past outcomes, NOT predictions of a future $100 wallet.",
                "Each coin is separately tested using $100, not a funded 15-coin portfolio.",
                "Only about 2 independent annual windows per asset; weak long-term evidence.",
                "Current-listed crypto universe has survivorship bias and correlated assets.",
                "Models were brainstormed using overlapping crypto history; not an untouched test.",
                "Fees, slippage, and $5 minimum trade are assumptions; live spreads may be wider.",
                "Months correspond to approximate 30/90/180/365 day intervals.",
                "Selecting the apparent highest performing combination would be data snooping.",
            ]}
    for symbol in symbols:
        try:
            opts={"end":end,"bars":bars}
            if fetch is not None:opts["fetch"]=fetch
            bars_data,provenance=fetch_daily(symbol,**opts)
            result["assets"][symbol]={"source":provenance,
                                       "analysis":analyze_market(bars_data)}
        except (ValueError,KeyError,OSError,TimeoutError) as exc:
            result["errors"][symbol]=str(exc)
    result["successful_assets"]=len(result["assets"])
    result["failed_assets"]=len(result["errors"])
    return result

def main():
    from .universe import UNIVERSE
    parser=argparse.ArgumentParser(description="User-owned $100 historical paper research")
    parser.add_argument("--symbols",default=",".join(UNIVERSE))
    parser.add_argument("--end",default="2026-09-30")
    parser.add_argument("--bars",type=int,default=1000)
    parser.add_argument("--min-success",type=int,default=12)
    parser.add_argument("--output",required=True)
    parser.add_argument("--panel",required=False,help="Static FR/EN historical research dashboard")
    a=parser.parse_args()
    out=multi_asset_study(symbols=tuple(a.symbols.split(",")),end=a.end,bars=a.bars)
    file=Path(a.output);file.parent.mkdir(parents=True,exist_ok=True)
    file.write_text(json.dumps(out,indent=2,allow_nan=False),encoding="utf-8")
    if a.panel:
        from .capital100_panel import render_capital_panel
        panel=Path(a.panel)
        panel.parent.mkdir(parents=True,exist_ok=True)
        panel.write_text(render_capital_panel(out),encoding="utf-8")
    print(json.dumps({"output":str(file),"successful_assets":out["successful_assets"],
                      "failed_assets":out["failed_assets"],"deployment_gate":"NO_REAL_ORDERS"}))
    if out["successful_assets"]<a.min_success:raise SystemExit("Too few verified assets")

if __name__=="__main__":main()
