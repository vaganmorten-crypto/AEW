# AEW 0.3.0 — Open-Ended Economic Evolution Laboratory (development)

AEW is a sandboxed artificial-life economy. Version 0.3.0 adds observability: structured trade/birth/bankruptcy events plus a responsive browser observatory intended for desktop and phone.

## Mobile observatory

Open `docs/index.html` locally, or publish the `docs/` folder with GitHub Pages. The browser dashboard runs a deterministic virtual AEW economy entirely in the browser and shows:

- live tick, population, virtual price and event count
- population/price chart
- trade, birth and bankruptcy event stream
- top-agent table
- per-agent lineage/details
- run/pause, single-step and 1x/10x/100x controls

No broker APIs, credentials, real money, external trading, network penetration or autonomous access to external systems are used.

## Python simulator

```bash
python -m pip install -r requirements.txt
python -m aew run --ticks 100 --agents 30 --seed 42 --out aew_snapshot.json
python -m aew dashboard aew_snapshot.json --out aew_dashboard.png
```

Snapshots now include an `events` array suitable for analysis and future server-side streaming.

## Tests

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

This branch is the v0.3.0 development line; v0.2.1 remains the stable baseline until tests and review are complete.
