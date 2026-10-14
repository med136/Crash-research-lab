import unittest
from cryptolab.audit_stats import paired_audit


def fold(x, dd=-10):
    return {"voltrend":{"return_pct":x,"max_drawdown_pct":dd},
            "passive":{"return_pct":0.,"max_drawdown_pct":-25.}}


class AuditStatsTests(unittest.TestCase):
    def test_all_winners_sign_probability(self):
        r=paired_audit([fold(10) for _ in range(5)],bootstrap_samples=100,seed=1)
        self.assertEqual(r["wins"],5)
        self.assertAlmostEqual(r["exact_two_sided_sign_p"],.0625)
        self.assertEqual(r["bootstrap_mean_excess_95pct_pp"],[10,10])
        self.assertFalse(r["is_prospective_evidence"])
    def test_mixed_returns(self):
        r=paired_audit([fold(-3),fold(2),fold(4),fold(-1)],bootstrap_samples=100,seed=2)
        self.assertEqual(r["wins"],2)
        self.assertEqual(r["losses"],2)
        self.assertEqual(r["median_excess_return_pp"],.5)
        self.assertEqual(r["exact_two_sided_sign_p"],1.)
        self.assertEqual(r["average_max_drawdown_improvement_pp"],15.)
    def test_ties_ignored_for_sign(self):
        r=paired_audit([fold(0),fold(2),fold(2)],bootstrap_samples=100)
        self.assertEqual(r["ties"],1)
        self.assertAlmostEqual(r["exact_two_sided_sign_p"],.5)
    def test_reject_nonfinite(self):
        with self.assertRaises(ValueError):
            paired_audit([fold(float("nan")),fold(1)])
    def test_reproducible(self):
        a=[fold(i) for i in [-3,2,1,4,0,1]]
        self.assertEqual(paired_audit(a,bootstrap_samples=100),paired_audit(a,bootstrap_samples=100))
    def test_reject_insufficient_folds(self):
        with self.assertRaises(ValueError):
            paired_audit([fold(2)])


if __name__ == "__main__":
    unittest.main()
