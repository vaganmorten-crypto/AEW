# Reproduction discovery — controlled run

Engine branch: `experiment/reproduction-discovery`

Protocol: 100 deterministic seeds (1–100), 60 founders per seed, 3,000 ticks, no founder injection, resurrection, rescue, or extinction protection.

Local controlled run using the branch engine logic after removing the last-agent freeze:

- Seeds with at least one birth: **100/100**
- Seeds reaching generation 3 or later: **83/100**
- Runs extinct by tick 3000: **72/100**
- Mean births per run: **83.38**
- Among runs with survivors, mean survivor reproduction-probability minus founder mean: **+0.00535**

Interpretation: reproduction can emerge and propagate through Gen 1 → Gen 2 → Gen 3 without population rescue. It is not automatically sufficient for persistence: most runs still go extinct. The small positive survivor shift in reproduction probability is compatible with weak selection for higher reproductive propensity in surviving runs, but is not by itself proof of causal selection. Follow-up experiments should measure lineage reproductive success against each inherited trait and compare matched controls.

Important engine correction discovered during this run: the previous `len(living) < 2` early return made the final surviving agent immortal and also prevented it from reproducing. The experiment branch now only stops ecological processing when the population is actually zero.
