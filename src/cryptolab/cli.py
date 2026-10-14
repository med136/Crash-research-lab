"""Command line: download public candles and run paper backtest."""
import argparse
import json
from dataclasses import asdict
from .market import download,save,load
from .engine import backtest

def main():
    ap=argparse.ArgumentParser()
    sub=ap.add_subparsers(dest="mode",required=True)
    d=sub.add_parser("download")
    d.add_argument("--symbol",choices=["BTCUSDT","ETHUSDT"],default="BTCUSDT")
    d.add_argument("--interval",choices=["1h","4h","1d"],default="1h")
    d.add_argument("--output",default="data/btc_1h.csv")
    b=sub.add_parser("backtest")
    b.add_argument("--input",required=True)
    b.add_argument("--fast",type=int,default=10)
    b.add_argument("--slow",type=int,default=30)
    b.add_argument("--capital",type=float,default=1000)
    args=ap.parse_args()
    if args.mode=="download":
        candles=download(args.symbol,args.interval)
        save(candles,args.output)
        print(f"Saved {len(candles)} completed candles to {args.output}")
    else:
        res=asdict(backtest(load(args.input),initial=args.capital,fast=args.fast,slow=args.slow))
        res.pop("curve")
        print(json.dumps(res,indent=2))

if __name__=="__main__":
    main()
