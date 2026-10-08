from aew.simulation import World

def test_deadline_is_age_based_for_offspring():
    w = World(agents=2, seed=9, deadline=3, elite_slots=0)
    for a in w.population:
        a.cash = 10000
        a.resource = 100
        a.genome.reproduction_probability = 0
    w.run(2)
    assert len(w.living) == 2
    w.run(1)
    assert len(w.living) == 0

def test_elite_rank_changes_with_wealth():
    w = World(agents=3, seed=5, deadline=1, elite_slots=1)
    for a in w.population:
        a.cash = 10000
        a.resource = 100
        a.genome.reproduction_probability = 0
    w.population[2].cash = 100000
    w.step()
    assert [a.id for a in w.living] == [2]

def test_mutation_disabled_preserves_genome():
    w = World(agents=2, seed=11, mutation=False)
    p = w.population[0]
    p.cash = 10000
    p.resource = 100
    p.genome.reproduction_threshold = 60
    p.genome.reproduction_probability = 1
    w.step()
    children = [a for a in w.population if a.parent == p.id]
    assert children
    assert children[0].genome == p.genome
