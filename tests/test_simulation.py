from random import Random
from aew.simulation import Genome, World

def make_ready(a, partners=1, offspring=1):
    a.cash=1000.; a.resource=200.
    a.genome.reproduction_threshold=55.
    a.genome.reproduction_probability=1.
    a.genome.offspring_investment=.08
    a.genome.partner_count=partners
    a.genome.offspring_count=offspring
    a.genome.partner_selectivity=0.

def run_until_birth(w, limit=20):
    before=w.births
    for _ in range(limit):
        w.step()
        if w.births>before:return
    raise AssertionError("expected birth")

def test_seed_is_deterministic():
    a=World(20,7);b=World(20,7);a.run(100);b.run(100)
    assert a.snapshot()==b.snapshot()

def test_reproduction_genes_mutate_within_bounds():
    g=Genome(.5,.5,130,.05,.2,.8,.25,3,2,.5,.5)
    seen=set()
    for seed in range(100):
        c=g.mutate(Random(seed))
        assert 1<=c.partner_count<=6 and 1<=c.offspring_count<=5
        assert 0<=c.partner_selectivity<=1 and .05<=c.gene_mix_bias<=.95
        seen.add((c.partner_count,c.offspring_count))
    assert len(seen)>1

def test_clone_can_make_multiple_offspring_and_pays_cost():
    w=World(2,11,max_population=20);p=w.population[0];make_ready(p,1,2)
    cash0,res0=p.cash,p.resource
    run_until_birth(w)
    kids=[a for a in w.population if a.parents==[p.id]]
    assert len(kids)>=2
    assert all(a.generation==1 and a.genome!=p.genome for a in kids[:2])
    assert p.cash<cash0 and p.resource<res0

def test_two_parent_reproduction_records_both_parents():
    w=World(2,13,max_population=10)
    for a in w.population:make_ready(a,2,1)
    run_until_birth(w)
    child=next(a for a in w.population if a.parents and len(a.parents)==2)
    assert set(child.parents)=={0,1}
    d=w.inspect_agent(child.id)
    assert set(d["parent_ids"])=={0,1}
    assert d["birth_event"]["mode"]=="2-parent"

def test_three_parent_reproduction_splices_genes_and_costs_all():
    w=World(3,17,max_population=10)
    for a in w.population:make_ready(a,3,1)
    before={a.id:(a.cash,a.resource) for a in w.population}
    run_until_birth(w)
    child=next(a for a in w.population if a.parents and len(a.parents)==3)
    assert set(child.parents)=={0,1,2}
    assert child.generation==1
    for pid in child.parents:
        p=next(a for a in w.population if a.id==pid)
        assert p.cash<before[pid][0] and p.resource<before[pid][1]
    ev=w.inspect_agent(child.id)["birth_event"]
    assert ev["mode"]=="3-parent" and ev["genes"]

def test_inspector_traverses_multi_parent_ancestry():
    w=World(3,23,max_population=20)
    for a in w.population:make_ready(a,2,1)
    run_until_birth(w)
    child=next(a for a in w.population if a.parents)
    make_ready(child,2,1)
    for a in w.population:a.genome.reproduction_probability=0.
    child.genome.reproduction_probability=1.
    run_until_birth(w)
    grand=next(a for a in reversed(w.population) if a.id!=child.id and a.parents and child.id in a.parents)
    d=w.inspect_agent(grand.id)
    assert child.id in d["parent_ids"]
    assert any(pid in d["ancestor_ids"] for pid in child.parents)

def test_long_run_evolves_beyond_founders():
    w=World(60,42);w.run(5000)
    assert w.births>0 and w.max_generation>=1
    assert any(a.parents for a in w.population)
    assert w.history[-1]["max_generation"]==w.max_generation
