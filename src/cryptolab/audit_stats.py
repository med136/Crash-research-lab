"""Distribution-free descriptive checks for paired, chronological paper backtests.

These statistics are *not* prospective evidence once researchers have examined
or tuned against the same historical series. Zero real orders / API credentials.
"""
from __future__ import annotations
from math import comb, isfinite
from random import Random
from statistics import mean, median


def paired_audit(folds: list[dict], *, bootstrap_samples: int = 10000, seed: int = 136) -> dict:
    """Compare Volatility Trend vs passive in the *same* out-of-sample windows.

    Bootstrap assumes exchangeable non-overlapping windows; market regimes can
    break this assumption. Sign-test probabilities are descriptive, not a
    p-hacked trading signal.
    """
    if not 2 <= len(folds) <= 10000:
        raise ValueError("Need at least two paired windows")
    if not 100 <= bootstrap_samples <= 100000:
        raise ValueError("Bootstrap sample count out of range")
    if any(not all(isfinite(float(f[k]["return_pct"])) for k in ("voltrend", "passive")) for f in folds):
        raise ValueError("Non-finite return")
    delta = [float(f["voltrend"]["return_pct"]) - float(f["passive"]["return_pct"]) for f in folds]
    ddraw = [float(f["voltrend"]["max_drawdown_pct"]) - float(f["passive"]["max_drawdown_pct"]) for f in folds]
    winners = sum(x > 0 for x in delta)
    losers = sum(x < 0 for x in delta)
    non_ties = winners + losers
    # Two-sided exact binomial sign test, conditional on non-tied windows.
    p = min(1.0, 2 * sum(comb(non_ties, j) for j in range(min(winners, losers)+1)) / 2**non_ties) if non_ties else 1.0
    rng = Random(seed)
    boot_means = sorted(mean(rng.choices(delta, k=len(delta))) for _ in range(bootstrap_samples))
    return {
        "folds":len(delta),
        "mean_excess_return_pp":round(mean(delta),6),
        "median_excess_return_pp":round(median(delta),6),
        "worst_excess_return_pp":round(min(delta),6),
        "wins":winners,"losses":losers,"ties":len(delta)-non_ties,
        "exact_two_sided_sign_p":round(p,6),
        "bootstrap_mean_excess_95pct_pp":[round(boot_means[int(.025*(len(boot_means)-1))],6),round(boot_means[int(.975*(len(boot_means)-1))],6)],
        "average_max_drawdown_improvement_pp":round(mean(ddraw),6),
        "is_prospective_evidence":False,
        "conclusion":"DESCRIPTIVE_ONLY: prior BTC model selection reused these dates; p-values do not validate future alpha.",
    }


def cost_scenarios(candles: list[dict], *, first: int = 900, days: int = 180, target: float = .6) -> dict:
    """Paired windows through the same simulator, with explicit adverse costs."""
    from .paired import paired_windows
    matrix = {
        "base":(.001,.0005),
        "double_cost":(.002,.001),
        "high_slippage":(.001,.003),
    }
    report={}
    for label,(fee,slippage) in matrix.items():
        paired=paired_windows(candles,first=first,days=days,target=target,fee=fee,slippage=slippage)
        report[label]={
            "fee":fee,"slippage":slippage,
            "strategy_vs_passive":paired_audit(paired["folds"],bootstrap_samples=1000),
            "allocation_controls":paired["summary"],
        }
    return {
        "scenarios":report,
        "decision":"NO_REAL_ORDERS",
        "note":"Same researched history, not clean holdout. Synthetic quote execution and third-party data need independent verification.",
    }
