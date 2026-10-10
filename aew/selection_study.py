"""AEW controlled selection, economic adaptation and 10k-step stability study.

Reports observations only; no survival bonus, artificial births or population floor.
"""
import argparse
import csv
import json
import time
from collections import Counter
from pathlib import Path
from statistics import mean
from aew.simulation import World

MODES = ("normal", "no_mutation", "no_inheritance")
GENES = ("risk", "trade_rate", "reproduction_threshold",
         "reproduction_probability", "offspring_investment", "resource_consumption")


def measures(world):
    living = world.living
    by_generation = {}
    for generation in sorted({a.generation for a in living}):
        members = [a for a in living if a.generation == generation]
        by_generation[str(generation)] = {
            "count": len(members),
            "mean_cash": mean(a.cash for a in members),
            "mean_resources": mean(a.resource for a in members),
            "mean_wealth": mean(a.cash + a.resource * world.price for a in members),
            "genes": {key: mean(getattr(a.genome, key) for a in members) for key in GENES},
        }
    return {
        "tick": world.tick, "population": len(living),
        "births": world.next_id - world.initial_agents,
        "deaths": sum(not a.alive for a in world.population),
        "price": world.price,
        "max_generation_ever": max((a.generation for a in world.population), default=0),
        "gen2_alive": sum(a.generation >= 2 for a in living),
        "gen3_alive": sum(a.generation >= 3 for a in living),
        "generations": by_generation,
        "mean_wealth": mean(a.cash + a.resource * world.price for a in living) if living else 0,
    }


def run(agents, ticks, seed, mode):
    w = World(agents=agents, seed=seed, group="A",
              resource_model="abundant", inheritance_mode=mode)
    checkpoints = [measures(w)]
    started = time.perf_counter()
    interval = max(1, ticks // 20)
    for i in range(ticks):
        w.step()
        if (i + 1) % interval == 0 or i + 1 == ticks:
            checkpoints.append(measures(w))
    end = checkpoints[-1]
    return {
        "mode": mode, "agents": agents, "ticks": ticks, "seed": seed,
        "seconds": round(time.perf_counter() - started, 3),
        "final_population": end["population"], "births": end["births"],
        "deaths": end["deaths"], "max_generation": end["max_generation_ever"],
        "gen2_alive": end["gen2_alive"], "gen3_alive": end["gen3_alive"],
        "mean_wealth": end["mean_wealth"], "checkpoints": checkpoints,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--agents", type=int, default=10000)
    p.add_argument("--ticks", type=int, default=10000)
    p.add_argument("--seeds", nargs="+", type=int, default=[42, 43, 44])
    p.add_argument("--modes", nargs="+", choices=MODES, default=list(MODES))
    p.add_argument("--out", default="selection-results")
    a = p.parse_args()
    if a.agents < 2 or a.ticks < 1:
        p.error("agents >= 2 and ticks >= 1 required")
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for mode in a.modes:
        for seed in a.seeds:
            result = run(a.agents, a.ticks, seed, mode)
            rows.append(result)
            (out / f"{mode}_{seed}.json").write_text(json.dumps(result, indent=2) + "\n")
            print(json.dumps({k: v for k, v in result.items() if k != "checkpoints"}), flush=True)
    keys = [k for k in rows[0] if k != "checkpoints"]
    with (out / "summary.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows([{k: row[k] for k in keys} for row in rows])


if __name__ == "__main__":
    main()
