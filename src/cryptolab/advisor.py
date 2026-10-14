"""Transparent, CAUSAL strategy advisor for paper-only research.

A regime-aware multi-signal voting model; NOT a fitted ML model, not a calibrated
probability, not a profitable-strategy claim, and never an execution engine.
"""
from __future__ import annotations
import math
from statistics import mean

HISTORY=201

def evaluate_closes(closes: list[float]) -> dict:
    if len(closes)<HISTORY:
        raise ValueError("Need 201 completed daily closes")
    p=[float(x) for x in closes[-HISTORY:]]
    if not all(math.isfinite(x) and x>0 for x in p):
        raise ValueError("Invalid historical prices")
    now=p[-1]
    ma20=mean(p[-20:])
    ma60=mean(p[-60:])
    ma200=mean(p[-200:])
    momentum30=now/p[-31]-1
    # Prior twenty sessions only; today does not alter the breakout boundary.
    breakout=now>max(p[-21:-1])
    r=[math.log(p[i]/p[i-1]) for i in range(len(p)-30,len(p))]
    mu=mean(r)
    vol=math.sqrt(365*mean([(x-mu)**2 for x in r]))
    trend=now>ma200
    trend_cross=ma20>ma60
    positive_momentum=momentum30>0
    high_volatility=vol>.95
    votes=sum([trend,trend_cross,positive_momentum,breakout])
    # Score counts *votes*, NOT estimated win probability.
    score=25*votes
    # Hard cash regime; a weak pattern cannot override 200-day downtrend.
    allowed=trend and votes>=3 and not high_volatility
    risk_budget=min(.60,.30/max(vol,.05)) if allowed else 0.
    mode=("PAPER_LONG_CANDIDATE" if allowed else "CASH_OR_RESEARCH")
    return {
        "mode":mode,"score_votes":score,"votes":votes,
        "max_exposure":round(risk_budget,6),
        "regime":"high_volatility" if high_volatility else ("uptrend" if trend else "downtrend"),
        "risk_flags":["HIGH_REALIZED_VOLATILITY"] if high_volatility else [],
        "signals":{"above_sma200":trend,"sma20_above_sma60":trend_cross,
                   "momentum30_positive":positive_momentum,"breakout20":breakout},
        "indicators":{"last_close":round(now,6),"sma200":round(ma200,6),
                      "momentum30_pct":round(momentum30*100,4),
                      "annualized_volatility_pct":round(vol*100,4)},
        "status":"UNVALIDATED_RESEARCH_ONLY",
        "note":"Vote score is not a trained AI, probability, investment recommendation or execution command.",
    }
