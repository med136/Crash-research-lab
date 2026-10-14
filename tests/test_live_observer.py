import json
import pytest
from crashlab.live_observer import observe_line

def test_final_event_is_marked_post_result():
    wire = json.dumps({"type":1,"target":"OnCrash","arguments":[{"l":55,"f":2.75}]}) + "\x1e"
    event = observe_line(json.dumps({"received_at":"2026-10-14T02:00:00Z","frame":wire}))[0]
    assert event == {"received_at":"2026-10-14T02:00:00+00:00","round_id":"55",
                     "multiplier":2.75,"event":"final_result"}

def test_ticks_cannot_be_misclassified_as_final_results():
    wire = json.dumps({"type":1,"target":"OnTick","arguments":[{"l":55,"f":100}]}) + "\x1e"
    assert observe_line(json.dumps({"received_at":"2026-10-14T02:00:00Z","frame":wire})) == []

def test_secret_fields_rejected():
    with pytest.raises(ValueError):
        observe_line(json.dumps({"received_at":"2026-10-14T02:00:00Z","frame":"{}","token":"secret"}))
