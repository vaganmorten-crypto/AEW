from random import Random
from aew.simulation import Genome, World

def test_seed_is_deterministic():
    a=World(20,7);b=World(20,7);a.run(100);b.run(100)
    assert a.snapshot()==b.snapshot()

def test_genome_mutation_is_bounded_and_changes_traits():
    g=Genome(.5,.5,130,.05,.2,.8,.08);c=g.mutate(Random(7))
    assert c!=g and .01<=c.risk<=.99 and .001<=c.reproduction_probability<=.40
    assert .05<=c.offspring_investment<=.55 and .20<=c.resource_consumption<=1.8

def test_birth_inherits_mutated_genome_and_generation():
    w=World(2,11);p=w.population[0];p.cash=500;p.resource=100
    p.genome.reproduction_threshold=55;p.genome.reproduction_probability=.40
    for _ in range(100):
        w.step()
        kids=[a for a in w.population if a.parent==p.id]
        if kids:
            c=kids[0];assert c.generation==1;assert c.genome!=p.genome
            assert p.children>=1;assert w.births>=1;return
    raise AssertionError("expected genetically controlled birth")

def test_inspector_reports_lineage():
    w=World(2,19);p=w.population[0];p.cash=500;p.resource=100
    p.genome.reproduction_threshold=55;p.genome.reproduction_probability=.40
    for _ in range(100):
        w.step()
        kids=[a for a in w.population if a.parent==p.id]
        if kids:
            d=w.inspect_agent(kids[0].id)
            assert d["lineage"][:2]==[kids[0].id,p.id]
            assert d["agent"]["genome"]["reproduction_threshold"]>0;return
    raise AssertionError("expected child")

def test_long_run_evolves_beyond_founders():
    w=World(60,42);w.run(5000)
    assert w.births>0
    assert w.max_generation>=1
    assert any(a.parent is not None for a in w.population)
    assert w.history[-1]["max_generation"]==w.max_generation
