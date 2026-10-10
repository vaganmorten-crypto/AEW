from aew.simulation import World
from aew.diagnostics import diagnose


def test_diagnostics_is_read_only_and_deterministic():
    a, b = World(20, 7), World(20, 7)
    before = a.snapshot()
    assert diagnose(a) == diagnose(a)
    assert a.snapshot() == before
    a.run(10)
    b.run(10)
    assert a.snapshot() == b.snapshot()
    assert diagnose(a) == diagnose(b)


def test_diagnostics_population_and_eligibility():
    w = World(4, 3)
    d = diagnose(w)
    assert d["living"] == 4
    assert d["total_agents_created"] == 4
    assert d["births"] == 0
    assert d["deaths"] == 0
    assert d["eligible_both"] <= d["eligible_cash"]
    assert d["eligible_both"] <= d["eligible_resources"]
    assert sum(d["generation_distribution"].values()) == 4


def test_diagnostics_survives_extinction():
    w = World(2, 1)
    for agent in w.population:
        agent.alive = False
    d = diagnose(w)
    assert d["living"] == 0
    assert d["deaths"] == 2
    assert d["mean_cash_living"] == 0
