"""Verified public Binance SPOT 1d monthly archive importer (research only).

Downloads companion .CHECKSUMs before importing. Checks timestamps in ms (pre-2025)
and microseconds (2025+). No private API keys or order endpoints.
"""
from __future__ import annotations

import argparse
import calendar
import csv
import hashlib
import io
import json
import math
import re
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from .market import save, validate

BASE = "https://data.binance.vision/data/spot/monthly/klines"
PAIRS = frozenset({"BTCUSDT", "ETHUSDT"})
DAY_MS = 86_400_000


def _month_index(month: str) -> int:
    if not re.fullmatch(r"20\d\d-(0[1-9]|1[0-2])", month):
        raise ValueError("Month must be YYYY-MM, from 2000 onward")
    y, m = map(int, month.split("-"))
    return y * 12 + m - 1


def month_names(start: str, end: str) -> list[str]:
    a, b = _month_index(start), _month_index(end)
    now = datetime.now(timezone.utc)
    latest_closed = now.year * 12 + now.month - 2
    if a > b or b > latest_closed or b - a > 59:
        raise ValueError("Select up to 60 fully elapsed monthly archives")
    return [f"{i // 12:04d}-{i % 12 + 1:02d}" for i in range(a, b + 1)]


def parse_archive(payload: bytes, *, symbol: str, month: str) -> list[dict]:
    if symbol not in PAIRS:
        raise ValueError("Unsupported symbol")
    _month_index(month)
    expected_name = f"{symbol}-1d-{month}.csv"
    y, m = map(int, month.split("-"))
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        if archive.namelist() != [expected_name]:
            raise ValueError("Unexpected archive members")
        info = archive.getinfo(expected_name)
        if info.file_size > 5_000_000:
            raise ValueError("Archive decompressed size too large")
        with archive.open(expected_name) as source:
            rows = list(csv.reader(io.TextIOWrapper(source, encoding="utf-8-sig")))
    expected_days = calendar.monthrange(y, m)[1]
    if len(rows) != expected_days:
        raise ValueError(f"Incomplete month: {len(rows)} rows, expected {expected_days}")
    result = []
    for day, row in enumerate(rows, start=1):
        if len(row) != 12:
            raise ValueError("Binance SPOT kline rows require twelve columns")
        raw_open = int(row[0])
        micro = raw_open >= 10**14
        if micro != (y >= 2025):
            raise ValueError("Unexpected millisecond/microsecond precision")
        open_ms = raw_open // 1000 if micro else raw_open
        if raw_open != open_ms * (1000 if micro else 1):
            raise ValueError("Kline does not start on a millisecond boundary")
        target_ms = int(datetime(y, m, day, tzinfo=timezone.utc).timestamp() * 1000)
        if open_ms != target_ms:
            raise ValueError("Missing, reordered or invalid UTC daily candle")
        close_raw = int(row[6])
        close_expect = raw_open + DAY_MS * (1000 if micro else 1) - 1
        if close_raw != close_expect:
            raise ValueError("Kline close timestamp is inconsistent")
        c = {"time": open_ms, "open": float(row[1]), "high": float(row[2]),
             "low": float(row[3]), "close": float(row[4]), "volume": float(row[5])}
        values = (c["open"], c["high"], c["low"], c["close"], c["volume"])
        if not all(math.isfinite(v) for v in values) or c["low"] <= 0 or c["volume"] < 0 or not (c["low"] <= c["open"] <= c["high"] and c["low"] <= c["close"] <= c["high"]):
            raise ValueError("Invalid OHLCV values in Binance archive")
        result.append(c)
    return result


def _get(url: str, timeout: int = 30) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "CryptoPaperResearch/0.3"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = r.read(8_000_001)
    if len(data) > 8_000_000:
        raise ValueError("Archive response exceeds 8MB safety cap")
    return data


def fetch_archive(symbol: str, month: str, *, fetch=_get) -> tuple[list[dict], dict]:
    if symbol not in PAIRS:
        raise ValueError("Unsupported pair")
    _month_index(month)
    name = f"{symbol}-1d-{month}.zip"
    url = f"{BASE}/{symbol}/1d/{name}"
    checksum = fetch(url + ".CHECKSUM").decode("utf-8-sig").strip()
    match = re.fullmatch(r"([0-9a-fA-F]{64})\s+\*?([^\s]+)", checksum)
    if not match or match[2] != name:
        raise ValueError("Invalid or untrusted companion checksum")
    payload = fetch(url)
    digest = hashlib.sha256(payload).hexdigest()
    if digest.lower() != match[1].lower():
        raise ValueError("ZIP checksum mismatch; refusing to import")
    bars = parse_archive(payload, symbol=symbol, month=month)
    return bars, {"source": url, "checksum_sha256": digest, "bars": len(bars), "month": month}


def download_months(symbol: str, start: str, end: str, output: str, *, fetch=_get) -> dict:
    if symbol not in PAIRS:
        raise ValueError("Unsupported pair")
    months = month_names(start, end)
    all_bars, provenance = [], []
    for month in months:
        bars, manifest = fetch_archive(symbol, month, fetch=fetch)
        all_bars.extend(bars)
        provenance.append(manifest)
    for a, b in zip(all_bars, all_bars[1:]):
        if b["time"] - a["time"] != DAY_MS:
            raise ValueError("Market history has a daily gap")
    if len(all_bars) >= 60:
        validate(all_bars)
    target = Path(output)
    save(all_bars, target)
    result = {"source": "Binance SPOT public monthly archive", "symbol": symbol,
              "interval": "1d", "start": start, "end": end,
              "bars": len(all_bars), "monthly_archives": provenance,
              "note": "Public market research only. Not live fills, not proof of profitable trading."}
    target.with_suffix(target.suffix + ".manifest.json").write_text(
        json.dumps(result, indent=2), encoding="utf-8")
    return result


def main() -> None:
    ap = argparse.ArgumentParser(description="Public verified Binance daily historical candles")
    ap.add_argument("--symbol", choices=sorted(PAIRS), required=True)
    ap.add_argument("--start", required=True, help="YYYY-MM")
    ap.add_argument("--end", required=True, help="YYYY-MM (last completed month)")
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    print(json.dumps(download_months(args.symbol, args.start, args.end, args.output), indent=2))


if __name__ == "__main__":
    main()
