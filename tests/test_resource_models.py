import pytest
from aew.simulation import World
from aew.diagnostics import diagnose


def test_baseline_unchanged():
    a = World(20, 42)
    b = World(20, 42, resource_model="baseline")
    a.run(20)
    b.run(20)
    assert a.snapshot() == b.snapshot()


@pytest.mark.parametrize("model", ["baseline", "scaled", "abundant"])
def test_resource_models_deterministic(model):
    a = World(20, 3, resource_model=model)
    b = World(20, 3, resource_model=model)
    a.run(20)
    b.run(20)
    assert a.snapshot() == b.snapshot()
    d = diagnose(a)
    assert d["births"] == a.next_id - 20
    assert d["deaths"] == sum(not x.alive for x in a.population)


def test_invalid_model():
    with pytest.raises(ValueError):
        World(20, 3, resource_model="unknown")
