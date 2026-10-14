import csv
import json
import pytest
from crashlab.import_frames import import_jsonl, normalize_timestamp

def frame(rid=10, multiplier=2.1, target="OnCrash"):
    return json.dumps({"type":1,"target":target,"arguments":[{"l":rid,"f":multiplier}]}) + "\x1e"

def write(tmp_path, records):
    source = tmp_path / "frames.jsonl"
    source.write_text("".join(json.dumps(r) + "\n" for r in records))
    return source

def record(at, content):
    return {"received_at":at, "frame":content}

def test_import_dedupe_and_utc(tmp_path):
    source = write(tmp_path, [
        record("2026-10-14T00:00:02Z", frame(3, 3.4)),
        record("2026-10-14T00:00:01+00:00", frame(3, 3.4)),
        record("2026-10-14T00:00:03Z", frame(4, 1.2)),
        record("2026-10-14T00:00:04Z", frame(5, 50, "OnTick")),
    ])
    dest = tmp_path / "result.csv"
    summary = import_jsonl(source, dest)
    rows = list(csv.DictReader(dest.open()))
    assert summary["unique_rounds"] == 2
    assert [r["round_id"] for r in rows] == ["3", "4"]
    assert rows[0]["received_at"] == "2026-10-14T00:00:01+00:00"

def test_reject_conflict_before_writing(tmp_path):
    source = write(tmp_path, [
        record("2026-10-14T00:00:01Z", frame(3, 2)),
        record("2026-10-14T00:00:02Z", frame(3, 3)),
    ])
    out = tmp_path / "result.csv"
    with pytest.raises(ValueError, match="Conflicting"):
        import_jsonl(source, out)
    assert not out.exists()

def test_reject_naive_time_and_bad_shape(tmp_path):
    with pytest.raises(ValueError, match="timezone"):
        normalize_timestamp("2026-10-14T12:00:00")
    source = write(tmp_path, [{"received_at":"2026-10-14T00:00:00Z", "token":"secret", "frame":frame()}])
    with pytest.raises(ValueError, match="schema"):
        import_jsonl(source, tmp_path / "out.csv")

def test_no_results(tmp_path):
    source = write(tmp_path, [record("2026-10-14T00:00:00Z", frame(target="OnTick"))])
    with pytest.raises(ValueError, match="No OnCrash"):
        import_jsonl(source, tmp_path / "result.csv")
