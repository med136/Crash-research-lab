import unittest
from cryptolab.engine import backtest,signal
from cryptolab.market import validate

class EngineTests(unittest.TestCase):
    def candles(self,n=100):
        return [{"time":i*3600000,"open":100+i,"high":101+i,
                 "low":99+i,"close":100+i,"volume":10} for i in range(n)]
    def test_signal(self):
        self.assertEqual(signal(list(range(40)),10,30),1)
    def test_no_future_leakage(self):
        a=self.candles()
        b=[dict(x) for x in a]
        b[-1]["close"]=b[-1]["high"]
        ra=backtest(a); rb=backtest(b)
        self.assertEqual(ra.trades,rb.trades)
        self.assertEqual(ra.curve[:-1],rb.curve[:-1])
    def test_costs(self):
        a=self.candles()
        self.assertGreaterEqual(backtest(a,fee=0).final,backtest(a,fee=.01).final)
    def test_trend_buy(self):
        r=backtest(self.candles())
        self.assertGreater(r.trades,0)
        self.assertGreater(r.final,0)
    def test_reject_bad(self):
        with self.assertRaises(ValueError):
            backtest(self.candles(20))
        with self.assertRaises(ValueError):
            validate(list(reversed(self.candles())))
if __name__=="__main__":
    unittest.main()
