import unittest
from cryptolab.exposure import constant_weight

def bars(n=100):
    return [{"open":100+i*.1,"close":100+i*.1} for i in range(n)]

class ConstantWeightTests(unittest.TestCase):
    def test_zero_weight_holds_cash(self):
        r=constant_weight(bars(),0,100,weight=0)
        self.assertEqual(r["trades"],0)
        self.assertAlmostEqual(r["final"],1000)
    def test_lower_fee_improves_trending_result(self):
        a=constant_weight(bars(),0,100,weight=.5,fee=0,slippage=0)
        b=constant_weight(bars(),0,100,weight=.5,fee=.002,slippage=.001)
        self.assertGreater(a["final"],b["final"])
    def test_invalid_weight(self):
        with self.assertRaises(ValueError):
            constant_weight(bars(),0,100,weight=1.1)
if __name__=="__main__":
    unittest.main()
