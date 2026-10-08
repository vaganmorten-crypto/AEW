from aew.simulation import World

def test_offspring_genome_is_independent_without_mutation():
    w=World(2,11,mutation=False,deadline=None)
    p=w.population[0]
    p.cash=10000; p.resource=100
    p.genome.reproduction_threshold=60
    p.genome.reproduction_probability=1
    w.step()
    children=[a for a in w.population if a.parent==p.id]
    assert children
    child=children[0]
    assert child.genome == p.genome
    assert child.genome is not p.genome
    assert child.born == 1
    p.genome.risk=.99
    assert child.genome.risk != .99

def test_stress_600_agents_10000_ticks():
    w=World(agents=600,seed=3)
    w.run(10000)
    assert w.tick==10000
    assert len(w.history)==10001
    assert all(a.cash==a.cash and a.resource==a.resource for a in w.population)
    assert sum(a.alive for a in w.population)==len(w.living)
