from aew.simulation import World

def test_seed_is_deterministic():
    a=World(20,7); b=World(20,7); a.run(25); b.run(25)
    assert a.snapshot()==b.snapshot()

def test_tick_snapshot_and_observability():
    w=World(10,1); w.run(5); s=w.snapshot()
    assert s["tick"]==5 and s["version"]=="0.5.0" and len(s["history"])==6
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

def test_all_reproduction_modes_and_seed_replay():
    for mode in "ABCDE":
        a = World(12, 7, mode=mode)
        b = World(12, 7, mode=mode)
        a.run(20)
        b.run(20)
        assert a.snapshot() == b.snapshot()
        assert a.snapshot()["reproduction_mode"] == mode

def test_duplication_and_repair():
    from random import Random
    from aew.simulation import Genome
    g = Genome.founder(Random(3))
    g.duplication_rate = 1
    g.repair_rate = 1
    child = g.reproduce(Random(9), "E")
    assert child.backup_risk == g.risk
    assert child.backup_trade_rate == g.trade_rate
    assert child.risk == g.risk
    assert child.trade_rate == g.trade_rate

def test_recombination_multiple_parents():
    from random import Random
    from aew.simulation import Genome
    g = Genome.founder(Random(1))
    h = Genome.founder(Random(2))
    g.recombination_rate = 1
    child = g.reproduce(Random(4), "D", (h,))
    assert isinstance(child, Genome)

def test_no_hard_population_cap():
    w = World(600, 1)
    assert len(w.living) == 600
    w.step()
    assert w.tick == 1

def test_invalid_mode():
    import pytest
    with pytest.raises(ValueError):
        World(2, 1, mode="X")

def test_repair_without_backup():
    from random import Random
    from aew.simulation import Genome
    g = Genome.founder(Random(3))
    g.repair_rate = 1.0
    g.backup_risk = None
    g.backup_trade_rate = None
    child = g.reproduce(Random(9), "C")
    assert child.risk == g.risk
    assert child.trade_rate == g.trade_rate

def test_copy_mode_does_not_recombine():
    from random import Random
    from aew.simulation import Genome
    g = Genome.founder(Random(1))
    h = Genome.founder(Random(2))
    g.recombination_rate = 1.0
    assert g.reproduce(Random(4), "A", (h,)) == g.reproduce(Random(4), "A")

def test_parent_contributors_are_recorded():
    w = World(3, 1, mode="D")
    for a in w.population:
        a.cash = 1000
        a.resource = 100
        a.genome.reproduction_threshold = 60
        a.genome.reproduction_probability = .35
    for _ in range(50):
        w.step()
        children = [a for a in w.population if a.generation]
        if children:
            assert len(children[0].parents) >= 2
            assert children[0].parent == children[0].parents[0]
            assert any(e["type"] == "birth" and "parents" in e for e in w.events)
            return
    assert False, "expected a birth"
