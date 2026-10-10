# AEW 0.5.0 experiment runner (development)

The main experiment is **not yet scientifically validated**. The A-E operators are
prototypes, and the engine still needs lifecycle and multi-parent resource-accounting
review before full runs. Do not interpret results as evidence of open-ended evolution.

## Correctness and smoke test

```sh
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m aew.experiments --agents 100 --ticks 100 --seeds 2 --out smoke-results
```

## Load testing (explicitly opt in)

```sh
AEW_RUN_LOAD=1 python -m pytest -q tests/test_experiments.py
```

The load profiles include 10,000 agents at 100, 1,000 and 10,000 steps,
plus 50,000 agents at 100 steps. The 10,000-step case may be expensive.
The simulator currently retains agent objects and per-tick history in memory,
and population size is not artificially capped. Monitor memory and runtime.

## Full experiment (only after validation)

```sh
python -m aew.experiments --agents 10000 --ticks 10000 --seeds 30 --groups ABCDE --out results-0.5.0
```

The runner writes one atomic JSON file per group/seed, plus results.csv,
summary.json and config.json. Restart with the same arguments to skip
completed results. Use persistent storage; a CI runner's local filesystem is
temporary. The runner records only aggregate measurements, not every genome.
Seed values are 0-29 and are reused across groups.

No fixed population cap is applied, but finite physical compute and memory
limits still apply. This branch has not run the 150 experiments.
