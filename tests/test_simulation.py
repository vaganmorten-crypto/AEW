from aew.simulation import World

def test_seed_is_deterministic():
    a=World(20,7); b=World(20,7); a.run(25); b.run(25)
    assert a.snapshot()==b.snapshot()

def test_tick_snapshot_and_observability():
    w=World(10,1); w.run(5); s=w.snapshot()
    assert s["tick"]==5 and s["version"]=="0.3.0" and len(s["history"])==6
    assert "events" in s and all("tick" in e and "type" in e for e in s["events"])

def test_every_agent_has_genetic_reproduction_traits():
    w=World(12,3)
    for a in w.population:
        g=a.genome
        assert g.reproduction_threshold > 0
        assert 0 < g.reproduction_probability <= .35
        assert 0 < g.offspring_investment < 1
        assert g.resource_consumption > 0
        assert 0 < g.trade_rate < 1

def test_birth_inherits_mutated_genome():
    w=World(2,11); p=w.population[0]
    p.cash=500; p.resource=100
    p.genome.reproduction_threshold=60
    p.genome.reproduction_probability=.35
    for _ in range(100):
        w.step()
        children=[a for a in w.population if a.parent==p.id]
        if children:
            c=children[0]
            assert c.generation==1
            assert c.genome != p.genome
            return
    assert False, "expected a genetically controlled birth"

def test_invalid_population():
    try: World(1,1)
    except ValueError: return
    assert False
