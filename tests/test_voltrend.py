import unittest
from cryptolab.voltrend import run

def bars(n=600):
    return [{"time":i*86400000,"open":100+i*.2,
             "high":101+i*.2,"low":99+i*.2,"close":100+i*.2,"volume":1000} for i in range(n)]

class VolTrendTests(unittest.TestCase):
    def test_run(self):
        r=run(bars())
        self.assertGreater(r["final"],0)
        self.assertGreaterEqual(r["trades"],1)
    def test_no_future_leak(self):
        a=bars();b=[dict(x) for x in a]
        b[-1]["close"]=b[-1]["high"]
        ra=run(a);rb=run(b)
        self.assertEqual(ra["trades"],rb["trades"])
        self.assertEqual(ra["curve"][:-1],rb["curve"][:-1])
    def test_validation(self):
        with self.assertRaises(ValueError):
            run(bars(50))
if __name__=="__main__":
    unittest.main()
