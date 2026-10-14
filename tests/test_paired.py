import unittest
from cryptolab.paired import paired_windows

def series(n=1000):
    return [{"time":i*86400000,
             "open":100+i*.13,"high":101+i*.13,"low":99+i*.13,
             "close":100+i*.13,"volume":100.} for i in range(n)]

class PairedTests(unittest.TestCase):
    def test_exact_same_windows(self):
        r=paired_windows(series(),first=500,days=100)
        self.assertEqual(r["fold_count"],5)
        for f in r["folds"]:
            self.assertEqual(f["end_index"]-f["start_index"]+1,100)
            self.assertEqual(f["passive"]["trades"],2)
            self.assertIn("0.5",f["fixed"])
    def test_future_does_not_change_past_fold(self):
        a=series()
        b=[dict(x) for x in a]
        for bar in b[600:]:
            for k in ("open","high","low","close"):
                bar[k]*=2
        x=paired_windows(a,first=500,days=100)
        y=paired_windows(b,first=500,days=100)
        self.assertEqual(x["folds"][0],y["folds"][0])
    def test_invalid_window(self):
        with self.assertRaises(ValueError):
            paired_windows(series(550),first=500,days=100)
if __name__=="__main__":
    unittest.main()
