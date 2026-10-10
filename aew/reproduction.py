"""Experimental hereditary operators for AEW 0.5.0.

No global population cap is imposed by these operators.
"""
from dataclasses import dataclass, replace
from random import Random
from typing import Sequence

FIELDS = ("risk", "trade_rate", "reproduction_threshold",
          "reproduction_probability", "offspring_investment",
          "resource_consumption", "mutation_rate")


@dataclass(frozen=True)
class ReproductionConfig:
    mode: str
    repair_probability: float = 0.9
    duplication_probability: float = 0.1

    def __post_init__(self):
        if self.mode not in ("A", "B", "C", "D", "E"):
            raise ValueError("Unknown experimental group")
        if not 0 <= self.repair_probability <= 1:
            raise ValueError("Invalid repair probability")
        if not 0 <= self.duplication_probability <= 1:
            raise ValueError("Invalid duplication probability")


def offspring_genome(parents: Sequence, rng: Random, config: ReproductionConfig):
    """Return a child genome without modifying any parent.

    A: mutation; B: duplication; C: mutation with probabilistic repair;
    D: multi-parent recombination; E: all mechanisms.
    The existing Genome is the base representation; duplication is modeled
    as an extra independently mutable copy of a gene, resolved into the
    expressed genome. This is not yet a variable-length executable genome.
    """
    if not parents:
        raise ValueError("At least one parent required")
    if config.mode == "D" and len(parents) < 2:
        raise ValueError("Recombination requires at least two parents")
    if config.mode in ("D", "E") and len(parents) > 1:
        values = {field: getattr(rng.choice(parents), field) for field in FIELDS}
        base = replace(parents[0], **values)
    else:
        base = replace(parents[0])
    child = base.mutate(rng)
    if config.mode in ("B", "E"):
        for field in FIELDS:
            if rng.random() < config.duplication_probability:
                # Preserve an unmutated functional copy at the expressed locus.
                child = replace(child, **{field: getattr(base, field)})
    if config.mode in ("C", "E"):
        for field in FIELDS:
            if rng.random() < config.repair_probability:
                child = replace(child, **{field: getattr(base, field)})
    return child
