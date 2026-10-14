import json
import pytest
from crashlab.timing_audit import audit_events

def write(tmp_path, entries):
    path=tmp_path/"events.jsonl"
    path.write_text("".join(json.dumps(x)+"\n" for x in entries),encoding="utf-8")
    return path

def event(round_id, kind, timestamp):
    return {"round_id":round_id,"event":kind,"received_at":timestamp}

def test_normal_timing(tmp_path):
    path=write(tmp_path,[event("a","OnStart","2026-10-14T00:00:00Z"),event("a","OnCrash","2026-10-14T00:00:03Z")])
    result=audit_events(path)
    assert result["rounds_with_both"]==1
    assert result["negative_start_crash_intervals"]==0

def test_reordered_event_is_flagged(tmp_path):
    path=write(tmp_path,[event(1,"OnCrash","2026-10-14T00:00:00Z"),event(1,"OnStart","2026-10-14T00:00:02Z")])
    assert audit_events(path)["negative_start_crash_intervals"]==1

def test_rejects_secret_fields(tmp_path):
    path=write(tmp_path,[{"round_id":1,"event":"OnStart","received_at":"2026-10-14T00:00:00Z","token":"private"}])
    with pytest.raises(ValueError,match="schema"):
        audit_events(path)

def test_empty_stream(tmp_path):
    with pytest.raises(ValueError,match="Empty"):
        audit_events(write(tmp_path,[]))
