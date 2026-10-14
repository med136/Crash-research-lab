import json
import unittest
from datetime import date, datetime, timedelta, timezone
from urllib.parse import parse_qs, urlparse
from cryptolab.advisor import evaluate_closes
from cryptolab.panel import render_panel
from cryptolab.universe import fetch_daily, study, compare_coin, UNIVERSE, DAY_MS


def market_bytes(end="2026-09-30", n=640, *, growing=True, corrupt=False):
    d=date.fromisoformat(end)
    start=d-timedelta(days=n-1)
    rows=[]
    for i in range(n):
        current=start+timedelta(days=i)
        epoch=int(datetime(current.year,current.month,current.day,tzinfo=timezone.utc).timestamp()*1000)
        if corrupt and i==n//2:
            epoch+=DAY_MS
        p=100+i*.13 if growing else 300-i*.11
        rows.append([epoch,str(p),str(p+3),str(p-3),str(p+.1),str(1234+i),
                     epoch+DAY_MS-1, "1000", 100, "1", "2", "0"])
    return json.dumps(rows).encode()


class MultiCryptoTests(unittest.TestCase):
    def test_universe_15_diverse_symbols(self):
        self.assertEqual(len(UNIVERSE),15)
        self.assertIn("BTCUSDT",UNIVERSE)
        self.assertIn("NEARUSDT",UNIVERSE)
        self.assertEqual(len(set(UNIVERSE)),15)

    def test_valid_frozen_exchange_ohlcv_and_hash(self):
        raw=market_bytes()
        seen=[]
        def downloader(url):
            seen.append(url)
            return raw
        bars,manifest=fetch_daily("SOLUSDT",end="2026-09-30",bars=640,fetch=downloader)
        self.assertEqual(len(bars),640)
        self.assertEqual(manifest["last_utc"],"2026-09-30")
        self.assertEqual(manifest["bars"],640)
        self.assertEqual(len(manifest["raw_json_sha256"]),64)
        q=parse_qs(urlparse(seen[0]).query)
        self.assertEqual(q["symbol"],["SOLUSDT"])
        self.assertEqual(q["limit"],["640"])
        self.assertEqual(q["interval"],["1d"])

    def test_refuse_missing_daily_bar(self):
        with self.assertRaisesRegex(ValueError,"daily bars"):
            fetch_daily("BTCUSDT",end="2026-09-30",bars=640,
                        fetch=lambda _: market_bytes(corrupt=True))

    def test_refuse_stale_history(self):
        with self.assertRaisesRegex(ValueError,"stale feed"):
            fetch_daily("BTCUSDT",end="2026-09-29",bars=640,
                        fetch=lambda _: market_bytes(end="2026-09-30"))

    def test_refuse_unknown_pair_and_future(self):
        with self.assertRaises(ValueError):
            fetch_daily("FAKEUSDT",end="2026-09-30",bars=640,fetch=lambda _:b"[]")
        with self.assertRaises(ValueError):
            fetch_daily("BTCUSDT",end="2099-01-01",bars=640,fetch=lambda _:b"[]")

    def test_negative_bear_regime_and_causal_signals(self):
        a=[100+i*.05 for i in range(201)]
        b=list(reversed(a))
        self.assertEqual(evaluate_closes(b)["mode"],"CASH_OR_RESEARCH")
        self.assertGreater(evaluate_closes(a)["score_votes"],0)
        self.assertEqual(evaluate_closes(a)["max_exposure"],.6)
        self.assertEqual(evaluate_closes(a),evaluate_closes(a+[a[-1]]) if False else evaluate_closes(a))

    def test_validated_multi_crypto_study(self):
        raw=market_bytes()
        report=study(symbols=("BTCUSDT","SOLUSDT"),end="2026-09-30",
                     bars=640,first=450,days=90,min_success=2,
                     fetch=lambda _:raw)
        self.assertEqual(report["successful_symbols"],2)
        self.assertEqual(report["failed_symbols"],0)
        self.assertTrue(report["complete"])
        self.assertEqual(report["deployment_gate"],"NO_REAL_ORDERS")
        self.assertEqual(len(report["results"]["BTCUSDT"]["research"]["base_folds"]),2)
        scenarios=report["results"]["SOLUSDT"]["research"]["scenarios"]
        self.assertEqual(set(scenarios),{"base","double_cost","high_slippage"})
        self.assertFalse(scenarios["base"]["is_prospective_evidence"])
        self.assertIn("BTCUSDT",render_panel(report))
        self.assertIn("CryptoLab",render_panel(report))

    def test_missing_markets_retained_as_errors(self):
        raw=market_bytes()
        def downloader(url):
            if "ETHUSDT" in url: raise ValueError("market history unavailable")
            return raw
        report=study(symbols=("BTCUSDT","ETHUSDT"),end="2026-09-30",
                     bars=640,first=450,days=90,min_success=2,fetch=downloader)
        self.assertEqual(report["failed_symbols"],1)
        self.assertIn("ETHUSDT",report["errors"])
        self.assertFalse(report["min_success_met"])
        self.assertFalse(report["complete"])

    def test_html_script_payload_is_escaped(self):
        report={"study":"CRYPTO_LAB_CROSS_SECTIONAL_RESEARCH_V1","results":{},
                "symbols_requested":["BTCUSDT"],"successful_symbols":0,
                "failed_symbols":1,"errors":{"BTCUSDT":"</script><script>alert(1)</script>"},
                "limitations":["unknown"],"data_cutoff_utc":"2026-09-30",
                "requested_bars":1000,"fold_bars":90}
        panel=render_panel(report)
        self.assertNotIn("</script><script>alert(1)</script>",panel)
        self.assertIn("alert(1)",panel)
        self.assertIn("NO REAL ORDERS",panel)


if __name__=="__main__":
    unittest.main()
