from crashlab.core import simulate
from crashlab.walkforward import walk_forward
import pytest

def test_reproducibility():
    values = simulate(1000, seed=2026)
    assert walk_forward(values) == walk_forward(values)

def test_constant_series():
    result = walk_forward([1.01] * 100, window=10)
    assert result.baseline_brier == 0
    assert result.adaptive_brier == 0

def test_invalid_arguments():
    with pytest.raises(ValueError):
        walk_forward([1.0] * 10)
    with pytest.raises(ValueError):
        walk_forward([1.0] * 100, window=200)
    with pytest.raises(ValueError):
        walk_forward([1.0] * 100, smoothing=-1)

def test_future_outcomes_do_not_change_training_prior():
    series = simulate(200, seed=12)
    # Only the final test outcome is modified. Baseline predictions are frozen.
    first = walk_forward(series, window=10)
    changed = series[:]
    changed[-1] = 1.0 if series[-1] >= 2 else 10.0
    second = walk_forward(changed, window=10)
    assert first.n_train == second.n_train
    assert first.baseline_brier != second.baseline_brier
