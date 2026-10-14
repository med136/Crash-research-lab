"""Public market data research and paper-only trading; never places orders."""
import argparse
import json
from dataclasses import asdict
from pathlib import Path
from .market import download,save,load,INTERVAL_MS
from .engine import backtest
from .research import evaluate
from .strategies import select_and_test
from .walk_forward import walk_forward
from .stress import stress_test
from .paired import paired_windows
from .audit_stats import cost_scenarios
from .paper import new_state,apply_new_candles,save_state,load_state,summary
from .volpaper import once as volatility_paper_once

def main():
    ap=argparse.ArgumentParser()
    sub=ap.add_subparsers(dest="mode",required=True)
    d=sub.add_parser("download")
    d.add_argument("--symbol",choices=["BTCUSDT","ETHUSDT"],default="BTCUSDT")
    d.add_argument("--interval",choices=list(INTERVAL_MS),default="1h")
    d.add_argument("--output",default="data/btc_1h.csv")
    b=sub.add_parser("backtest")
    b.add_argument("--input",required=True)
    b.add_argument("--fast",type=int,default=10)
    b.add_argument("--slow",type=int,default=30)
    b.add_argument("--capital",type=float,default=1000)
    au=sub.add_parser("audit")
    au.add_argument("--input",required=True)
    au.add_argument("--first",type=int,default=900)
    au.add_argument("--days",type=int,default=180)
    pw=sub.add_parser("paired")
    pw.add_argument("--input",required=True)
    pw.add_argument("--first",type=int,default=900)
    pw.add_argument("--days",type=int,default=180)
    st=sub.add_parser("stress")
    st.add_argument("--input",required=True)
    wf=sub.add_parser("walk-forward")
    wf.add_argument("--input",required=True)
    wf.add_argument("--initial-train",type=int,default=900)
    wf.add_argument("--test-size",type=int,default=180)
    wf.add_argument("--step",type=int,default=180)
    x=sub.add_parser("research")
    x.add_argument("--input",required=True)
    x.add_argument("--capital",type=float,default=1000)
    e=sub.add_parser("evaluate")
    e.add_argument("--input",required=True)
    e.add_argument("--capital",type=float,default=1000)
    vp=sub.add_parser("paper-vol")
    vp.add_argument("--symbol",choices=["BTCUSDT","ETHUSDT"],required=True)
    vp.add_argument("--state",required=True)
    vp.add_argument("--capital",type=float,default=1000.)
    vp.add_argument("--input",default=None,help="offline CSV replay only")
    p=sub.add_parser("paper")
    p.add_argument("--symbol",choices=["BTCUSDT","ETHUSDT"],default="BTCUSDT")
    p.add_argument("--interval",choices=list(INTERVAL_MS),default="1h")
    p.add_argument("--state",default="data/paper_state.json")
    p.add_argument("--capital",type=float,default=1000)
    p.add_argument("--fast",type=int,default=10)
    p.add_argument("--slow",type=int,default=30)
    args=ap.parse_args()
    if args.mode=="download":
        candles=download(args.symbol,args.interval)
        save(candles,args.output)
        print(f"Saved {len(candles)} completed candles to {args.output}")
    elif args.mode=="backtest":
        result=asdict(backtest(load(args.input),initial=args.capital,fast=args.fast,slow=args.slow))
        result.pop("curve")
        print(json.dumps(result,indent=2))
    elif args.mode=="audit":
        print(json.dumps(cost_scenarios(load(args.input),first=args.first,days=args.days),indent=2))
    elif args.mode=="paired":
        print(json.dumps(paired_windows(load(args.input),first=args.first,days=args.days),indent=2))
    elif args.mode=="stress":
        print(json.dumps(stress_test(load(args.input)),indent=2))
    elif args.mode=="walk-forward":
        print(json.dumps(walk_forward(load(args.input),initial_train=args.initial_train,test_size=args.test_size,step=args.step),indent=2))
    elif args.mode=="research":
        print(json.dumps(select_and_test(load(args.input),initial=args.capital),indent=2))
    elif args.mode=="evaluate":
        print(json.dumps(evaluate(load(args.input),capital=args.capital),indent=2))
    elif args.mode=="paper-vol":
        print(json.dumps(volatility_paper_once(symbol=args.symbol,path=args.state,capital=args.capital,input_csv=args.input),indent=2))
    else:
        statepath=Path(args.state)
        candles=download(args.symbol,args.interval)
        if statepath.exists():
            state=load_state(str(statepath))
            if state["symbol"]!=args.symbol or state["interval"]!=args.interval:
                raise ValueError("State symbol/interval mismatch")
            newer=[c for c in candles if c["time"]>state["last_time"]]
            if newer and newer[0]["time"]-state["last_time"]!=INTERVAL_MS[args.interval]:
                raise ValueError("Missing candles: refuse skipping a market gap")
            for older,current in zip(newer,newer[1:]):
                if current["time"]-older["time"]!=INTERVAL_MS[args.interval]:
                    raise ValueError("Gap in market data")
            apply_new_candles(state,newer)
        else:
            state=new_state(candles,initial=args.capital,fast=args.fast,slow=args.slow)
            state["symbol"],state["interval"]=args.symbol,args.interval
        save_state(state,str(statepath))
        print(json.dumps(summary(state),indent=2))
        print("Paper only. Re-run after a candle closes. No orders are submitted.")

if __name__=="__main__":
    main()
