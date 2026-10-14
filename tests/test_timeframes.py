import json
import math
import unittest
from datetime import date, datetime, timedelta, timezone
from urllib.parse import parse_qs, urlparse
from cryptolab.timeframes import (
    fetch_bars, evaluate_bars, study, INTERVAL_MS, DEFAULT_FRAMES,
)
from cryptolab.intraday_panel import render_timeframe_panel
from cryptolab.voltrend import run


def synthetic(symbol="BTCUSDT", frame="5m", end="2026-09-30", bars=640, *, skip=False):
    dt=INTERVAL_MS[frame]
    day=date.fromisoformat(end)
    next_day=datetime(day.year,day.month,day.day,tzinfo=timezone.utc)+timedelta(days=1)
    last=int(next_day.timestamp()*1000)-dt
    items=[]
    for i in range(bars):
        tm=last-(bars-1-i)*dt
        if skip and i==bars//2: tm+=dt
        p=200+i*.06
        items.append([tm,str(p),str(p+2),str(p-2),str(p+.1),
                      str(140+i),tm+dt-1,"1000",1,"1","1","0"])
    return json.dumps(items).encode()


class TimeframeTests(unittest.TestCase):
    def test_four_small_frames(self):
        self.assertEqual(DEFAULT_FRAMES,("5m","15m","1h","4h"))

    def test_fetch_every_frame_and_provenance(self):
        for frame in DEFAULT_FRAMES:
            with self.subTest(frame=frame):
                def mock_fetch(url):
                    q=parse_qs(urlparse(url).query)
                    self.assertEqual(q["interval"],[frame])
                    self.assertEqual(q["limit"],["640"])
                    return synthetic(frame=frame)
                candles,manifest=fetch_bars("BTCUSDT",frame,end="2026-09-30",bars=640,fetch=mock_fetch)
                self.assertEqual(len(candles),640)
                self.assertEqual(candles[1]["time"]-candles[0]["time"],INTERVAL_MS[frame])
                self.assertEqual(manifest["timeframe"],frame)
                self.assertEqual(len(manifest["raw_json_sha256"]),64)

    def test_rejects_gap_in_intraday_history(self):
        with self.assertRaises(ValueError):
            fetch_bars("BTCUSDT","15m",end="2026-09-30",bars=640,
                       fetch=lambda _:synthetic(frame="15m",skip=True))

    def test_rejects_stale_or_future_date(self):
        with self.assertRaises(ValueError):
            fetch_bars("BTCUSDT","1h",end="2026-09-29",bars=640,
                       fetch=lambda _:synthetic(frame="1h"))
        with self.assertRaises(ValueError):
            fetch_bars("BTCUSDT","1h",end="2099-01-01",bars=640,
                       fetch=lambda _:b"[]")

    def test_intraday_volatility_correct_scale(self):
        bars,_=fetch_bars("BTCUSDT","5m",end="2026-09-30",bars=640,
                          fetch=lambda _:synthetic(frame="5m"))
        # Same candle data, different annualization scales. Larger number
        # of candles/year increases annualized volatility and can reduce exposure.
        short=run(bars,start_at=450,vol_target=.60,bars_per_year=365.)
        actual=run(bars,start_at=450,vol_target=.60,bars_per_year=365*288.)
        self.assertTrue(math.isfinite(short["return_pct"]))
        self.assertTrue(math.isfinite(actual["return_pct"]))
        self.assertNotEqual(short["return_pct"],actual["return_pct"])
        self.assertGreaterEqual(actual["max_drawdown_pct"],-100.)

    def test_frame_window_in_actual_hours(self):
        for frame,hours in (("5m",7.5),("15m",22.5),("1h",90.),("4h",360.)):
            bars,_=fetch_bars("BTCUSDT",frame,end="2026-09-30",bars=640,
                               fetch=lambda _,frame=frame:synthetic(frame=frame))
            r=evaluate_bars(bars,interval=frame,first=450,window=90)
            self.assertEqual(r["window_hours"],hours)
            self.assertEqual(r["folds"],2)
            self.assertEqual(set(r["scenarios"]),{"base","double_cost","high_slippage"})

    def test_study_records_failed_market(self):
        def fake(url):
            q=parse_qs(urlparse(url).query)
            if q["symbol"][0]=="ETHUSDT": raise ValueError("no spot bars")
            return synthetic(frame=q["interval"][0])
        r=study(symbols=("BTCUSDT","ETHUSDT"),frames=("5m",),
                end="2026-09-30",bars=640,first=450,window=90,
                min_success=2,fetch=fake)
        self.assertEqual(r["successful_markets"],1)
        self.assertEqual(r["failed_markets"],1)
        self.assertIn("ETHUSDT@5m",r["errors"])
        self.assertFalse(r["min_success_met"])
        self.assertEqual(r["deployment_gate"],"NO_REAL_ORDERS")

    def test_french_panel_switch_and_escaping(self):
        r=study(symbols=("BTCUSDT",),frames=("15m",),
                end="2026-09-30",bars=640,first=450,window=90,
                min_success=1,fetch=lambda _:synthetic(frame="15m"))
        r["errors"]["injection"]="</script><script>alert(1)</script>"
        panel=render_timeframe_panel(r)
        self.assertIn('<html lang="fr">',panel)
        self.assertIn('id="locale-fr"',panel)
        self.assertIn('id="locale-en"',panel)
        self.assertIn("Toutes les unités",panel)
        self.assertNotIn("</script><script>alert(1)</script>",panel)
        self.assertIn("BTCUSDT",panel)

    def test_daily_existing_panel_has_language_toggle(self):
        from cryptolab.panel import render_panel
        report={"study":"CRYPTO_LAB_CROSS_SECTIONAL_RESEARCH_V1",
                "symbols_requested":[],"results":{},"errors":{},
                "successful_symbols":0,"failed_symbols":0,
                "data_cutoff_utc":"2026-09-30","requested_bars":640,"fold_bars":90}
        html=render_panel(report)
        self.assertIn('<html lang="fr">',html)
        self.assertIn('id="locale-fr"',html)
        self.assertIn('id="locale-en"',html)
        self.assertIn("Tableau de recherche",html)

if __name__=="__main__":
    unittest.main()
