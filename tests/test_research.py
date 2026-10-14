import unittest
from cryptolab.research import evaluate

def prices(n=500):
    return [{"time":i*3600000,"open":float(100+i/10+(i%21-10)*.1),
             "close":float(100+i/10+(i%21-10)*.1),
             "high":float(101+i/10+(i%21-10)*.1),
             "low":float(99+i/10+(i%21-10)*.1),"volume":10.0}
            for i in range(n)]

class ResearchTests(unittest.TestCase):
    def test_holdout_cannot_influence_selection(self):
        a=prices();b=[dict(x) for x in a]
        for i in range(325,len(b)):
            for key in ("open","close","high","low"):
                b[i][key]*=3
        x=evaluate(a);y=evaluate(b)
        self.assertEqual(x["selected"],y["selected"])
        self.assertEqual(x["training_candidates"],y["training_candidates"])
    def test_output(self):
        r=evaluate(prices())
        self.assertEqual(r["holdout_candles"],175)
        self.assertEqual(len(r["training_candidates"]),4)
        self.assertIn("buy_hold_pct",r["holdout"])
    def test_insufficient_candles(self):
        with self.assertRaises(ValueError):
            evaluate(prices(200))
if __name__=="__main__":
    unittest.main()
