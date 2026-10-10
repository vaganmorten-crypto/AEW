"""AEW 0.5.0 experimental reproduction operators.

The current AEW genome is a seven-parameter dataclass, not executable Tierra
bytecode. These operators act on the real parameter genome; they do not claim
to implement instruction-level digital organisms.
"""
from dataclasses import asdict, fields
from random import Random
from .simulation import Genome, clamp

GROUPS = ("A", "B", "C", "D", "E")

def reproduce(parent: Genome, rng: Random, group: str,
              partners: tuple[Genome, ...] = ()) -> Genome:
    """Create a fresh child genome without mutating any parent."""
    if group not in GROUPS:
        raise ValueError("Unknown experimental group")
    base = Genome(**asdict(parent))
    if group in ("D", "E") and partners:
        donors = (parent,) + partners
        base = Genome(**{f.name: getattr(rng.choice(donors), f.name)
                         for f in fields(Genome)})
    if group in ("B", "E"):
        # Preserve an unmutated donor for one locus; model of redundancy
        # only. True gene duplication needs a variable-length genome.
        protected = rng.choice(fields(Genome)).name
        child = base.mutate(rng)
        setattr(child, protected, getattr(base, protected))
        return child
    if group == "C":
        # Evolvable copying fidelity: the parent's mutation_rate is heritable.
        # A copying-error repair event restores the complete pre-mutation
        # genome. This costs no resources here; see experiment limitations.
        child = base.mutate(rng)
        fidelity = clamp(1.0 - base.mutation_rate, 0.0, 1.0)
        return base if rng.random() < fidelity else child
    if group == "E":
        return base.mutate(rng)
    return base.mutate(rng)
