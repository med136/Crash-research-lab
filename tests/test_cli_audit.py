import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from cryptolab import cli


class AuditCliTests(unittest.TestCase):
    def test_cli_produces_machine_readable_report(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"bars.csv"
            with path.open("w") as f:
                f.write("time,open,high,low,close,volume\n")
                for i in range(700):
                    price=100+i/10
                    f.write(f"{i*86400000},{price},{price+2},{price-2},{price},100\n")
            output=io.StringIO()
            with patch("sys.argv",["cryptolab","audit","--input",str(path),"--first","500","--days","100"]):
                with contextlib.redirect_stdout(output):
                    cli.main()
            report=json.loads(output.getvalue())
            self.assertEqual(report["decision"],"NO_REAL_ORDERS")
            self.assertEqual(report["scenarios"]["base"]["strategy_vs_passive"]["folds"],2)


if __name__=="__main__":
    unittest.main()
