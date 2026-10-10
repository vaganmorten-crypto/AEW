"""Reproducible AEW experiment runner. Run: python -m aew.experiments --help."""
import argparse
import csv
import json
import os
import time
from pathlib import Path
from statistics import mean
from aew.simulation import World

FIELDS = ("group", "seed", "initial_agents", "ticks", "final_population",
          "peak_population", "max_generation", "births", "total_cash",
          "total_resource", "elapsed_seconds")


def execute(group, seed, agents, ticks):
    start = time.perf_counter()
    world = World(agents=agents, seed=seed, group=group)
    peak = agents
    for _ in range(ticks):
        world.step()
        # History is already collected by World; do not serialize it per tick.
        peak = max(peak, world.history[-1]["population"])
    living = world.living
    return dict(group=group, seed=seed, initial_agents=agents, ticks=ticks,
                final_population=len(living), peak_population=peak,
                max_generation=max((a.generation for a in world.population), default=0),
                births=world.next_id-agents,
                total_cash=round(sum(a.cash for a in living), 6),
                total_resource=round(sum(a.resource for a in living), 6),
                elapsed_seconds=round(time.perf_counter()-start, 3))


def write_atomic(path, data):
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def run_suite(output, agents=10000, ticks=10000, seeds=30, groups="ABCDE"):
    if agents < 2 or ticks < 0 or seeds < 1:
        raise ValueError("Invalid experiment dimensions")
    if not groups or any(g not in "ABCDE" for g in groups) or len(set(groups)) != len(groups):
        raise ValueError("Groups must be unique letters from ABCDE")
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    config = dict(agents=agents, ticks=ticks, seeds=seeds, groups=groups)
    config_path = output / "config.json"
    if config_path.exists():
        if json.loads(config_path.read_text(encoding="utf-8")) != config:
            raise ValueError("Existing output has different experiment settings")
    else:
        write_atomic(config_path, config)
    for group in groups:
        for seed in range(seeds):
            path = output / f"{group}_{seed:03d}.json"
            if path.exists():
                saved = json.loads(path.read_text(encoding="utf-8"))
                if any(saved[k] != v for k, v in
                       (("group", group), ("seed", seed), ("initial_agents", agents), ("ticks", ticks))):
                    raise ValueError(f"Invalid saved result: {path}")
                continue
            result = execute(group, seed, agents, ticks)
            write_atomic(path, result)
            print(f"{group} seed={seed}: pop={result['final_population']} "
                  f"births={result['births']} elapsed={result['elapsed_seconds']}s", flush=True)
    rows = [json.loads((output / f"{g}_{s:03d}.json").read_text(encoding="utf-8"))
            for g in groups for s in range(seeds)]
    with (output / "results.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    summary = {g: {k: mean(row[k] for row in rows if row["group"] == g)
                   for k in ("final_population", "peak_population", "max_generation",
                             "births", "total_cash", "total_resource", "elapsed_seconds")}
               for g in groups}
    write_atomic(output / "summary.json", summary)
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="experiment-results")
    parser.add_argument("--agents", type=int, default=10000)
    parser.add_argument("--ticks", type=int, default=10000)
    parser.add_argument("--seeds", type=int, default=30)
    parser.add_argument("--groups", default="ABCDE")
    args = parser.parse_args()
    run_suite(args.out, args.agents, args.ticks, args.seeds, args.groups)


if __name__ == "__main__":
    main()
