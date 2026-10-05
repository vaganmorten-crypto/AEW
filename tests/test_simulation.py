from aew.simulation import World

def test_seed_is_deterministic():
    a=World(20,7); b=World(20,7); a.run(25); b.run(25)
    assert a.snapshot()==b.snapshot()

def test_tick_snapshot_and_observability():
    w=World(10,1); w.run(5); s=w.snapshot()
    assert s["tick"]==5 and s["version"]=="0.3.0" and len(s["history"])==6
    assert "events" in s and all("tick" in e and "type" in e for e in s["events"])

def test_invalid_population():
    try: World(1,1)
    except ValueError: return
    assert False
