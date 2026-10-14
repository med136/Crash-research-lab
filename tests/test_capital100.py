import math
import unittest
from cryptolab.capital100 import (
    CAPITAL,HORIZONS,STRATEGIES,analyze_market,aggregate,signal_targets,simulate,windows
)

DAY=86_400_000

def candles(n=1000,kind="up"):
    result=[]
    for i in range(n):
        if kind=="up":price=100+i*.24+math.sin(i*.25)*2
        elif kind=="down":price=300-i*.20+math.sin(i*.35)*2
        else:price=120+math.sin(i*.1)*12+math.sin(i*.51)*3
        result.append({"time":i*DAY,"open":price,"high":price+5,
                       "low":price-5,"close":price,"volume":100+i})
    return result

class HundredDollarTests(unittest.TestCase):
    def test_initial_100_all_time_horizons(self):
        out=analyze_market(candles())
        self.assertEqual(out["initial_usd"],100.)
        for h in HORIZONS:
            x=out["scenarios"]["base"][h]
            self.assertGreaterEqual(x["window_count"],2)
            self.assertEqual(set(x["models"]),set(STRATEGIES))
            self.assertEqual(x["models"]["cash"]["median_final_usd"],100.)
            self.assertAlmostEqual(x["models"]["cash"]["mean_max_drawdown_pct"],0.)
            self.assertEqual(x["models"]["cash"]["mean_rebalances"],0)
    def test_no_future_information_in_signals(self):
        x=candles(); y=[dict(c) for c in x]
        for row in y[700:]:
            row.update(open=row["open"]*2,close=row["close"]*2,high=row["high"]*2)
        a=signal_targets(x);b=signal_targets(y)
        for name in STRATEGIES:self.assertEqual(a[name][201:700],b[name][201:700])
    def test_cash_remains_exact_100_and_zero_trades(self):
        c=candles();r=simulate(c,[0.]*len(c),201,291)
        self.assertEqual(r["final_usd"],100.)
        self.assertEqual(r["entries"],0);self.assertEqual(r["exits"],0)
    def test_fee_and_slippage_stress(self):
        c=candles();hold=[1.]*len(c)
        cheap=simulate(c,hold,201,566,fee=.001,slippage=.0005)
        costly=simulate(c,hold,201,566,fee=.002,slippage=.003)
        self.assertGreater(cheap["final_usd"],100.)
        self.assertLess(costly["final_usd"],cheap["final_usd"])
        self.assertGreaterEqual(cheap["entries"],1)
        self.assertEqual(cheap["exits"],1)
    def test_target_is_at_prior_candle_close(self):
        c=candles();a=[0.]*len(c);a[201]=1.;a[202]=0.
        run=simulate(c,a,201,203,fee=0,slippage=0)
        self.assertEqual(run["entries"],1);self.assertEqual(run["exits"],1)
        self.assertAlmostEqual(run["final_usd"],100*c[202]["open"]/c[201]["open"])
    def test_trade_size_and_no_leverage(self):
        c=candles()
        self.assertGreaterEqual(simulate(c,[1.]*len(c),201,231)["final_usd"],0)
        tiny=simulate(c,[.02]*len(c),201,231,min_trade_usd=5.)
        self.assertEqual(tiny["final_usd"],100.)
        self.assertEqual(tiny["entries"],0)
    def test_invalid_window_and_weight(self):
        c=candles()
        with self.assertRaises(ValueError):simulate(c,[0.]*len(c),100,300)
        with self.assertRaises(ValueError):simulate(c,[1.1]*len(c),201,350)
    def test_fold_dates_nonoverlap_and_benchmarks(self):
        c=candles();signals=signal_targets(c)
        for days in HORIZONS.values():
            folds=windows(c,signals,days,.001,.0005)
            self.assertEqual(len(folds),(len(c)-201)//days)
            self.assertTrue(all(a["end_index"]<b["start_index"] for a,b in zip(folds,folds[1:])))
            self.assertEqual(aggregate(folds)["cash"]["worst_final_usd"],100.)

if __name__=="__main__":
    unittest.main()
