"""Conservative assessment of model improvement over a baseline.

Uses chronological per-round squared-loss differences and a moving-block bootstrap.
A CI crossing zero is inconclusive; even a positive CI is not proof of future profits.
"""
from __future__ import annotations
from math import isfinite
import random

def block_bootstrap_ci(differences: list[float], *, block_size: int = 20,
                       replications: int = 2000, seed: int = 2026,
                       alpha: float = 0.05) -> dict:
    n = len(differences)
    if n < 60 or block_size < 1 or block_size > n or replications < 100:
        raise ValueError("Need at least 60 observations and 100 replications")
    if not 0 < alpha < 1 or any(not isfinite(x) or abs(x) > 1 for x in differences):
        raise ValueError("Invalid loss differences or alpha")
    rng = random.Random(seed)
    estimates = []
    for _ in range(replications):
        sample = []
        while len(sample) < n:
            start = rng.randrange(n - block_size + 1)
            sample.extend(differences[start:start + block_size])
        estimates.append(sum(sample[:n]) / n)
    estimates.sort()
    lo = estimates[int(alpha/2 * replications)]
    hi = estimates[min(replications-1,int((1-alpha/2)*replications))]
    effect = sum(differences) / n
    return {"rounds": n, "mean_brier_improvement": effect,
            "ci_lower": lo, "ci_upper": hi,
            "conclusion": "inconclusive" if lo <= 0 <= hi else
            "positive_in_sample_evidence_only" if lo > 0 else "model_worse"}
