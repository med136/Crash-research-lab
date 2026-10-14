import unittest
from cryptolab.vol_research import select_vol_target

def candles(n=600):
    return [{"time":i*86400000,"open":100+i*.1,"high":101+i*.1,
             "low":99+i*.1,"close":100+i*.1,"volume":10} for i in range(n)]

class SelectionTests(unittest.TestCase):
    def test_untouched_holdout(self):
        a=candles();b=[dict(x) for x in a]
        for x in b[420:]:
            x["open"]*=2;x["close"]*=2;x["high"]*=2;x["low"]*=2
        ra=select_vol_target(a);rb=select_vol_target(b)
        self.assertEqual(ra["chosen_volatility_target"],rb["chosen_volatility_target"])
        self.assertEqual(ra["training"],rb["training"])
if __name__=="__main__":
    unittest.main()
