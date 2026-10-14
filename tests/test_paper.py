import tempfile
import unittest
from pathlib import Path
from cryptolab.paper import new_state,step,apply_new_candles,save_state,load_state,summary

def candles(n=40):
    return [{"time":i*3600000,"close":100+i} for i in range(n)]

class PaperTests(unittest.TestCase):
    def test_first_trade_waits_for_new_observation(self):
        history=candles()
        state=new_state(history,fast=10,slow=30)
        self.assertEqual(len(state["trades"]),0)
        self.assertEqual(state["pending_target"],1)
        step(state,history[-1])
        self.assertEqual(len(state["trades"]),0)
        step(state,{"time":40*3600000,"close":141})
        self.assertEqual(state["trades"][0]["side"],"BUY")
        self.assertEqual(state["trades"][0]["price"],141)
    def test_duplicate_idempotent(self):
        s=new_state(candles())
        step(s,{"time":40*3600000,"close":140})
        before=dict(s)
        step(s,{"time":40*3600000,"close":140})
        self.assertEqual(s,before)
    def test_reject_backdated(self):
        s=new_state(candles())
        with self.assertRaises(ValueError):
            step(s,{"time":1,"close":150})
    def test_state_persists(self):
        s=new_state(candles())
        with tempfile.TemporaryDirectory() as d:
            path=str(Path(d)/"state.json")
            save_state(s,path)
            self.assertEqual(load_state(path),s)
        self.assertEqual(summary(s)["trades"],0)
    def test_batch_same_as_single(self):
        seq=[{"time":i*3600000,"close":100+i} for i in range(40,45)]
        a=new_state(candles());b=new_state(candles())
        apply_new_candles(a,seq)
        for candle in seq:step(b,candle)
        self.assertEqual(a,b)

if __name__=="__main__": unittest.main()
