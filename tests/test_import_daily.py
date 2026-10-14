import tempfile
import unittest
from pathlib import Path
from cryptolab.import_daily import import_daily

class ImportDailyTests(unittest.TestCase):
    def test_valid_series(self):
        from datetime import date,timedelta
        with tempfile.TemporaryDirectory() as d:
            source=Path(d)/"source.csv"
            start=date(2020,1,1)
            rows=["date,open,high,low,close,volume"]+[
                f"{(start+timedelta(days=i)).isoformat()},100,110,90,101,1000"
                for i in range(60)]
            source.write_text("\n".join(rows))
            result=import_daily(source,Path(d)/"output.csv")
            self.assertEqual(result["rows"],60)
    def test_missing_bar_rejected(self):
        from datetime import date,timedelta
        with tempfile.TemporaryDirectory() as d:
            source=Path(d)/"source.csv"
            start=date(2020,1,1)
            rows=["date,open,high,low,close,volume"]+[
                f"{(start+timedelta(days=i+(i>=30))).isoformat()},100,110,90,101,1000"
                for i in range(60)]
            source.write_text("\n".join(rows))
            with self.assertRaises(ValueError):
                import_daily(source,Path(d)/"out.csv")
if __name__=="__main__":
    unittest.main()
