import unittest
from cryptolab.stress import stress_test

def make(n=700):
    out=[]
    for i in range(n):
        p=100+i*.1+(i%23-11)*.15
        out.append({"time":i*86400000,"open":p,"high":p+2,"low":p-2,
                    "close":p,"volume":100.})
    return out

class StressTests(unittest.TestCase):
    def test_scenarios_and_no_approval(self):
        result=stress_test(make())
        self.assertEqual(len(result["scenarios"]),4)
        self.assertEqual(result["verdict"],"RESEARCH_ONLY")
        self.assertIn("beats_passive_base",result["checks"])
    def test_train_selection_unchanged_by_holdout_mutation(self):
        a=make();b=[dict(x) for x in a]
        for x in b[490:]:
            for k in ("open","high","low","close"):
                x[k]*=2
        self.assertEqual(stress_test(a)["selected_target"],stress_test(b)["selected_target"])
    def test_insufficient_history_rejected(self):
        with self.assertRaises(ValueError):
            stress_test(make(250))
if __name__=="__main__": unittest.main()
