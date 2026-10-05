from aew.model import World

def test_deterministic():
    a=World(seed=7); a.initialize(10); a.run(25)
    b=World(seed=7); b.initialize(10); b.run(25)
    assert a.snapshot()==b.snapshot()

def test_closed_world_runs():
    w=World(seed=1); w.initialize(20); w.run(120); s=w.snapshot()
    assert s["tick"]==120 and s["total_agents_ever"]>=20 and s["population"]>=0
