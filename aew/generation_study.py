"""Longer multi-seed generational survival study for the abundant resource model."""
import argparse
import csv
import json
import time
from collections import Counter
from pathlib import Path
from aew.simulation import World


def experiment(agents, ticks, seed):
    world = World(agents=agents, seed=seed, group="A", resource_model="abundant")
    started = time.perf_counter()
    peak = agents
    interval = max(1, ticks // 20)
    checkpoints = []
    for i in range(ticks):
        world.step()
        living = world.living
        peak = max(peak, len(living))
        if (i + 1) % interval == 0 or i + 1 == ticks:
            generations = Counter(a.generation for a in living)
            checkpoints.append({
                "tick": world.tick, "population": len(living),
                "living_generations": dict(sorted(generations.items())),
                "max_living_generation": max(generations, default=0),
                "births_cumulative": world.next_id - agents,
            })
    living = world.living
    distribution = Counter(a.generation for a in living)
    return {
        "agents": agents, "ticks": ticks, "seed": seed, "model": "abundant",
        "final_population": len(living), "peak_population": peak,
        "births": world.next_id - agents,
        "deaths": sum(not a.alive for a in world.population),
        "max_generation_ever": max((a.generation for a in world.population), default=0),
        "max_living_generation": max(distribution, default=0),
        "living_gen2_plus": sum(n for g, n in distribution.items() if g >= 2),
        "living_gen3_plus": sum(n for g, n in distribution.items() if g >= 3),
        "living_generations": dict(sorted(distribution.items())),
        "seconds": round(time.perf_counter() - started, 3),
        "checkpoints": checkpoints,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--sizes", nargs="+", type=int, default=[1000, 5000, 10000])
    p.add_argument("--seeds", nargs="+", type=int, default=[42, 43, 44])
    p.add_argument("--ticks", type=int, default=1000)
    p.add_argument("--out", default="generation-results")
    a = p.parse_args()
    if a.ticks < 1 or any(n < 2 for n in a.sizes):
        p.error("invalid dimensions")
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for agents in a.sizes:
        for seed in a.seeds:
            result = experiment(agents, a.ticks, seed)
            rows.append(result)
            (out / f"generations_{agents}_{seed}.json").write_text(json.dumps(result, indent=2) + "\n")
            print(json.dumps({k: v for k, v in result.items() if k not in ("checkpoints", "living_generations")}), flush=True)
    fields = [k for k in rows[0] if k not in ("checkpoints", "living_generations")]
    with (out / "summary.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows([{k: r[k] for k in fields} for r in rows])


if __name__ == "__main__":
    main()
