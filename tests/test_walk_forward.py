import unittest
from cryptolab.walk_forward import walk_forward

def series(n=1100):
    return [{"time":i*86400000,"open":100+i*.1,"high":101+i*.1,
             "low":99+i*.1,"close":100+i*.1,"volume":100} for i in range(n)]

class WalkForwardTests(unittest.TestCase):
    def test_non_overlapping_folds(self):
        r=walk_forward(series(),initial_train=500,test_size=150,step=150)
        self.assertEqual(r["fold_count"],4)
        for fold in r["folds"]:
            self.assertEqual(fold["test_end_index"]-fold["test_start_index"]+1,150)
    def test_future_data_cannot_select_past_target(self):
        x=series()
        y=[dict(bar) for bar in x]
        for bar in y[650:]:
            for field in ("open","close","high","low"):
                bar[field]*=2
        a=walk_forward(x,initial_train=500,test_size=150,step=150)
        b=walk_forward(y,initial_train=500,test_size=150,step=150)
        self.assertEqual(a["folds"][0]["vol_target"],b["folds"][0]["vol_target"])
        self.assertEqual(a["folds"][0]["strategy_return_pct"],b["folds"][0]["strategy_return_pct"])
    def test_bad_parameters(self):
        with self.assertRaises(ValueError):
            walk_forward(series(),initial_train=200)
if __name__=="__main__":
    unittest.main()
