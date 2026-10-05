# Architecture

AEW is intentionally small and auditable. `aew/model.py` contains the closed world, agents, strategies, inheritance/mutation, scarcity, bilateral exchange, production, reproduction and bankruptcy/death. `aew/__main__.py` provides reproducible command-line runs and a lightweight textual dashboard. Snapshots are plain JSON.

## Safety architecture
The simulation has no network client, browser automation, credential handling, brokerage integration, payment integration, exploit logic or self-propagation. All assets and transactions exist only in Python memory and exported simulation snapshots.
