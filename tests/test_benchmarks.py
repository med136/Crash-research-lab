import unittest
from cryptolab.benchmarks import buy_and_hold

class BenchmarksTest(unittest.TestCase):
    def test_only_entry_exit_fees(self):
        candles=[{"open":100.,"close":100.} for _ in range(60)]
        a=buy_and_hold(candles,0,60,fee=0,slippage=0)
        self.assertEqual(a["trades"],2)
        self.assertAlmostEqual(a["final"],1000)
        b=buy_and_hold(candles,0,60,fee=.001,slippage=.0005)
        self.assertLess(b["final"],1000)
        self.assertEqual(b["trades"],2)
    def test_missing_history(self):
        with self.assertRaises(ValueError):
            buy_and_hold([],0,0)
if __name__=="__main__":
    unittest.main()
