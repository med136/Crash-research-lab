import calendar
import csv
import hashlib
import io
import tempfile
import unittest
import zipfile
from datetime import datetime,timezone
from pathlib import Path
from cryptolab.binance_bulk import parse_archive, fetch_archive, download_months, month_names


def make_archive(symbol, month, *, corrupt_day=None, bad_price=False):
    y,m=map(int,month.split('-'))
    micro=y>=2025
    output=io.BytesIO()
    name=f'{symbol}-1d-{month}.csv'
    with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as zip:
        body=io.StringIO();wr=csv.writer(body)
        for day in range(1,calendar.monthrange(y,m)[1]+1):
            t=int(datetime(y,m,day,tzinfo=timezone.utc).timestamp()*1000)*(1000 if micro else 1)
            if corrupt_day==day:t+=86_400_000*(1000 if micro else 1)
            length=86_400_000*(1000 if micro else 1)
            wr.writerow([t,100,105,95,200 if bad_price and day==1 else 101,1000,t+length-1,0,0,0,0,0])
        zip.writestr(name,body.getvalue())
    return output.getvalue()


class BinanceBulkTests(unittest.TestCase):
    def test_2024_millisecond_archive(self):
        rows=parse_archive(make_archive('BTCUSDT','2024-02'),symbol='BTCUSDT',month='2024-02')
        self.assertEqual(len(rows),29)
        self.assertEqual(rows[0]['time'],1706745600000)
    def test_2025_microsecond_archive(self):
        rows=parse_archive(make_archive('ETHUSDT','2025-01'),symbol='ETHUSDT',month='2025-01')
        self.assertEqual(len(rows),31)
        self.assertEqual(rows[0]['time'],1735689600000)
    def test_reject_missing_or_wrong_day(self):
        with self.assertRaises(ValueError):
            parse_archive(make_archive('BTCUSDT','2024-02',corrupt_day=10),symbol='BTCUSDT',month='2024-02')
    def test_reject_invalid_ohlcv(self):
        with self.assertRaises(ValueError):
            parse_archive(make_archive('BTCUSDT','2024-02',bad_price=True),symbol='BTCUSDT',month='2024-02')
    def test_checksum_verification(self):
        blob=make_archive('BTCUSDT','2024-02')
        filename='BTCUSDT-1d-2024-02.zip'
        def fetch(url):
            if url.endswith('.CHECKSUM'):
                return f'{hashlib.sha256(blob).hexdigest()}  {filename}\n'.encode()
            return blob
        bars,meta=fetch_archive('BTCUSDT','2024-02',fetch=fetch)
        self.assertEqual(len(bars),29)
        self.assertEqual(meta['checksum_sha256'],hashlib.sha256(blob).hexdigest())
        def tampered(url):
            if url.endswith('.CHECKSUM'):
                return (('0'*64)+'  '+filename).encode()
            return blob
        with self.assertRaises(ValueError):
            fetch_archive('BTCUSDT','2024-02',fetch=tampered)
    def test_multiple_months_contiguous_with_manifest(self):
        blobs={m:make_archive('BTCUSDT',m) for m in ('2024-02','2024-03')}
        def fetch(url):
            month='2024-02' if '2024-02' in url else '2024-03'
            blob=blobs[month]
            if url.endswith('.CHECKSUM'):
                return f'{hashlib.sha256(blob).hexdigest()} BTCUSDT-1d-{month}.zip'.encode()
            return blob
        with tempfile.TemporaryDirectory() as d:
            p=str(Path(d)/'btc.csv')
            result=download_months('BTCUSDT','2024-02','2024-03',p,fetch=fetch)
            self.assertEqual(result['bars'],60)
            self.assertTrue(Path(p+'.manifest.json').exists())
    def test_reject_future_and_reversed_months(self):
        for start,end in [('2025-02','2025-01'),('2099-01','2099-02')]:
            with self.assertRaises(ValueError): month_names(start,end)

if __name__=='__main__':
    unittest.main()
