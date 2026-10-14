import sys
import types
import unittest
from unittest.mock import patch
from cryptolab.audit_stats import cost_scenarios


class CostScenarioTests(unittest.TestCase):
    def test_three_cost_configs_and_conservative_verdict(self):
        calls=[]
        def fake_paired(data, *, first, days, target, fee, slippage):
            calls.append((fee,slippage))
            f={"voltrend":{"return_pct":1.,"max_drawdown_pct":-5.},
               "passive":{"return_pct":2.,"max_drawdown_pct":-8.}}
            return {"folds":[f,f],"summary":{"voltrend":{},"passive":{}}}
        with patch.dict(sys.modules,{"cryptolab.paired":types.SimpleNamespace(paired_windows=fake_paired)}):
            r=cost_scenarios([],first=900,days=180)
        self.assertEqual(r["decision"],"NO_REAL_ORDERS")
        self.assertEqual(set(r["scenarios"]),{"base","double_cost","high_slippage"})
        self.assertEqual(calls,[(.001,.0005),(.002,.001),(.001,.003)])
        self.assertLess(r["scenarios"]["base"]["strategy_vs_passive"]["mean_excess_return_pp"],0)


if __name__ == "__main__":
    unittest.main()
