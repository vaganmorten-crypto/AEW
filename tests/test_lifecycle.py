from aew.simulation import World, Agent, Genome

def test_deadline_and_elite():
    w=World(agents=12,seed=1,deadline=2,elite_slots=2)
    for a in w.population:
        a.cash=10000
        a.resource=100
        a.genome.reproduction_probability=0
        a.genome.resource_consumption=.25
    w.run(2)
    assert len(w.living)==2
    assert sum(e["type"]=="deadline_death" for e in w.events)==10

def test_no_deadline_control():
    w=World(agents=12,seed=1,deadline=None,elite_slots=0)
    for a in w.population:
        a.cash=10000
        a.resource=100
        a.genome.reproduction_probability=0
    w.run(2)
    assert len(w.living)==12

def test_600_founders_no_cap():
    w=World(agents=600,seed=3)
    assert len(w.living)==600

def test_invalid_parameters():
    import pytest
    with pytest.raises(ValueError): World(deadline=0)
    with pytest.raises(ValueError): World(elite_slots=-1)
