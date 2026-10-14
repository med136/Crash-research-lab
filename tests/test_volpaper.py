import json
import math
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from cryptolab.market import save
from cryptolab.volpaper import (
    DAY_MS, HISTORY_LENGTH, initialize, target_from_history,
    step, advance, report, state_lock, once,
)


def history(n=205, *, rise=True):
    prices=[100 + i * .17 if rise else 300 - i * .17 for i in range(n)]
    return [
        {"time":i * DAY_MS, "open":p, "high":p+1, "low":p-1,
         "close":p, "volume":10.0}
        for i,p in enumerate(prices)
    ]


class VolatilityPaperTests(unittest.TestCase):
    def test_warm_up_no_lookahead_or_backfilled_trades(self):
        rows=history()
        s=initialize(rows, symbol="BTCUSDT")
        self.assertEqual(s["trades"], [])
        self.assertEqual(s["cash"], 1000.)
        self.assertGreater(s["pending_target"],0.)
        self.assertLessEqual(s["pending_target"],1.)
        next_bar=history(206)[-1]
        t=step(s,next_bar)
        self.assertEqual(t["trades"][0]["time"], next_bar["time"])
        self.assertEqual(t["trades"][0]["fill_assumption"], "hypothetical_at_observed_close")
        self.assertEqual(s["trades"], [])
        self.assertEqual(t["last_time"],next_bar["time"])
        self.assertEqual(t["pending_target"],target_from_history(t["history"]))
        self.assertGreater(t["units"],0)
        self.assertGreaterEqual(t["cash"],0)

    def test_downtrend_stays_in_cash(self):
        s=initialize(history(rise=False),symbol="BTCUSDT")
        self.assertEqual(s["pending_target"],0.)
        t=step(s,history(206,rise=False)[-1])
        self.assertEqual(t["trades"], [])
        self.assertEqual(t["cash"],1000)

    def test_same_bar_is_idempotent(self):
        rows=history()
        s=initialize(rows,symbol="BTCUSDT")
        bar=history(206)[-1]
        once_state=step(s,bar)
        original=deepcopy(once_state)
        self.assertEqual(step(once_state,bar),once_state)
        self.assertEqual(once_state,original)

    def test_conflicting_revision_fails(self):
        s=initialize(history(),symbol="ETHUSDT")
        last=history()[-1]
        revised=dict(last,close=last["close"]+.2)
        with self.assertRaises(ValueError):
            step(s,revised)

    def test_gap_and_backwards_refused_without_mutation(self):
        s=initialize(history(),symbol="BTCUSDT")
        before=deepcopy(s)
        with self.assertRaises(ValueError):
            step(s,history(207)[-1])
        with self.assertRaises(ValueError):
            step(s,history(203)[-1])
        self.assertEqual(s,before)

    def test_replay_and_restart_offline(self):
        with tempfile.TemporaryDirectory() as d:
            source=Path(d)/"historical.csv"
            wallet=Path(d)/"portfolio.json"
            save(history(),source)
            first=once(symbol="BTCUSDT",path=str(wallet),input_csv=str(source))
            self.assertEqual(first["executions"],0)
            self.assertEqual(first["source"],"csv_replay")
            save(history(206),source)
            second=once(symbol="BTCUSDT",path=str(wallet),input_csv=str(source))
            third=once(symbol="BTCUSDT",path=str(wallet),input_csv=str(source))
            self.assertEqual(second,third)
            self.assertGreater(second["executions"],0)
            saved=json.loads(wallet.read_text())
            self.assertEqual(saved["last_time"],history(206)[-1]["time"])
            self.assertEqual(len(saved["history"]),HISTORY_LENGTH)

    def test_symbol_switch_is_forbidden(self):
        with tempfile.TemporaryDirectory() as d:
            csv=Path(d)/"bars.csv";wallet=Path(d)/"wallet.json"
            save(history(),csv)
            once(symbol="BTCUSDT",path=str(wallet),input_csv=str(csv))
            with self.assertRaises(ValueError):
                once(symbol="ETHUSDT",path=str(wallet),input_csv=str(csv))

    def test_old_sma_wallet_is_incompatible(self):
        with tempfile.TemporaryDirectory() as d:
            csv=Path(d)/"bars.csv";wallet=Path(d)/"wallet.json"
            save(history(),csv)
            wallet.write_text(json.dumps({"version":1,"model":"sma"}))
            with self.assertRaises(ValueError):
                once(symbol="BTCUSDT",path=str(wallet),input_csv=str(csv))

    def test_lock_is_exclusive(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"wallet.json"
            with state_lock(path):
                with self.assertRaises(RuntimeError):
                    with state_lock(path):
                        pass
            self.assertFalse(Path(str(path)+".lock").exists())

    def test_missing_bar_replay_fails_without_saving_state(self):
        with tempfile.TemporaryDirectory() as d:
            source=Path(d)/"historical.csv"
            wallet=Path(d)/"portfolio.json"
            save(history(),source)
            once(symbol="BTCUSDT",path=str(wallet),input_csv=str(source))
            before=wallet.read_bytes()
            broken=history(207)
            broken.pop(-2)
            save(broken,source)
            with self.assertRaises(ValueError):
                once(symbol="BTCUSDT",path=str(wallet),input_csv=str(source))
            self.assertEqual(wallet.read_bytes(),before)

    def test_reject_invalid_close(self):
        s=initialize(history(),symbol="BTCUSDT")
        bar=history(206)[-1]
        with self.assertRaises(ValueError):
            step(s,dict(bar,close=math.inf))

    def test_exposure_is_capped(self):
        s=initialize(history(),symbol="BTCUSDT",vol_target=1.)
        t=step(s,history(206)[-1])
        self.assertLessEqual(t["units"]*t["last_close"] /
                             (t["cash"]+t["units"]*t["last_close"]),1.+1e-12)

    def test_mixed_source_state_rejected(self):
        s=initialize(history(),symbol="BTCUSDT",source="csv_replay")
        self.assertEqual(report(s)["paper_only"],True)


if __name__ == "__main__":
    unittest.main()
