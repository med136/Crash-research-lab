import json
import pytest
from crashlab.signalr import parse_frame, parse_unique_frames

def msg(target, args):
    return json.dumps({"type": 1, "target": target, "arguments": args}) + "\x1e"

def test_parse_result_only():
    wire = msg("OnCrash", [{"l": 105, "f": 2.35, "ts": "2026-10-14T00:00:00Z"}])
    assert [(x.round_id, x.multiplier) for x in parse_frame(wire)] == [("105", 2.35)]

def test_ignores_unknown_and_precrash_events():
    assert parse_frame(msg("OnTick", [{"l": 106, "f": 12.0}])) == []
    assert parse_frame("{}\x1e" + "not json\x1e") == []

def test_multiple_signalr_messages_and_duplicates():
    a = msg("OnCrash", [{"l": 1, "f": 2.5}])
    b = msg("OnCrash", [{"l": 2, "f": 3.5}])
    assert len(parse_frame(a + b)) == 2
    assert len(parse_unique_frames([a, a, b])) == 2

def test_conflicting_outcomes_rejected():
    with pytest.raises(ValueError, match="Conflicting"):
        parse_unique_frames([
            msg("OnCrash", [{"l": 1, "f": 2.5}]),
            msg("OnCrash", [{"l": 1, "f": 3.5}]),
        ])

@pytest.mark.parametrize("value", [0, -1, "NaN", "Infinity", None, {}, True])
def test_invalid_multipliers(value):
    assert parse_frame(msg("OnCrash", [{"l": 1, "f": value}])) == []

def test_rejects_oversized_frames():
    with pytest.raises(ValueError):
        parse_frame("x" * 2_000_001)
