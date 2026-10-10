# AEW 0.5.0 development — reproduction experiments

**Status: experimental, not released.** The canonical Python engine is `aew/simulation.py`. The default branch still has a 0.3.0 engine and a separately authored 0.4.0 browser observatory. These are not evidence that the 0.5.0 experiments have been implemented or measured.

The 0.5.0 development line will compare five reproduction mechanisms: A simple copying/mutation; B function duplication; C heritable error-checking/repair; D cloning and multi-parent recombination; E all mechanisms available. Each arm must run 600 founders, 10,000 ticks and 30 deterministic seeds, with recorded ancestry, population, economic resources, mutation and reproduction counts, and extinction times. All arms must share the same environmental assumptions and seeds. No mechanism is declared superior without measured results.

**Known baseline limitation:** `aew/simulation.py` currently imposes `capacity=max(0,200-len(self.living))`, limiting births; this must be removed or replaced with explicit resource competition before the experiment. The current Python engine supports only asexual mutated offspring. The HTML dashboard uses separate 0.4.0 data; it must not be presented as live output from the Python engine.

## Existing CLI

```bash
python -m pip install -r requirements.txt
python -m aew run --ticks 100 --agents 30 --seed 42 --out aew_snapshot.json
```

## Tests

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

Do not tag or publish 0.5.0 as stable until the new reproduction engine, tests, 150 runs, generated observatory data and GitHub Pages checks pass.
