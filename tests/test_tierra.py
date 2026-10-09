from aew.tierra import TierraWorld, HARVEST, REPRODUCE, JUMP

def test_birth_and_lineage():
    w = TierraWorld(seed=1, mutation_rate=0)
    w.add((HARVEST, REPRODUCE, JUMP), energy=20)
    w.run(5)
    assert any(e["type"] == "birth" for e in w.events)
    assert all(a.genome == (HARVEST, REPRODUCE, JUMP) for a in w.population.values())

def test_capacity_and_repeatability():
    def run():
        w = TierraWorld(seed=42, capacity=7, mutation_rate=0.4)
        w.add(energy=30)
        values = w.run(40)
        assert max(values) <= 7
        return values, w.events
    assert run() == run()

def test_extinction():
    w = TierraWorld()
    w.add((JUMP,), energy=2)
    w.run(3)
    assert not w.population
