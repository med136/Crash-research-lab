import unittest
from cryptolab.capital100_panel import render_capital_panel

class HundredDollarPanelTests(unittest.TestCase):
    def test_requires_report_type(self):
        with self.assertRaises(ValueError):
            render_capital_panel({"study":"WRONG"})
    def test_french_english_toggle_and_100_capital(self):
        r={"study":"CRYPTO_LAB_100_USD_EXPLORATORY_V1",
           "capital_usd":100.,"historical_cutoff_utc":"2026-09-30",
           "assets_requested":["BTCUSDT"],"assets":{},"errors":{},
           "successful_assets":0,"strategies":["cash","buy_hold"],
           "horizons":{"1_month_30d":30},"limitations":["historical only"]}
        html=render_capital_panel(r)
        self.assertIn('<html lang="fr">',html)
        self.assertIn('id="locale-fr"',html)
        self.assertIn('id="locale-en"',html)
        self.assertIn("Que seraient devenus 100",html)
        self.assertIn("AUCUN ORDRE RÉEL",html)
        self.assertIn("2026-09-30",html)
    def test_html_script_breakout_escaped(self):
        r={"study":"CRYPTO_LAB_100_USD_EXPLORATORY_V1",
           "capital_usd":100.,"historical_cutoff_utc":"2026-09-30",
           "assets_requested":[],"assets":{},
           "errors":{"unexpected":"</script><script>alert(1)</script>"},
           "successful_assets":0,"strategies":[],"horizons":{},
           "limitations":[]}
        html=render_capital_panel(r)
        self.assertNotIn("</script><script>alert(1)</script>",html)
        self.assertIn("alert(1)",html)

if __name__=="__main__": unittest.main()
