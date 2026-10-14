# Crash Research Lab

Independent reproducible research into whether past Crash-game multipliers provide useful **out-of-sample** predictive information. This is not a live multiplier oracle, a guaranteed predictor, or a wagering bot.

## First experiment

The repository contains a CSV validator, synthetic independent multiplier generator, baseline statistical model and a chronological **walk-forward** evaluator in `src/crashlab/walkforward.py`.

For each held-out round `t`, the model sees only observations earlier than `t`. The baseline is the training-set event frequency, while the adaptive model uses the trailing `window` results shrunk toward that fixed baseline. Both are scored on the identical later rounds with Brier scores. A smaller Brier score is better.

## Reproduce

```bash
python -m pip install -e '.[dev]'
python -m crashlab.cli simulate --rows 2000 --output data/synthetic.csv
python -m crashlab.cli analyze --input data/synthetic.csv --output report.json
python -c "from crashlab.core import read_csv; from crashlab.walkforward import walk_forward; print(walk_forward(read_csv('data/synthetic.csv')).as_dict())"
pytest -q
```

Expected CSV columns: `round_id,multiplier`, ordered oldest to newest with unique round IDs. Do not upload identifiable/private or unauthorized datasets. No real 1xBet data is included or yet evaluated.

## Interpretation

This synthetic model is **not** evidence about how 1xBet generates its outcomes. A positive score difference on one holdout is not evidence of sustained exploitable predictability; it would need multiple truly prospective datasets, confidence intervals, leak checks and replication. No bets, automated cashout, scraping behind access controls or attempts to recover private server seeds are implemented.
