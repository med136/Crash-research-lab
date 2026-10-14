import pytest
from crashlab.significance import block_bootstrap_ci

def test_zero_difference_is_inconclusive():
    result = block_bootstrap_ci([0.0]*100, replications=100)
    assert result["conclusion"] == "inconclusive"
    assert result["ci_lower"] == result["ci_upper"] == 0.0

def test_always_positive_difference():
    result = block_bootstrap_ci([0.01]*100, replications=100)
    assert result["ci_lower"] > 0
    assert result["conclusion"] == "positive_in_sample_evidence_only"

def test_reproducible_seed():
    x = [0.1 if i % 2 else -0.1 for i in range(100)]
    assert block_bootstrap_ci(x, replications=100) == block_bootstrap_ci(x, replications=100)

def test_invalid_input():
    with pytest.raises(ValueError):
        block_bootstrap_ci([0.1]*10)
    with pytest.raises(ValueError):
        block_bootstrap_ci([2.0]*100)
