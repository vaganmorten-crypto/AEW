"""Bounded AEW load benchmark: wall time, peak RSS, population growth."""
import argparse
import csv
import json
import os
import resource
import sys
import time
from pathlib import Path
from aew.simulation import World
from aew.diagnostics import diagnose


def rss_mib():
    # Linux ru_maxrss is KiB; GitHub's ubuntu runner uses Linux.
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024


def benchmark(agents, ticks, seed=42, group="A"):
    started = time.perf_counter()
    world = World(agents=agents, seed=seed, group=group)
    peak = agents
    checkpoints = [{"tick": 0, "population": agents}]
    interval = max(1, ticks // 10)
    for i in range(ticks):
        world.step()
        current = world.history[-1]["population"]
        peak = max(peak, current)
        if (i + 1) % interval == 0 or i + 1 == ticks:
            checkpoints.append({"tick": i + 1, "population": current})
    d = diagnose(world)
    return {
        "agents": agents, "ticks": ticks, "seed": seed, "group": group,
        "elapsed_seconds": round(time.perf_counter() - started, 3),
        "peak_rss_mib": round(rss_mib(), 2),
        "final_population": d["living"],
        "peak_population": peak,
        "population_growth": d["living"] - agents,
        "births": d["births"], "deaths": d["deaths"],
        "max_generation": d["max_generation"],
        "checkpoints": checkpoints,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sizes", nargs="+", type=int, default=[1000, 5000, 10000])
    parser.add_argument("--ticks", type=int, default=100)
    parser.add_argument("--out", default="load-results")
    args = parser.parse_args()
    if args.ticks < 1 or any(n < 2 for n in args.sizes):
        parser.error("ticks must be >= 1 and sizes >= 2")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for n in args.sizes:
        row = benchmark(n, args.ticks)
        rows.append(row)
        (out / f"load_{n}.json").write_text(json.dumps(row, indent=2) + "\n")
        print(json.dumps({k: v for k, v in row.items() if k != "checkpoints"}), flush=True)
    fields = [k for k in rows[0] if k != "checkpoints"]
    with (out / "load_summary.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows([{k: r[k] for k in fields} for r in rows])


if __name__ == "__main__":
    main()
