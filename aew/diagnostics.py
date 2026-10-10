"""Read-only diagnostics for AEW experimental worlds.

Does not consume random numbers or change simulation decisions.
"""
from collections import Counter
from statistics import mean


def diagnose(world):
    living = world.living
    counts = Counter(e["type"] for e in world.events)
    eligible_cash = 0
    eligible_resources = 0
    eligible_both = 0
    for agent in living:
        threshold = agent.genome.reproduction_threshold
        resource_threshold = max(2.0, threshold / world.price * 0.55)
        cash_ok = agent.cash >= threshold
        resource_ok = agent.resource >= resource_threshold
        eligible_cash += cash_ok
        eligible_resources += resource_ok
        eligible_both += cash_ok and resource_ok
    generations = Counter(a.generation for a in living)
    return {
        "tick": world.tick,
        "group": world.config.mode,
        "seed": world.seed,
        "living": len(living),
        "total_agents_created": world.next_id,
        "deaths": sum(not a.alive for a in world.population),
        "births": sum(a.parent is not None for a in world.population),
        "eligible_cash": eligible_cash,
        "eligible_resources": eligible_resources,
        "eligible_both": eligible_both,
        "blocked_cash": len(living) - eligible_cash,
        "blocked_resources": len(living) - eligible_resources,
        "max_generation": max(generations, default=0),
        "generation_distribution": dict(sorted(generations.items())),
        "total_cash_living": round(sum(a.cash for a in living), 4),
        "total_resources_living": round(sum(a.resource for a in living), 4),
        "mean_cash_living": round(mean(a.cash for a in living), 4) if living else 0.0,
        "recent_event_counts": dict(sorted(counts.items())),
        "events_retained": len(world.events),
        "event_log_truncated": len(world.events) >= 2000,
    }
