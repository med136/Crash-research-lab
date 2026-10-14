import unittest
from cryptolab.strategies import Strategy,run,select_and_test

def series(n=600):
    values=[]
    for i in range(n):
        price=100+i*.06 + (i%17-8)*.15
        values.append({"time":i*86400000,"open":price,"high":price+2,
                       "low":price-2,"close":price+.01,"volume":500})
    return values

class StrategyTests(unittest.TestCase):
    def test_holdout_not_used_for_selection(self):
        a=series()
        b=[dict(x) for x in a]
        for x in b[420:]:
            for k in ("open","high","low","close"):
                x[k]*=2
        self.assertEqual(select_and_test(a)["chosen"],select_and_test(b)["chosen"])
        self.assertEqual(select_and_test(a)["train_candidates"],select_and_test(b)["train_candidates"])
    def test_costs_decrease_result(self):
        a=series()
        config=Strategy("test",100,20,3.,.5)
        self.assertGreaterEqual(run(a,config,fee=0,slippage=0)["equity"],
                                run(a,config,fee=.01,slippage=.01)["equity"])
    def test_validation(self):
        with self.assertRaises(ValueError):
            select_and_test(series(200))
    def test_no_intrabar_foreknowledge(self):
        a=series()
        b=[dict(x) for x in a]
        b[-1]["close"]=b[-1]["high"]
        config=Strategy("test",100,20,3.,.5)
        ra=run(a,config)
        rb=run(b,config)
        self.assertEqual(ra["trades"],rb["trades"])
        self.assertEqual(ra["curve"][:-1],rb["curve"][:-1])
if __name__=="__main__":
    unittest.main()
