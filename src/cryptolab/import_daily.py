"""Import a public third-party daily BTC OHLC CSV with auditable date validation."""
from __future__ import annotations
import csv
from datetime import date, datetime, timezone, timedelta
from pathlib import Path
from .market import validate, save

def import_daily(source: str | Path, output: str | Path) -> dict:
    candles = []
    with open(source, newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if not header or len(header) != 6:
            raise ValueError("Expected six daily OHLCV columns")
        for row in reader:
            if not row or not any(row):
                continue
            if len(row) != 6:
                raise ValueError("Expected six columns per row")
            day = date.fromisoformat(row[0])
            if day >= datetime.now(timezone.utc).date():
                raise ValueError("Refusing today's unfinished daily candle")
            o,h,l,c,v = map(float,row[1:])
            if not all(__import__("math").isfinite(x) for x in (o,h,l,c,v)):
                raise ValueError("Non-finite OHLCV")
            if l<=0 or v<0 or h<l or not(l<=o<=h and l<=c<=h):
                raise ValueError("Invalid OHLCV envelope")
            candles.append({"time":int(datetime(day.year,day.month,day.day,tzinfo=timezone.utc).timestamp()*1000),
                            "open":o,"high":h,"low":l,"close":c,"volume":v})
    validate(candles)
    for a,b in zip(candles,candles[1:]):
        if b["time"]-a["time"] != 86400000:
            raise ValueError("Missing or duplicate daily bar")
    save(candles,output)
    return {"rows":len(candles),"start":date.fromtimestamp(candles[0]["time"]/1000).isoformat(),
            "end":date.fromtimestamp(candles[-1]["time"]/1000).isoformat(),
            "output":str(output)}
