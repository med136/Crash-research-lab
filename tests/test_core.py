import math
import pytest
from crashlab.core import analyze, read_csv, simulate, brier, lag1_binary_corr

def test_simulation_reproducible():
    assert simulate(30, 42) == simulate(30, 42)
    assert all(v >= 1 for v in simulate(30))

def test_analysis_is_chronological_and_consistent():
    values = simulate(200, 7)
    result = analyze(values)
    assert result["train_n"] == 140
    assert result["test_n"] == 60
    assert math.isclose(result["brier_improvement"], result["baseline_brier"] - result["model_brier"])

def test_holdout_perturbation_does_not_change_frozen_training_forecast():
    values = simulate(100, 5)
    a = analyze(values)
    b = analyze(values[:70] + [50.0]*30)
    assert a["train_event_rate"] == b["train_event_rate"]
    assert a["train_lag1_correlation"] == b["train_lag1_correlation"]

def test_bad_inputs(tmp_path):
    path = tmp_path / "data.csv"
    path.write_text("round_id,multiplier\na,1.3\na,2.5\n")
    with pytest.raises(ValueError, match="duplicate"):
        read_csv(path)
    with pytest.raises(ValueError):
        analyze([1.5]*12)

def test_metrics():
    assert brier([1, 0], [1, 0]) == 0
    assert lag1_binary_corr([1,1,1,1]) is None
