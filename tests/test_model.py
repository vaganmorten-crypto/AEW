from random import Random
from aew.model import Genome, World

def test_genome_mutation_is_bounded_and_changes_traits():
    g=Genome(.5,.5,180,.04,.2,1.0,.08)
    child=g.mutate(Random(7))
    assert child != g
    assert .01 <= child.risk <= .99
    assert .001 <= child.reproduction_probability <= .35
    assert .05 <= child.offspring_investment <= .60
    assert .25 <= child.resource_consumption <= 2.0

def test_model_exports_canonical_world():
    w=World(10,7); w.run(5)
    assert w.snapshot()["version"]=="0.5.0-experimental"
