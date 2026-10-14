"""Download public completed OHLCV candles; no credentials or trading API."""
import csv
import json
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://data-api.binance.vision/api/v3/klines"
INTERVAL_MS = {"1h": 3600_000, "4h": 4*3600_000, "1d": 24*3600_000}

def download(symbol="BTCUSDT", interval="1h", n=1000):
    if symbol not in {"BTCUSDT","ETHUSDT"} or interval not in INTERVAL_MS or not 60 <= n <= 1000:
        raise ValueError("Unsupported parameters")
    query = urllib.parse.urlencode({"symbol":symbol,"interval":interval,"limit":n})
    req = urllib.request.Request(API+"?"+query,headers={"User-Agent":"CryptoResearchPaperOnly/0.1"})
    with urllib.request.urlopen(req,timeout=25) as r:
        raw = json.load(r)
    if not isinstance(raw,list):
        raise ValueError("Unexpected market response")
    import time
    current_ms=int(time.time()*1000)
    candles=[]
    for a in raw:
        if len(a)<7 or int(a[6])>=current_ms:
            continue
        c={"time":int(a[0]),"open":float(a[1]),"high":float(a[2]),
           "low":float(a[3]),"close":float(a[4]),"volume":float(a[5])}
        if c["low"]<=0 or not c["low"]<=c["open"]<=c["high"] or not c["low"]<=c["close"]<=c["high"]:
            raise ValueError("Malformed OHLC candle")
        candles.append(c)
    validate(candles)
    return candles

def validate(candles):
    if len(candles)<60:
        raise ValueError("Need >=60 completed candles")
    if any(candles[i]["time"]>=candles[i+1]["time"] for i in range(len(candles)-1)):
        raise ValueError("Unsorted or duplicate candles")

def save(candles,path):
    target=Path(path);target.parent.mkdir(parents=True,exist_ok=True)
    with target.open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=["time","open","high","low","close","volume"])
        writer.writeheader();writer.writerows(candles)

def load(path):
    with open(path,newline="") as f:
        rows=list(csv.DictReader(f))
    candles=[{k:int(r[k]) if k=="time" else float(r[k])
              for k in ("time","open","high","low","close","volume")} for r in rows]
    validate(candles)
    return candles
