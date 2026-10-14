import unittest
from cryptolab.market import validate

def candles(n=60):
    return [{"time":i*3600000,"open":100.,"high":101.,"low":99.,
             "close":100.,"volume":1.} for i in range(n)]

class MarketValidationTests(unittest.TestCase):
    def test_accepts_complete_bars(self):
        validate(candles())
    def test_rejects_nan(self):
        c=candles();c[-1]["close"]=float("nan")
        with self.assertRaises(ValueError):
            validate(c)
    def test_rejects_invalid_envelope(self):
        c=candles();c[-1]["high"]=98.
        with self.assertRaises(ValueError):
            validate(c)
    def test_rejects_duplicate(self):
        c=candles();c[-1]["time"]=c[-2]["time"]
        with self.assertRaises(ValueError):
            validate(c)
    def test_rejects_negative_volume(self):
        c=candles();c[-1]["volume"]=-1.
        with self.assertRaises(ValueError):
            validate(c)

if __name__=="__main__":
    unittest.main()
