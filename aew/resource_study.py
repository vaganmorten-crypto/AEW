"""Controlled resource-model comparison, independent of the 150-run suite."""
import argparse
import csv
import json
import resource
import time
from pathlib import Path
from aew.simulation import World
from aew.diagnostics import diagnose


def run_case(model, agents, ticks, seed):
    start = time.perf_counter()
    world = World(agents=agents, seed=seed, group="A", resource_model=model)
    peak = agents
    checkpoints = []
    interval = max(1, ticks // 10)
    for step in range(ticks):
        world.step()
        peak = max(peak, world.history[-1]["population"])
        if (step + 1) % interval == 0 or step + 1 == ticks:
            d = diagnose(world)
            checkpoints.append({
                "tick": world.tick, "population": d["living"],
                "eligible_both": d["eligible_both"],
                "blocked_cash": d["blocked_cash"],
                "blocked_resources": d["blocked_resources"],
                "births": d["births"], "deaths": d["deaths"],
            })
    d = diagnose(world)
    return {
        "model": model, "agents": agents, "ticks": ticks, "seed": seed,
        "seconds": round(time.perf_counter() - start, 4),
        "peak_rss_mib": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 2),
        "final_population": d["living"], "peak_population": peak,
        "births": d["births"], "deaths": d["deaths"],
        "max_generation": d["max_generation"],
        "eligible_both": d["eligible_both"],
        "blocked_cash": d["blocked_cash"],
        "blocked_resources": d["blocked_resources"],
        "checkpoints": checkpoints,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--sizes", nargs="+", type=int, default=[1000, 5000, 10000])
    p.add_argument("--ticks", type=int, default=100)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--out", default="resource-results")
    a = p.parse_args()
    if a.ticks < 1 or any(n < 2 for n in a.sizes):
        p.error("invalid sizes or ticks")
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for model in ("baseline", "scaled", "abundant"):
        for size in a.sizes:
            result = run_case(model, size, a.ticks, a.seed)
            rows.append(result)
            (out / f"{model}_{size}.json").write_text(json.dumps(result, indent=2) + "\n")
            print(json.dumps({k: v for k, v in result.items() if k != "checkpoints"}), flush=True)
    fields = [k for k in rows[0] if k != "checkpoints"]
    with (out / "summary.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows([{k: r[k] for k in fields} for r in rows])


if __name__ == "__main__":
    main()
