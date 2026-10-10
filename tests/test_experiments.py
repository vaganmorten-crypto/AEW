import csv
import json
import pytest
from aew.experiments import execute, run_suite


def test_experiment_is_reproducible_ignoring_wall_clock():
    a = execute("A", 2, 12, 5)
    b = execute("A", 2, 12, 5)
    a.pop("elapsed_seconds")
    b.pop("elapsed_seconds")
    assert a == b


def test_small_matrix_and_resume(tmp_path):
    rows = run_suite(tmp_path, agents=12, ticks=5, seeds=2)
    assert len(rows) == 10
    assert len(list(tmp_path.glob("[A-E]_*.json"))) == 10
    assert len(list(csv.DictReader((tmp_path / "results.csv").open()))) == 10
    assert set(json.loads((tmp_path / "summary.json").read_text())) == set("ABCDE")
    previous = {p.name: p.read_bytes() for p in tmp_path.glob("[A-E]_*.json")}
    assert len(run_suite(tmp_path, agents=12, ticks=5, seeds=2)) == 10
    assert previous == {p.name: p.read_bytes() for p in tmp_path.glob("[A-E]_*.json")}
    with pytest.raises(ValueError):
        run_suite(tmp_path, agents=13, ticks=5, seeds=2)


def test_no_hardcoded_200_agent_cap():
    from aew.simulation import World
    world = World(250, seed=4)
    assert len(world.living) == 250
    world.step()
    assert len(world.population) >= 250


@pytest.mark.parametrize("agents,ticks", [(10000, 100), (10000, 1000), (10000, 10000), (50000, 100)])
def test_load_profiles_are_opt_in(agents, ticks):
    import os
    if os.environ.get("AEW_RUN_LOAD") != "1":
        pytest.skip("Run load profiles explicitly with AEW_RUN_LOAD=1")
    result = execute("A", 1, agents, ticks)
    assert result["initial_agents"] == agents
    assert result["ticks"] == ticks
    assert result["final_population"] >= 0
