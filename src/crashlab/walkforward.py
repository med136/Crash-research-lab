"""Leakage-safe one-step-ahead forecasts for a binary Crash threshold event.

Every prediction at index t uses only observations with indices < t.
No wagering functionality is implemented here.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import sqrt
from .core import brier

@dataclass(frozen=True)
class WalkForwardResult:
    n_train: int
    n_test: int
    threshold: float
    baseline_brier: float
    adaptive_brier: float
    brier_improvement: float
    baseline_accuracy: float
    adaptive_accuracy: float

    def as_dict(self) -> dict:
        return vars(self).copy()

def walk_forward(values: list[float], *, threshold: float = 2.0,
                 train_fraction: float = 0.7, window: int = 30,
                 smoothing: float = 20.0) -> WalkForwardResult:
    """Expanding historical prior vs rolling recent frequency, prequential testing.

    The adaptive model shrinks recent frequency toward a *frozen* training prior.
    Observed test outcomes can update its lag window only AFTER their prediction.
    """
    if len(values) < 40 or threshold <= 1 or not 0 < train_fraction < 1:
        raise ValueError("Invalid dataset size, threshold, or fraction")
    if window < 2 or smoothing < 0:
        raise ValueError("Invalid window or smoothing")
    import math
    if any(not math.isfinite(x) or x < 1 for x in values):
        raise ValueError("Invalid multiplier")
    y = [int(x >= threshold) for x in values]
    cut = int(len(y) * train_fraction)
    if cut < window or cut >= len(y):
        raise ValueError("Need sufficient chronological train and test samples")
    prior = sum(y[:cut]) / cut
    preds_baseline: list[float] = []
    preds_adaptive: list[float] = []
    for t in range(cut, len(y)):
        recent = y[t-window:t]  # contains only outcomes from strictly earlier rounds
        p = (sum(recent) + smoothing * prior) / (len(recent) + smoothing)
        preds_baseline.append(prior)
        preds_adaptive.append(p)
    truth = y[cut:]
    baseline = brier(truth, preds_baseline)
    adaptive = brier(truth, preds_adaptive)
    return WalkForwardResult(
        n_train=cut, n_test=len(truth), threshold=threshold,
        baseline_brier=baseline, adaptive_brier=adaptive,
        brier_improvement=baseline-adaptive,
        baseline_accuracy=sum((p>=0.5)==bool(v) for p,v in zip(preds_baseline,truth))/len(truth),
        adaptive_accuracy=sum((p>=0.5)==bool(v) for p,v in zip(preds_adaptive,truth))/len(truth),
    )
