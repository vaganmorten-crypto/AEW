# AEW 0.4.0 cognitive-evolution branch

This branch experiments with heritable cognitive architecture rather than hard-coding a profitable strategy.

## Added
- Genome v2: learning rate, memory span, planning horizon, exploration, information budget and mutable decision-network structure.
- CognitiveAgent: observation, bounded memory, prediction/action score and lifetime learning.
- 1000-agent default founder population (10x the old 100-agent default).
- MarketDataFeed: read-only time-series input. It intentionally exposes no order/broker method.
- Agent Inspector data: lineage, full genome, memory use, decision score, prediction error and architecture size.
- Complexity cost: larger cognitive structures consume virtual cash, so intelligence must earn its keep.
- Reproducible Gen 0 -> Gen N experiment runner.

## Safety boundary
External financial data may be transformed into MarketDataFeed frames, but agents can act only inside AEW. Do not add credentials, broker order APIs, money transfer, network exploitation or autonomous external actions.

## Experiment
```bash
python -m aew.experiment --agents 1000 --ticks 500 --seed 42 --out experiment_gen0_genN.json
```
The output records population, maximum generation, cognitive complexity and prediction error over time.
