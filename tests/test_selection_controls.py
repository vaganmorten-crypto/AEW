import pytest
from aew.simulation import World


@pytest.mark.parametrize("mode", ["normal", "no_mutation", "no_inheritance"])
def test_selection_modes_deterministic(mode):
    a = World(100, 42, resource_model="abundant", inheritance_mode=mode)
    b = World(100, 42, resource_model="abundant", inheritance_mode=mode)
    a.run(100)
    b.run(100)
    assert a.snapshot() == b.snapshot()


def test_no_mutation_copies_parent_genome():
    w = World(1000, 42, resource_model="abundant", inheritance_mode="no_mutation")
    w.run(100)
    lookup = {a.id: a for a in w.population}
    children = [a for a in w.population if a.parent is not None]
    assert children
    assert all(a.genome == lookup[a.parent].genome for a in children)


def test_invalid_inheritance_mode():
    with pytest.raises(ValueError):
        World(10, inheritance_mode="invalid")
