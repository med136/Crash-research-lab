"""Dependency-free baseline analysis with chronological train/test separation."""
from __future__ import annotations
import csv
import math
import random
from pathlib import Path

def read_csv(path: str | Path) -> list[float]:
    values: list[float] = []
    ids: set[str] = set()
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or not {"round_id", "multiplier"}.issubset(reader.fieldnames):
            raise ValueError("Expected round_id and multiplier columns")
        for row in reader:
            rid = row["round_id"].strip()
            if not rid or rid in ids:
                raise ValueError("Missing or duplicate round_id")
            ids.add(rid)
            try:
                x = float(row["multiplier"])
            except (TypeError, ValueError) as exc:
                raise ValueError(f"Invalid multiplier for {rid}") from exc
            if not math.isfinite(x) or x < 1:
                raise ValueError(f"Invalid multiplier for {rid}: {x}")
            values.append(x)
    if not values:
        raise ValueError("Empty dataset")
    return values

def simulate(n: int, seed: int = 42, edge: float = 0.03) -> list[float]:
    """Illustrative independent toy distribution, NOT any provider's verified algorithm."""
    if n < 1 or not 0 <= edge < 1:
        raise ValueError("Invalid n or edge")
    rng = random.Random(seed)
    return [max(1.0, (1.0 - edge) / (1.0 - rng.random())) for _ in range(n)]

def brier(actual: list[int], predicted: list[float]) -> float:
    if not actual or len(actual) != len(predicted):
        raise ValueError("Mismatched or empty predictions")
    return sum((y - p) ** 2 for y, p in zip(actual, predicted)) / len(actual)

def logloss(actual: list[int], predicted: list[float]) -> float:
    if not actual or len(actual) != len(predicted):
        raise ValueError("Mismatched or empty predictions")
    eps = 1e-12
    return -sum(y * math.log(max(eps, min(1-eps, p))) + (1-y) * math.log(max(eps, min(1-eps, 1-p))) for y, p in zip(actual, predicted)) / len(actual)

def lag1_binary_corr(x: list[int]) -> float | None:
    if len(x) < 3:
        return None
    a, b = x[:-1], x[1:]
    ma, mb = sum(a)/len(a), sum(b)/len(b)
    va = sum((v-ma)**2 for v in a)
    vb = sum((v-mb)**2 for v in b)
    if not va or not vb:
        return None
    return sum((u-ma)*(v-mb) for u, v in zip(a,b))/math.sqrt(va*vb)

def analyze(values: list[float], threshold: float = 2.0, train_fraction: float = 0.7, window: int = 30) -> dict:
    if threshold <= 1 or not 0 < train_fraction < 1 or window < 2 or len(values) < 30:
        raise ValueError("Requires threshold >1, 0<train_fraction<1, window>=2, at least 30 rounds")
    if any(not math.isfinite(v) or v < 1 for v in values):
        raise ValueError("Invalid multipliers")
    y = [int(v >= threshold) for v in values]
    cut = int(len(y)*train_fraction)
    train, test = y[:cut], y[cut:]
    if len(train) < window or not test:
        raise ValueError("Insufficient training or test data")
    prior = sum(train)/len(train)
    recent = sum(train[-window:])/window
    baseline_predictions = [prior]*len(test)
    model_predictions = [recent]*len(test)
    return {
        "n": len(values), "train_n": len(train), "test_n": len(test),
        "threshold": threshold, "window": window,
        "train_event_rate": prior, "test_event_rate": sum(test)/len(test),
        "baseline_brier": brier(test, baseline_predictions),
        "model_brier": brier(test, model_predictions),
        "baseline_logloss": logloss(test, baseline_predictions),
        "model_logloss": logloss(test, model_predictions),
        "train_lag1_correlation": lag1_binary_corr(train),
        "brier_improvement": brier(test, baseline_predictions)-brier(test, model_predictions),
        "interpretation": "Exploratory only. Positive improvement on one test is not proof of predictive power."
    }
